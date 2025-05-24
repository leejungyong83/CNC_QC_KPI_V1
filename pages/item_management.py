import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

def show_production_model_management():
    """생산모델 관리 화면 표시 (Supabase 연동)"""
    st.title("생산모델 관리")
    
    # Supabase 클라이언트 가져오기
    supabase = get_supabase_client()
    
    # 연결 상태 확인
    show_connection_status(supabase)
    
    # 탭 생성
    tabs = st.tabs(["생산모델 목록", "신규 모델 등록", "모델 수정", "모델 삭제"])
    
    with tabs[0]:
        show_model_list(supabase)
    
    with tabs[1]:
        show_model_form(supabase)
    
    with tabs[2]:
        show_model_edit(supabase)
    
    with tabs[3]:
        show_model_delete(supabase)

def show_connection_status(supabase):
    """연결 상태를 표시합니다."""
    if hasattr(supabase, '_init_session_state'):
        st.warning("⚠️ 현재 오프라인 모드로 작동 중입니다. Supabase 연결 후 실제 데이터베이스와 동기화됩니다.")
    else:
        st.success("✅ Supabase에 연결되었습니다.")

def show_model_list(supabase):
    """생산모델 목록 페이지 (Supabase 연동)"""
    st.header("📋 생산모델 목록")
    
    # 새로고침 버튼
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()
    
    with col2:
        # 검색어 필드
        search = st.text_input("🔍 검색", placeholder="모델명 또는 모델번호 검색", key="search_input")
    
    try:
        # Supabase에서 데이터 조회
        if hasattr(supabase, '_init_session_state'):
            # 오프라인 모드 - 업데이트된 더미 데이터 직접 사용
            models_data = get_dummy_models_data()
            df = pd.DataFrame(models_data)
        else:
            # 실제 Supabase 연결
            response = supabase.table('production_models').select('*').order('created_at', desc=True).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
            else:
                df = pd.DataFrame()
        
        # 검색 필터링
        if search and not df.empty:
            if 'model_name' in df.columns and 'model_no' in df.columns:
                mask = (df['model_name'].str.contains(search, case=False, na=False) | 
                       df['model_no'].str.contains(search, case=False, na=False))
                df = df[mask]
        
        # 데이터 표시
        if not df.empty:
            # 컬럼명 한글로 변경하여 표시
            display_df = df.rename(columns={
                'id': 'ID',
                'model_no': '모델번호',
                'model_name': '모델명',
                'process': '공정',
                'created_at': '생성일시'
            })
            
            st.dataframe(
                display_df,
                column_config={
                    "ID": st.column_config.TextColumn("ID", width="small"),
                    "모델번호": st.column_config.TextColumn("모델번호", width="medium"),
                    "모델명": st.column_config.TextColumn("모델명", width="medium"),
                    "공정": st.column_config.TextColumn("공정", width="medium"),
                    "생성일시": st.column_config.DatetimeColumn("생성일시", width="medium"),
                },
                use_container_width=True,
                hide_index=True
            )
            
            if hasattr(supabase, '_init_session_state'):
                st.info(f"📊 오프라인 모드: {len(df)}개의 샘플 데이터")
            else:
                st.info(f"📊 총 {len(df)}개의 생산모델이 등록되어 있습니다.")
        else:
            st.info("등록된 생산모델이 없습니다.")
            
    except Exception as e:
        st.error(f"❌ 데이터 조회 중 오류 발생: {str(e)}")
        if "does not exist" in str(e):
            st.warning("⚠️ production_models 테이블이 존재하지 않습니다.")
            if st.button("🏗️ 테이블 생성하기"):
                create_production_models_table(supabase)

