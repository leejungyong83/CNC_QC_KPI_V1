import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)

def show_production_model_management():
    """생산모델 관리 화면 표시 (Supabase 연동)"""
    st.title("🏭 생산모델 관리")
    
    # Supabase 클라이언트 가져오기
    supabase = get_supabase_client()
    
    # 연결 상태 확인
    show_connection_status(supabase)
    
    # 탭 생성
    tabs = st.tabs(["📋 생산모델 목록", "➕ 신규 모델 등록", "✏️ 모델 수정", "🗑️ 모델 삭제"])
    
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
            display_df = df.copy()
            
            # 컬럼이 존재하는 경우에만 표시
            available_columns = {}
            if 'id' in df.columns:
                available_columns['id'] = 'ID'
            if 'model_no' in df.columns:
                available_columns['model_no'] = '모델번호'
            if 'model_name' in df.columns:
                available_columns['model_name'] = '모델명'
            if 'process' in df.columns:
                available_columns['process'] = '공정'
            if 'created_at' in df.columns:
                available_columns['created_at'] = '생성일시'
            
            display_df = display_df.rename(columns=available_columns)
            
            # 컬럼 설정
            column_config = {}
            for original, korean in available_columns.items():
                if korean == "ID":
                    column_config[korean] = st.column_config.TextColumn("ID", width="small")
                elif korean in ["모델번호", "모델명", "공정"]:
                    column_config[korean] = st.column_config.TextColumn(korean, width="medium")
                elif korean == "생성일시":
                    column_config[korean] = st.column_config.DatetimeColumn("생성일시", width="medium")
            
            st.dataframe(
                display_df[list(available_columns.values())],
                column_config=column_config,
                use_container_width=True,
                hide_index=True
            )
            
            st.info(f"📊 총 {len(df)}개의 생산모델이 등록되어 있습니다.")
        else:
            st.info("등록된 생산모델이 없습니다.")
            
    except Exception as e:
        st.error(f"❌ 데이터 조회 중 오류 발생: {str(e)}")
        if "does not exist" in str(e):
            st.warning("⚠️ production_models 테이블이 존재하지 않습니다.")

