import streamlit as st
import pandas as pd
import time
from io import BytesIO
from utils.supabase_client import get_supabase_client

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)

def show_defect_type_management():
    """불량유형 관리 화면을 표시합니다."""
    st.title("🔧 불량유형 관리")
    
    # 탭 생성
    tabs = st.tabs(["📋 불량유형 목록", "➕ 불량유형 등록", "✏️ 불량유형 수정/삭제"])
    
    with tabs[0]:
        show_defect_type_list()
    
    with tabs[1]:
        show_defect_type_add()
    
    with tabs[2]:
        show_defect_type_edit()

def show_defect_type_list():
    """불량유형 목록을 표시합니다."""
    st.subheader("📋 불량유형 목록")
    
    # 새로고침 버튼
    if st.button("🔄 새로고침", key="refresh_list"):
        st.success("데이터를 새로고침했습니다.")
    
    # 불량유형 데이터 가져오기
    defect_types_df = get_all_defect_types()
    
    if defect_types_df.empty:
        st.info("등록된 불량유형이 없습니다.")
        return
    
    # 데이터프레임 표시
    if "id" in defect_types_df.columns:
        # 컬럼 순서 정리
        display_columns = ["id", "name"]
        if "description" in defect_types_df.columns:
            display_columns.append("description")
        if "created_at" in defect_types_df.columns:
            display_columns.append("created_at")
        if "updated_at" in defect_types_df.columns:
            display_columns.append("updated_at")
        
        # 존재하는 컬럼만 선택
        existing_columns = [col for col in display_columns if col in defect_types_df.columns]
        display_df = defect_types_df[existing_columns]
        
        # 컬럼명 한글화
        column_mapping = {
            "id": "ID",
            "name": "불량유형명",
            "description": "설명", 
            "created_at": "생성일시",
            "updated_at": "수정일시"
        }
        display_df = display_df.rename(columns=column_mapping)
        
        # 데이터프레임 표시
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        st.info(f"총 {len(defect_types_df)}개의 불량유형이 등록되어 있습니다.")
        
        # 엑셀 다운로드 버튼
        if st.button("📊 엑셀로 다운로드"):
            try:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    display_df.to_excel(writer, index=False, sheet_name='불량유형목록')
                
                output.seek(0)
                
                st.download_button(
                    label="💾 불량유형목록.xlsx 다운로드",
                    data=output.getvalue(),
                    file_name="불량유형목록.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"엑셀 다운로드 준비 중 오류가 발생했습니다: {str(e)}")
    else:
        st.error("데이터 형식이 올바르지 않습니다. 필요한 컬럼이 없습니다.")

def show_defect_type_add():
    """불량유형 등록 폼을 표시합니다."""
    st.subheader("➕ 새 불량유형 등록")
    
    # 새로고침 버튼
    if st.button("🔄 새로고침", key="refresh_add"):
        st.success("데이터를 새로고침했습니다.")
    
    # 불량유형 데이터 가져오기
    defect_types_df = get_all_defect_types()
    
    # 폼
    with st.form("defect_type_add_form", clear_on_submit=True):
        st.subheader("새 불량유형 정보 입력")
        
        # 불량유형 이름
        defect_name = st.text_input("불량유형 이름 *", placeholder="예: 치수 불량")
        
        # 설명
        defect_desc = st.text_area("설명", placeholder="이 불량유형에 대한 설명을 입력하세요")
        
        # 제출 버튼
        submit_button = st.form_submit_button("불량유형 등록", type="primary")
        
        if submit_button:
            if not defect_name:
                st.error("불량유형 이름은 필수 입력 항목입니다.")
            else:
                # 중복 체크
                if not defect_types_df.empty and defect_name in defect_types_df["name"].values:
                    st.error(f"'{defect_name}' 불량유형이 이미 존재합니다.")
                else:
                    # 새 불량유형 추가
                    with st.spinner("불량유형을 등록 중입니다..."):
                        success = add_defect_type(defect_name, defect_desc)
                        if success:
                            st.success(f"새 불량유형 '{defect_name}'이(가) 등록되었습니다.")
                            st.rerun()
                        else:
                            st.error("불량유형 등록 중 오류가 발생했습니다.")
    
    # 현재 등록된 불량유형 목록 (간략히 표시)
    st.subheader("현재 등록된 불량유형")
    if not defect_types_df.empty:
        st.write(", ".join(defect_types_df["name"].tolist()))
    else:
        st.info("등록된 불량유형이 없습니다.")

def show_defect_type_edit():
    """불량유형 수정/삭제 폼을 표시합니다."""
    st.subheader("✏️ 불량유형 수정/삭제")
    
    # 새로고침 버튼
    if st.button("🔄 새로고침", key="refresh_edit"):
        st.success("데이터를 새로고침했습니다.")
    
    # 불량유형 데이터 가져오기
    defect_types_df = get_all_defect_types()
    
    if defect_types_df.empty:
        st.info("수정할 불량유형이 없습니다. 먼저 불량유형을 등록해주세요.")
        return
    
    # 수정할 불량유형 선택
    selected_id = st.selectbox(
        "수정할 불량유형을 선택하세요", 
        options=defect_types_df["id"].tolist(),
        format_func=lambda x: f"{get_defect_type_name(x, defect_types_df)} ({x})"
    )
    
    if selected_id:
        selected_defect = defect_types_df[defect_types_df["id"] == selected_id].iloc[0]
        
        # 현재 선택된 불량유형 정보 표시
        st.subheader("현재 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**불량유형:** {selected_defect['name']}")
        with col2:
            st.write(f"**ID:** {selected_defect['id']}")
        
        st.write(f"**설명:** {selected_defect.get('description', '(설명 없음)')}")
        
        # 수정/삭제 탭
        edit_tabs = st.tabs(["수정", "삭제"])
        
        # 수정 탭
        with edit_tabs[0]:
            with st.form("defect_type_edit_form"):
                st.subheader("불량유형 정보 수정")
                
                # 불량유형 이름
                defect_name = st.text_input("불량유형 이름 *", value=selected_defect["name"])
                
                # 설명
                current_desc = selected_defect.get("description", "")
                defect_desc = st.text_area("설명", value=current_desc if current_desc else "")
                
                # 제출 버튼
                submit_button = st.form_submit_button("불량유형 수정", type="primary")
                
                if submit_button:
                    if not defect_name:
                        st.error("불량유형 이름은 필수 입력 항목입니다.")
                    else:
                        # 중복 체크 (자기 자신은 제외)
                        if not defect_types_df.empty:
                            dupes = defect_types_df[(defect_types_df["name"] == defect_name) & (defect_types_df["id"] != selected_id)]
                            if not dupes.empty:
                                st.error(f"'{defect_name}' 불량유형이 이미 존재합니다.")
                            else:
                                # 불량유형 수정
                                with st.spinner("불량유형을 수정 중입니다..."):
                                    success = update_defect_type(selected_id, defect_name, defect_desc)
                                    if success:
                                        st.success(f"불량유형 '{defect_name}'이(가) 수정되었습니다.")
                                        st.rerun()
                                    else:
                                        st.error("불량유형 수정 중 오류가 발생했습니다.")
        
        # 삭제 탭
        with edit_tabs[1]:
            st.subheader("불량유형 삭제")
            st.warning("⚠️ 주의: 불량유형을 삭제하면 되돌릴 수 없습니다!")
            
            # 삭제할 불량유형 정보 다시 표시
            st.write(f"**삭제할 불량유형:** {selected_defect['name']}")
            st.write(f"**설명:** {selected_defect.get('description', '(설명 없음)')}")
            
            # 삭제 확인
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🗑️ 삭제 확인", type="primary"):
                    with st.spinner("불량유형을 삭제 중입니다..."):
                        success = delete_defect_type(selected_id)
                        if success:
                            st.success(f"불량유형 '{selected_defect['name']}'이(가) 삭제되었습니다.")
                            st.rerun()
                        else:
                            st.error("불량유형 삭제 중 오류가 발생했습니다.")
            
            with col2:
                if st.button("❌ 취소"):
                    st.rerun()

def get_all_defect_types():
    """모든 불량유형 데이터를 가져옵니다."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("defect_types").select("*").order("created_at", desc=True).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"불량유형 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")
        return pd.DataFrame()

def add_defect_type(name, description=None):
    """새 불량유형을 추가합니다."""
    try:
        supabase = get_supabase_client()
        
        defect_data = {
            "name": name,
            "description": description if description else None
        }
        
        response = supabase.table("defect_types").insert(defect_data).execute()
        return True if response.data else False
    
    except Exception as e:
        st.error(f"불량유형 추가 중 오류 발생: {str(e)}")
        return False

def update_defect_type(defect_id, name, description=None):
    """기존 불량유형을 수정합니다."""
    try:
        supabase = get_supabase_client()
        
        defect_data = {
            "name": name,
            "description": description if description else None
        }
        
        response = supabase.table("defect_types").update(defect_data).eq("id", defect_id).execute()
        return True if response.data else False
    
    except Exception as e:
        st.error(f"불량유형 수정 중 오류 발생: {str(e)}")
        return False

def delete_defect_type(defect_id):
    """불량유형을 삭제합니다."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("defect_types").delete().eq("id", defect_id).execute()
        return True if response.data else False
    
    except Exception as e:
        st.error(f"불량유형 삭제 중 오류 발생: {str(e)}")
        return False

def get_defect_type_name(defect_id, defect_types_df):
    """불량유형 ID로 이름을 조회합니다."""
    if defect_types_df.empty:
        return "알 수 없음"
    
    defect = defect_types_df[defect_types_df["id"] == defect_id]
    if defect.empty:
        return "알 수 없음"
    
    return defect.iloc[0]["name"] 