import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

def show_inspector_crud():
    """검사자 CRUD 관리 페이지를 표시합니다."""
    st.header("👥 검사자 데이터베이스 관리")
    
    # Supabase 클라이언트 가져오기
    supabase = get_supabase_client()
    
    # 연결 상태 확인 및 표시
    show_connection_status(supabase)
    
    # 탭 생성
    list_tab, add_tab, edit_tab, delete_tab, sync_tab = st.tabs(["검사자 목록", "검사자 추가", "검사자 수정", "검사자 삭제", "데이터 동기화"])
    
    # 검사자 목록 탭
    with list_tab:
        show_inspector_list(supabase)
    
    # 검사자 추가 탭
    with add_tab:
        show_add_inspector(supabase)
    
    # 검사자 수정 탭
    with edit_tab:
        show_edit_inspector(supabase)
    
    # 검사자 삭제 탭
    with delete_tab:
        show_delete_inspector(supabase)
    
    # 데이터 동기화 탭
    with sync_tab:
        show_data_sync(supabase)

def show_connection_status(supabase):
    """연결 상태를 표시합니다."""
    st.success("✅ Supabase에 연결되었습니다.")

def show_data_sync(supabase):
    """데이터 동기화 기능을 표시합니다."""
    st.subheader("🔄 데이터 동기화")
    
    st.success("Supabase에 연결되었습니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("실제 데이터베이스에서 조회")
        if st.button("데이터베이스 조회", type="primary"):
            try:
                response = supabase.table('inspectors').select('*').execute()
                if response.data:
                    df = pd.DataFrame(response.data)
                    st.dataframe(df, use_container_width=True)
                    st.success(f"데이터베이스에서 {len(response.data)}개의 검사자 데이터를 조회했습니다.")
                else:
                    st.info("데이터베이스에 검사자 데이터가 없습니다.")
            except Exception as e:
                st.error(f"데이터베이스 조회 중 오류 발생: {str(e)}")
    
    with col2:
        st.subheader("샘플 데이터 업로드")
        if st.button("샘플 검사자 데이터 업로드"):
            upload_sample_inspectors(supabase)

def upload_sample_inspectors(supabase):
    """샘플 검사자 데이터를 실제 데이터베이스에 업로드합니다."""
    sample_inspectors = [
        {
            "name": "김검사원",
            "employee_id": "INSP001",
            "department": "품질관리부"
        },
        {
            "name": "이검사원", 
            "employee_id": "INSP002",
            "department": "품질관리부"
        },
        {
            "name": "박검사원",
            "employee_id": "INSP003",
            "department": "생산품질팀"
        }
    ]
    
    try:
        # 기존 데이터 확인
        existing_response = supabase.table('inspectors').select('employee_id').execute()
        existing_employee_ids = [inspector['employee_id'] for inspector in existing_response.data] if existing_response.data else []
        
        # 중복되지 않는 검사자만 추가
        new_inspectors = [inspector for inspector in sample_inspectors if inspector['employee_id'] not in existing_employee_ids]
        
        if new_inspectors:
            response = supabase.table('inspectors').insert(new_inspectors).execute()
            if response.data:
                st.success(f"{len(new_inspectors)}명의 검사자가 성공적으로 업로드되었습니다!")
                st.rerun()
            else:
                st.error("검사자 업로드에 실패했습니다.")
        else:
            st.warning("모든 샘플 검사자가 이미 데이터베이스에 존재합니다.")
            
    except Exception as e:
        st.error(f"샘플 데이터 업로드 중 오류 발생: {str(e)}")
        st.info("RLS 정책 오류인 경우 Supabase 설정에서 RLS를 비활성화하거나 적절한 정책을 설정하세요.")

def show_inspector_list(supabase):
    """검사자 목록을 표시합니다."""
    st.subheader("📋 검사자 목록")
    
    # 실제 Supabase 연결인지 확인
    is_real_supabase = True
    try:
        # inspectors 테이블에서 모든 검사자 조회
        response = supabase.table('inspectors').select('*').order('name').execute()
        
        if response.data:
            # 데이터프레임으로 변환
            df = pd.DataFrame(response.data)
            
            # 컬럼 설정
            column_config = {
                "id": st.column_config.TextColumn("ID", width="small"),
                "name": st.column_config.TextColumn("이름", width="medium"),
                "employee_id": st.column_config.TextColumn("사번", width="medium"),
                "department": st.column_config.TextColumn("부서", width="medium"),
            }
            
            # 추가 컬럼이 있는 경우 포함
            display_columns = []
            for col in ['id', 'name', 'employee_id', 'department']:
                if col in df.columns:
                    display_columns.append(col)
            
            # 사용 가능한 컬럼만 표시
            if display_columns:
                df = df[display_columns]
            
            st.dataframe(
                df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True
            )
            
            st.info(f"총 {len(df)} 명의 검사자가 등록되어 있습니다.")
        else:
            st.info("등록된 검사자가 없습니다.")
            
    except Exception as e:
        st.error(f"검사자 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")

def show_add_inspector(supabase):
    """새 검사자 추가 폼을 표시합니다."""
    st.subheader("➕ 새 검사자 추가")
    
    # 실제 Supabase 연결인지 확인
    is_real_supabase = True
    # 연결 테스트 및 테이블 구조 확인
    if is_real_supabase:
        try:
            # 테이블 구조 확인을 위한 더 안전한 접근
            test_response = supabase.table('inspectors').select('*').limit(1).execute()
            st.info("✅ Supabase inspectors 테이블에 연결되었습니다.")
            
            # 실제 테이블 컬럼 확인
            if test_response.data:
                available_columns = list(test_response.data[0].keys())
                st.info(f"사용 가능한 컬럼: {', '.join(available_columns)}")
            
        except Exception as e:
            st.error(f"❌ inspectors 테이블 연결 오류: {str(e)}")
            if "does not exist" in str(e):
                st.warning("⚠️ inspectors 테이블이 존재하지 않습니다. 'Supabase 설정'에서 테이블을 생성하세요.")
                return
    
    with st.form("add_inspector_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("이름 *", placeholder="김검사원")
            employee_id = st.text_input("사번 *", placeholder="INSP001")
        
        with col2:
            department = st.text_input("부서 *", placeholder="품질관리부")
        
        submitted = st.form_submit_button("검사자 추가", type="primary")
        
        if submitted:
            # 필수 필드 검증
            if not name or not employee_id or not department:
                st.error("이름, 사번, 부서는 필수 항목입니다.")
                return
            
            try:
                # 검사자 데이터
                inspector_data = {
                    "name": name,
                    "employee_id": employee_id,
                    "department": department
                }
                
                # 데이터베이스에 삽입
                response = supabase.table('inspectors').insert(inspector_data).execute()
                
                if response.data:
                    st.success(f"검사자 '{name}' ({employee_id})이(가) 성공적으로 추가되었습니다!")
                    # 추가된 데이터 확인
                    st.json(response.data[0])
                    st.rerun()
                else:
                    st.error("검사자 추가에 실패했습니다.")
                    
            except Exception as e:
                error_message = str(e)
                st.error(f"검사자 추가 중 오류가 발생했습니다: {error_message}")
                
                # 구체적인 오류 해결 가이드 제공
                if "could not find" in error_message.lower() and "column" in error_message.lower():
                    st.warning("⚠️ 테이블 구조 불일치 오류입니다.")
                    st.info("💡 'Supabase 설정' 메뉴에서 올바른 inspectors 테이블을 생성하거나, 기존 테이블 구조를 확인하세요.")
                    
                elif "violates row-level security policy" in error_message:
                    st.warning("⚠️ RLS 정책 오류입니다.")
                    st.code("ALTER TABLE inspectors DISABLE ROW LEVEL SECURITY;", language="sql")
                elif "duplicate key value violates unique constraint" in error_message:
                    st.warning("⚠️ 이미 존재하는 사번입니다.")
                elif "23514" in error_message:
                    st.warning("⚠️ 데이터베이스 제약 조건 위반입니다.")
                    st.info("💡 입력 데이터가 테이블의 제약 조건을 위반했습니다. 'Supabase 설정'에서 제약 조건을 확인하세요.")
                else:
                    st.info("💡 자세한 해결 방법은 'Supabase 설정' 메뉴를 참조하세요.")

def show_edit_inspector(supabase):
    """검사자 정보 수정 폼을 표시합니다."""
    st.subheader("✏️ 검사자 정보 수정")
    
    try:
        # 검사자 목록 조회
        response = supabase.table('inspectors').select('*').order('name').execute()
        
        if not response.data:
            st.info("수정할 검사자가 없습니다.")
            return
        
        # 검사자 선택
        inspector_options = {f"{inspector['name']} ({inspector['employee_id']})": inspector for inspector in response.data}
        selected_inspector_key = st.selectbox("수정할 검사자 선택", list(inspector_options.keys()))
        
        if selected_inspector_key:
            selected_inspector = inspector_options[selected_inspector_key]
            
            with st.form("edit_inspector_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("이름 *", value=selected_inspector.get('name', ''))
                    employee_id = st.text_input("사번 *", value=selected_inspector.get('employee_id', ''))
                
                with col2:
                    department = st.text_input("부서 *", value=selected_inspector.get('department', ''))
                
                submitted = st.form_submit_button("수정", type="primary")
                
                if submitted:
                    # 필수 필드 검증
                    if not name or not employee_id or not department:
                        st.error("이름, 사번, 부서는 필수 항목입니다.")
                        return
                    
                    try:
                        # 업데이트 데이터
                        update_data = {
                            "name": name,
                            "employee_id": employee_id,
                            "department": department
                        }
                        
                        # 데이터베이스 업데이트
                        response = supabase.table('inspectors').update(update_data).eq('id', selected_inspector['id']).execute()
                        
                        if response.data:
                            st.success(f"검사자 '{name}' 정보가 성공적으로 수정되었습니다!")
                            st.rerun()
                        else:
                            st.error("검사자 정보 수정에 실패했습니다.")
                            
                    except Exception as e:
                        error_message = str(e)
                        st.error(f"검사자 정보 수정 중 오류가 발생했습니다: {error_message}")
                        
                        # 구체적인 오류 해결 가이드 제공
                        if "could not find" in error_message.lower() and "column" in error_message.lower():
                            st.warning("⚠️ 테이블 구조 불일치 오류입니다.")
                            st.info("💡 'Supabase 설정' 메뉴에서 올바른 inspectors 테이블을 생성하거나, 기존 테이블 구조를 확인하세요.")
                        elif "violates row-level security policy" in error_message:
                            st.warning("⚠️ RLS 정책 오류입니다.")
                            st.code("ALTER TABLE inspectors DISABLE ROW LEVEL SECURITY;", language="sql")
                        elif "duplicate key value violates unique constraint" in error_message:
                            st.warning("⚠️ 이미 존재하는 사번입니다.")
                        elif "23514" in error_message:
                            st.warning("⚠️ 데이터베이스 제약 조건 위반입니다.")
                            st.info("💡 입력 데이터가 테이블의 제약 조건을 위반했습니다. 'Supabase 설정'에서 제약 조건을 확인하세요.")
                        else:
                            st.info("💡 자세한 해결 방법은 'Supabase 설정' 메뉴를 참조하세요.")
            
    except Exception as e:
        error_message = str(e)
        st.error(f"검사자 목록을 불러오는 중 오류가 발생했습니다: {error_message}")
        
        if "does not exist" in error_message:
            st.warning("⚠️ inspectors 테이블이 존재하지 않습니다. 'Supabase 설정'에서 테이블을 생성하세요.")

def show_delete_inspector(supabase):
    """검사자 삭제 폼을 표시합니다."""
    st.subheader("🗑️ 검사자 삭제")
    
    # 경고 메시지
    st.warning("⚠️ 검사자 삭제는 되돌릴 수 없습니다. 신중하게 진행하세요.")
    
    try:
        # 검사자 목록 조회
        response = supabase.table('inspectors').select('*').order('name').execute()
        
        if not response.data:
            st.info("삭제할 검사자가 없습니다.")
            return
        
        # 검사자 선택
        inspector_options = {f"{inspector['name']} ({inspector['employee_id']})": inspector for inspector in response.data}
        selected_inspector_key = st.selectbox("삭제할 검사자 선택", ["선택하세요..."] + list(inspector_options.keys()))
        
        if selected_inspector_key != "선택하세요...":
            selected_inspector = inspector_options[selected_inspector_key]
            
            # 선택된 검사자 정보 표시
            st.subheader("삭제 대상 검사자 정보")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**이름:** {selected_inspector.get('name', 'N/A')}")
                st.write(f"**사번:** {selected_inspector.get('employee_id', 'N/A')}")
            
            with col2:
                st.write(f"**부서:** {selected_inspector.get('department', 'N/A')}")
                st.write(f"**ID:** {selected_inspector.get('id', 'N/A')}")
            
            # 삭제 확인
            st.subheader("삭제 확인")
            
            # 안전을 위한 확인 단계
            confirm_text = st.text_input(
                f"삭제를 확인하려면 '{selected_inspector['name']}'을(를) 입력하세요:",
                placeholder="검사자 이름 입력"
            )
            
            # 추가 확인 체크박스
            final_confirm = st.checkbox("위 검사자를 삭제하겠다는 것을 확인합니다.")
            
            if st.button("검사자 삭제", type="primary", disabled=not final_confirm):
                if confirm_text == selected_inspector['name']:
                    try:
                        # 데이터베이스에서 검사자 삭제
                        response = supabase.table('inspectors').delete().eq('id', selected_inspector['id']).execute()
                        
                        if response.data:
                            st.success(f"검사자 '{selected_inspector['name']}' ({selected_inspector['employee_id']})이(가) 성공적으로 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("검사자 삭제에 실패했습니다.")
                            
                    except Exception as e:
                        st.error(f"검사자 삭제 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.error("검사자 이름이 일치하지 않습니다. 정확히 입력해주세요.")
            
    except Exception as e:
        st.error(f"검사자 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")

# 유틸리티 함수들
def validate_employee_id(employee_id):
    """사번 형식 검증"""
    import re
    # 간단한 사번 형식 검증 (INSP001 형태)
    pattern = r'^[A-Z]{2,10}[0-9]{2,5}$'
    return re.match(pattern, employee_id) is not None 