def show_model_form(supabase):
    """신규 모델 등록 폼"""
    st.header("➕ 신규 생산모델 등록")
    
    with st.form("add_model_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            model_no = st.text_input("모델번호 *", placeholder="예: CNC-001")
            model_name = st.text_input("모델명 *", placeholder="예: 기본형 CNC 모델")
        
        with col2:
            process_options = ["C1", "C2", "C2-1", "직접입력"]
            process_selection = st.selectbox("공정 *", process_options)
            
            # 직접입력 선택 시 텍스트 입력 필드 표시
            if process_selection == "직접입력":
                process = st.text_input("공정명 입력", placeholder="공정명을 입력하세요")
            else:
                process = process_selection
                
            notes = st.text_area("비고", placeholder="모델에 대한 추가 정보")
        
        submitted = st.form_submit_button("등록", type="primary")
        
        if submitted:
            if not model_no or not model_name:
                st.error("모델번호와 모델명은 필수 항목입니다.")
            elif process_selection == "직접입력" and not process:
                st.error("직접입력을 선택한 경우 공정명을 입력해주세요.")
            else:
                try:
                    model_data = {
                        "model_no": model_no,
                        "model_name": model_name,
                        "process": process,
                        "notes": notes if notes else None,
                        "created_at": get_database_time().isoformat()  # 베트남 시간대 timestamptz
                    }
                    
                    response = supabase.table('production_models').insert(model_data).execute()
                    
                    if response.data:
                        st.success(f"✅ 모델 '{model_name}' 등록 완료!")
                        st.rerun()
                    else:
                        st.error("모델 등록에 실패했습니다.")
                        
                except Exception as e:
                    st.error(f"모델 등록 중 오류 발생: {str(e)}")

def show_model_edit(supabase):
    """모델 수정 폼"""
    st.header("✏️ 생산모델 수정")
    
    try:
        response = supabase.table('production_models').select('*').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # 수정할 모델 선택
            options = [f"{row['model_no']} - {row['model_name']}" for _, row in df.iterrows()]
            selected = st.selectbox("수정할 모델 선택", ["선택하세요"] + options)
            
            if selected != "선택하세요":
                selected_index = options.index(selected)
                selected_row = df.iloc[selected_index]
                
                with st.form("edit_model_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_model_no = st.text_input("모델번호", value=selected_row['model_no'])
                        new_model_name = st.text_input("모델명", value=selected_row['model_name'])
                    
                    with col2:
                        process_options = ["C1", "C2", "C2-1", "직접입력"]
                        current_process = selected_row['process']
                        
                        # 현재 공정이 기본 옵션에 있는지 확인
                        if current_process in process_options:
                            default_index = process_options.index(current_process)
                            process_selection = st.selectbox("공정", process_options, index=default_index)
                        else:
                            # 기존 데이터가 직접입력된 값인 경우
                            process_selection = st.selectbox("공정", process_options, index=process_options.index("직접입력"))
                        
                        # 직접입력 선택 시 또는 기존 값이 직접입력인 경우
                        if process_selection == "직접입력":
                            if current_process not in process_options[:-1]:  # "직접입력" 제외한 기본 옵션이 아닌 경우
                                new_process = st.text_input("공정명 입력", value=current_process, placeholder="공정명을 입력하세요")
                            else:
                                new_process = st.text_input("공정명 입력", placeholder="공정명을 입력하세요")
                        else:
                            new_process = process_selection
                            
                        new_notes = st.text_area("비고", value=selected_row['notes'] if selected_row['notes'] else "")
                    
                    if st.form_submit_button("수정", type="primary"):
                        if not new_model_no or not new_model_name:
                            st.error("모델번호와 모델명은 필수 항목입니다.")
                        elif process_selection == "직접입력" and not new_process:
                            st.error("직접입력을 선택한 경우 공정명을 입력해주세요.")
                        else:
                            try:
                                updated_data = {
                                    "model_no": new_model_no,
                                    "model_name": new_model_name,
                                    "process": new_process,
                                    "notes": new_notes if new_notes else None,
                                    "updated_at": get_database_time().isoformat()  # 베트남 시간대 timestamptz
                                }
                                
                                response = supabase.table('production_models').update(updated_data).eq('id', selected_row['id']).execute()
                                
                                if response.data:
                                    st.success("✅ 모델이 성공적으로 수정되었습니다!")
                                    st.rerun()
                                else:
                                    st.error("모델 수정에 실패했습니다.")
                                    
                            except Exception as e:
                                st.error(f"모델 수정 중 오류 발생: {str(e)}")
        else:
            st.info("수정할 모델이 없습니다.")
            
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {str(e)}")

def show_model_delete(supabase):
    """모델 삭제 폼"""
    st.header("🗑️ 생산모델 삭제")
    
    try:
        response = supabase.table('production_models').select('*').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # 삭제할 모델 선택
            options = [f"{row['model_no']} - {row['model_name']}" for _, row in df.iterrows()]
            selected = st.selectbox("삭제할 모델 선택", ["선택하세요"] + options)
            
            if selected != "선택하세요":
                selected_index = options.index(selected)
                selected_row = df.iloc[selected_index]
                
                st.warning("⚠️ 다음 모델을 삭제하시겠습니까?")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**모델번호**: {selected_row['model_no']}")
                    st.write(f"**모델명**: {selected_row['model_name']}")
                
                with col2:
                    st.write(f"**공정**: {selected_row['process']}")
                    st.write(f"**비고**: {selected_row['notes'] if selected_row['notes'] else '없음'}")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("🗑️ 삭제 확인", type="primary"):
                        try:
                            response = supabase.table('production_models').delete().eq('id', selected_row['id']).execute()
                            
                            if response.data:
                                st.success("✅ 모델이 성공적으로 삭제되었습니다!")
                                st.rerun()
                            else:
                                st.error("모델 삭제에 실패했습니다.")
                                
                        except Exception as e:
                            st.error(f"모델 삭제 중 오류 발생: {str(e)}")
                
                with col2:
                    if st.button("❌ 취소"):
                        st.rerun()
        else:
            st.info("삭제할 모델이 없습니다.")
            
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {str(e)}")

def get_all_models():
    """모든 생산모델 반환 (Supabase 연동)"""
    supabase = get_supabase_client()
    
    try:
        # 실제 Supabase 조회
        response = supabase.table('production_models').select('*').order('created_at', desc=True).execute()
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"생산모델 데이터 조회 실패: {str(e)}")
        return pd.DataFrame() 