def show_model_form(supabase):
    """생산모델 등록 페이지 (Supabase 연동)"""
    st.header("➕ 신규 모델 등록")
    
    with st.form(key="model_form"):
        st.markdown("### 📝 모델 정보 입력")
        
        col1, col2 = st.columns(2)
        
        with col1:
            model_no = st.text_input("모델번호 *", placeholder="예: MODEL-001", help="고유한 모델 식별번호")
            model_name = st.text_input("모델명 *", placeholder="예: PA1", help="모델의 이름")
        
        with col2:
            process = st.selectbox("공정 *", 
                                 options=["", "C1", "C2", "CNC1_PQC", "CNC2_PQC", "OQC", "IQC", "FQC"],
                                 help="해당 모델의 공정 선택")
            notes = st.text_area("비고", placeholder="추가 설명 (선택사항)")
        
        # 제출 버튼
        submit = st.form_submit_button("✅ 모델 등록", type="primary", use_container_width=True)
        
        if submit:
            if not model_no or not model_name or not process:
                st.error("❌ 모델번호, 모델명, 공정은 필수 입력 항목입니다.")
            else:
                try:
                    if hasattr(supabase, '_init_session_state'):
                        # 오프라인 모드
                        st.warning("⚠️ 오프라인 모드입니다. Supabase 연결 후 실제 데이터베이스에 저장됩니다.")
                        st.success(f"✅ 모델 '{model_name}' 등록 준비 완료 (오프라인)")
                    else:
                        # 실제 Supabase에 저장
                        model_data = {
                            "model_no": model_no,
                            "model_name": model_name,
                            "process": process,
                            "notes": notes if notes else None,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        response = supabase.table('production_models').insert(model_data).execute()
                        
                        if response.data:
                            st.success(f"✅ 생산모델 '{model_name}' ({model_no})이(가) 성공적으로 등록되었습니다!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ 모델 등록에 실패했습니다.")
                            
                except Exception as e:
                    error_message = str(e)
                    st.error(f"❌ 등록 중 오류 발생: {error_message}")
                    
                    if "duplicate key value" in error_message.lower():
                        st.warning("⚠️ 이미 존재하는 모델번호입니다. 다른 번호를 사용해주세요.")
                    elif "violates row-level security policy" in error_message:
                        st.warning("⚠️ RLS 정책 오류입니다. Supabase 설정을 확인하세요.")

def show_model_edit(supabase):
    """생산모델 수정 페이지"""
    st.header("✏️ 모델 수정")
    
    try:
        # 수정할 모델 선택
        if hasattr(supabase, '_init_session_state'):
            # 오프라인 모드
            st.warning("⚠️ 오프라인 모드에서는 수정 기능을 사용할 수 없습니다.")
            return
        
        # 모델 목록 조회
        response = supabase.table('production_models').select('*').order('created_at', desc=True).execute()
        
        if not response.data:
            st.info("수정할 모델이 없습니다.")
            return
        
        # 모델 선택 드롭다운
        model_options = {f"{model['model_name']} ({model['model_no']})": model for model in response.data}
        selected_model_key = st.selectbox("수정할 모델 선택", ["선택하세요..."] + list(model_options.keys()))
        
        if selected_model_key != "선택하세요...":
            selected_model = model_options[selected_model_key]
            
            with st.form(key="edit_model_form"):
                st.markdown(f"### 📝 모델 정보 수정: {selected_model['model_name']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    model_no = st.text_input("모델번호 *", value=selected_model['model_no'], disabled=True, help="모델번호는 변경할 수 없습니다")
                    model_name = st.text_input("모델명 *", value=selected_model['model_name'])
                
                with col2:
                    current_process = selected_model.get('process', '')
                    process_options = ["C1", "C2", "CNC1_PQC", "CNC2_PQC", "OQC", "IQC", "FQC"]
                    process_index = process_options.index(current_process) if current_process in process_options else 0
                    process = st.selectbox("공정 *", options=process_options, index=process_index)
                    notes = st.text_area("비고", value=selected_model.get('notes', '') or '')
                
                # 수정 버튼
                update_button = st.form_submit_button("✅ 수정 완료", type="primary", use_container_width=True)
                
                if update_button:
                    if not model_name or not process:
                        st.error("❌ 모델명과 공정은 필수 항목입니다.")
                    else:
                        try:
                            update_data = {
                                "model_name": model_name,
                                "process": process,
                                "notes": notes if notes else None,
                                "updated_at": datetime.now().isoformat()
                            }
                            
                            response = supabase.table('production_models').update(update_data).eq('id', selected_model['id']).execute()
                            
                            if response.data:
                                st.success(f"✅ 모델 '{model_name}' 정보가 성공적으로 수정되었습니다!")
                                st.rerun()
                            else:
                                st.error("❌ 수정에 실패했습니다.")
                                
                        except Exception as e:
                            st.error(f"❌ 수정 중 오류 발생: {str(e)}")
                            
    except Exception as e:
        st.error(f"❌ 데이터 조회 중 오류 발생: {str(e)}")

def show_model_delete(supabase):
    """생산모델 삭제 페이지"""
    st.header("🗑️ 모델 삭제")
    
    # 경고 메시지
    st.warning("⚠️ **주의**: 모델 삭제는 되돌릴 수 없습니다. 신중하게 진행하세요.")
    
    try:
        if hasattr(supabase, '_init_session_state'):
            # 오프라인 모드
            st.warning("⚠️ 오프라인 모드에서는 삭제 기능을 사용할 수 없습니다.")
            return
        
        # 모델 목록 조회
        response = supabase.table('production_models').select('*').order('created_at', desc=True).execute()
        
        if not response.data:
            st.info("삭제할 모델이 없습니다.")
            return
        
        # 삭제할 모델 선택
        model_options = {f"{model['model_name']} ({model['model_no']})": model for model in response.data}
        selected_model_key = st.selectbox("삭제할 모델 선택", ["선택하세요..."] + list(model_options.keys()))
        
        if selected_model_key != "선택하세요...":
            selected_model = model_options[selected_model_key]
            
            # 선택된 모델 정보 표시
            st.subheader("🔍 삭제 대상 모델 정보")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**모델번호:** {selected_model['model_no']}")
                st.write(f"**모델명:** {selected_model['model_name']}")
            
            with col2:
                st.write(f"**공정:** {selected_model['process']}")
                st.write(f"**생성일:** {selected_model.get('created_at', 'N/A')}")
            
            if selected_model.get('notes'):
                st.write(f"**비고:** {selected_model['notes']}")
            
            # 삭제 확인
            st.subheader("❗ 삭제 확인")
            
            # 안전을 위한 확인 단계
            confirm_text = st.text_input(
                f"삭제를 확인하려면 모델명 '{selected_model['model_name']}'을(를) 입력하세요:",
                placeholder="모델명 입력"
            )
            
            # 추가 확인 체크박스
            final_confirm = st.checkbox("위 모델을 삭제하겠다는 것을 확인합니다.")
            
            if st.button("🗑️ 모델 삭제", type="primary", disabled=not final_confirm):
                if confirm_text == selected_model['model_name']:
                    try:
                        # 데이터베이스에서 모델 삭제
                        response = supabase.table('production_models').delete().eq('id', selected_model['id']).execute()
                        
                        if response.data:
                            st.success(f"✅ 모델 '{selected_model['model_name']}' ({selected_model['model_no']})이(가) 성공적으로 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("❌ 삭제에 실패했습니다.")
                            
                    except Exception as e:
                        st.error(f"❌ 삭제 중 오류 발생: {str(e)}")
                else:
                    st.error("❌ 모델명이 일치하지 않습니다. 정확히 입력해주세요.")
                    
    except Exception as e:
        st.error(f"❌ 데이터 조회 중 오류 발생: {str(e)}")

def create_production_models_table(supabase):
    """production_models 테이블 생성"""
    st.info("🏗️ production_models 테이블 생성 SQL:")
    
    create_table_sql = """
    CREATE TABLE production_models (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        model_no TEXT UNIQUE NOT NULL,
        model_name TEXT NOT NULL,
        process TEXT NOT NULL,
        notes TEXT,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    
    -- RLS 비활성화 (개발 환경용)
    ALTER TABLE production_models DISABLE ROW LEVEL SECURITY;
    """
    
    st.code(create_table_sql, language="sql")
    st.warning("⚠️ 위 SQL을 Supabase SQL Editor에서 실행하세요.")

def get_dummy_models_data():
    """오프라인 모드용 더미 데이터 (Supabase 실제 데이터와 동일한 구조)"""
    return [
        {
            "id": "1df2409d-a5b2-46c3-ac9e-9857ea6b24d1",
            "model_no": "AUTO-202505211130839",
            "model_name": "PA1",
            "process": "CNC2_PQC",
            "notes": "오프라인 모드 데이터",
            "created_at": "2025-05-21T06:08:39.297Z",
            "updated_at": "2025-05-21T06:08:39.297Z"
        },
        {
            "id": "d7464e2e-bdd0-49f8-b1cd-35a826fe23b1",
            "model_no": "AUTO-202505211104305",
            "model_name": "PA2",
            "process": "OQC",
            "notes": "오프라인 모드 데이터",
            "created_at": "2025-05-21T03:43:05.326Z",
            "updated_at": "2025-05-21T03:43:05.326Z"
        }
    ]

def get_all_models():
    """모든 생산모델 반환 (Supabase 연동)"""
    supabase = get_supabase_client()
    
    try:
        if hasattr(supabase, '_init_session_state'):
            # 오프라인 모드
            return pd.DataFrame(get_dummy_models_data())
        else:
            # 실제 Supabase 조회
            response = supabase.table('production_models').select('*').order('created_at', desc=True).execute()
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
    except:
        # 오류 시 더미 데이터 반환
        return pd.DataFrame(get_dummy_models_data()) 