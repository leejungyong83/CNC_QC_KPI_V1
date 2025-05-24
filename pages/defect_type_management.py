import streamlit as st
import pandas as pd
from utils.supabase_client import get_supabase_client
from utils.defect_utils import get_all_defect_types, get_defect_type_names
import uuid
import time
import io  # BytesIO를 사용하기 위해 추가

def show_defect_type_management():
    """불량 유형 관리 화면을 표시합니다."""
    st.title("불량 유형 관리")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["불량 유형 목록", "불량 유형 등록", "불량 유형 수정/삭제"])
    
    # 불량 유형 목록 탭
    with tab1:
        show_defect_type_list()
    
    # 불량 유형 등록 탭
    with tab2:
        show_defect_type_add()
        
    # 불량 유형 수정/삭제 탭
    with tab3:
        show_defect_type_edit()

def show_defect_type_list():
    """불량 유형 목록을 표시합니다."""
    st.header("불량 유형 목록")
    
    # 새로고침 버튼 추가
    if st.button("🔄 새로고침", key="refresh_list"):
        st.success("데이터를 새로고침했습니다.")
    
    # 불량 유형 데이터 가져오기
    defect_types_df = get_all_defect_types()
    
    # 검색 기능 추가
    search_term = st.text_input("불량 유형 검색", placeholder="검색어를 입력하세요")
    
    if defect_types_df.empty:
        st.info("등록된 불량 유형이 없습니다. '불량 유형 등록' 탭에서 새로운 불량 유형을 추가해주세요.")
        return
    
    # 검색어 필터링
    if search_term:
        defect_types_df = defect_types_df[defect_types_df['name'].str.contains(search_term, case=False) | 
                                         defect_types_df['description'].str.contains(search_term, case=False, na=False)]
    
    # 표시할 컬럼 선택
    display_cols = ["id", "name", "description"]
    
    if set(display_cols).issubset(defect_types_df.columns):
        # 표시할 데이터프레임 준비
        df_display = defect_types_df[display_cols].copy()
        
        # 컬럼명 변경
        df_display.columns = ["ID", "불량 유형", "설명"]
        
        # 데이터프레임 표시
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "불량 유형": st.column_config.TextColumn("불량 유형", width="medium"),
                "설명": st.column_config.TextColumn("설명", width="large"),
            }
        )
        
        # 전체 불량 유형 수 표시
        st.caption(f"총 {len(df_display)}개의 불량 유형이 등록되어 있습니다.")
        
        # 엑셀 다운로드 버튼
        try:
            buffer = io.BytesIO()  # BytesIO 객체 생성
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_display.to_excel(writer, sheet_name='불량유형목록', index=False)
            
            excel_data = buffer.getvalue()  # 바이트 데이터 추출
            
            st.download_button(
                label="📥 Excel 다운로드",
                data=excel_data,
                file_name="defect_types.xlsx",
                mime="application/vnd.ms-excel"
            )
        except Exception as e:
            st.error(f"엑셀 다운로드 준비 중 오류가 발생했습니다: {str(e)}")
    else:
        st.error("데이터 형식이 올바르지 않습니다. 필요한 컬럼이 없습니다.")

def show_defect_type_add():
    """불량 유형 등록 폼을 표시합니다."""
    st.header("불량 유형 등록")
    
    # 새로고침 버튼 추가
    if st.button("🔄 새로고침", key="refresh_add"):
        st.success("데이터를 새로고침했습니다.")
    
    # 불량 유형 데이터 가져오기
    defect_types_df = get_all_defect_types()
    
    # 폼
    with st.form("defect_type_add_form", clear_on_submit=True):
        st.subheader("새 불량 유형 정보 입력")
        
        # 불량 유형 이름
        defect_name = st.text_input("불량 유형 이름 *", placeholder="예: 치수 불량")
        
        # 설명
        defect_desc = st.text_area("설명", placeholder="이 불량 유형에 대한 설명을 입력하세요")
        
        # 제출 버튼
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.form_submit_button("불량 유형 등록", use_container_width=True)
        
        if submit_button:
            if not defect_name:
                st.error("불량 유형 이름은 필수 입력 항목입니다.")
            else:
                # 중복 체크
                if not defect_types_df.empty and defect_name in defect_types_df["name"].values:
                    st.error(f"'{defect_name}' 불량 유형이 이미 존재합니다.")
                else:
                    # 새 불량 유형 추가
                    with st.spinner("불량 유형을 등록 중입니다..."):
                        success = add_defect_type(defect_name, defect_desc)
                        if success:
                            st.success(f"새 불량 유형 '{defect_name}'이(가) 등록되었습니다.")
                            # st.rerun() 대신 잠시 대기 후 성공 메시지만 표시
                            time.sleep(1)
                        else:
                            st.error("불량 유형 등록 중 오류가 발생했습니다.")
    
    # 현재 등록된 불량 유형 목록 (간략히 표시)
    st.subheader("현재 등록된 불량 유형")
    if not defect_types_df.empty:
        st.write(", ".join(defect_types_df["name"].tolist()))
    else:
        st.info("등록된 불량 유형이 없습니다.")

def show_defect_type_edit():
    """불량 유형 수정/삭제 폼을 표시합니다."""
    st.header("불량 유형 수정/삭제")
    
    # 새로고침 버튼 추가
    if st.button("🔄 새로고침", key="refresh_edit"):
        st.success("데이터를 새로고침했습니다.")
    
    # 불량 유형 데이터 가져오기
    defect_types_df = get_all_defect_types()
    
    if defect_types_df.empty:
        st.info("수정할 불량 유형이 없습니다. 먼저 불량 유형을 등록해주세요.")
        return
    
    # 수정할 불량 유형 선택
    selected_id = st.selectbox(
        "수정할 불량 유형을 선택하세요", 
        options=defect_types_df["id"].tolist(),
        format_func=lambda x: f"{get_defect_type_name(x, defect_types_df)} ({x})"
    )
    
    if selected_id:
        selected_defect = defect_types_df[defect_types_df["id"] == selected_id].iloc[0]
        
        # 현재 선택된 불량 유형 정보 표시
        st.subheader("현재 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**불량 유형:** {selected_defect['name']}")
        with col2:
            st.write(f"**ID:** {selected_defect['id']}")
        
        st.write(f"**설명:** {selected_defect['description'] or '(설명 없음)'}")
        
        # 수정/삭제 탭
        edit_tabs = st.tabs(["수정", "삭제"])
        
        # 수정 탭
        with edit_tabs[0]:
            with st.form("defect_type_edit_form"):
                st.subheader("불량 유형 정보 수정")
                
                # 불량 유형 이름
                defect_name = st.text_input("불량 유형 이름 *", value=selected_defect["name"])
                
                # 설명
                defect_desc = st.text_area("설명", value=selected_defect["description"] if "description" in selected_defect and selected_defect["description"] else "")
                
                # 제출 버튼
                col1, col2 = st.columns([1, 4])
                with col1:
                    submit_button = st.form_submit_button("불량 유형 수정", use_container_width=True)
                
                if submit_button:
                    if not defect_name:
                        st.error("불량 유형 이름은 필수 입력 항목입니다.")
                    else:
                        # 중복 체크 (자기 자신은 제외)
                        if not defect_types_df.empty:
                            dupes = defect_types_df[(defect_types_df["name"] == defect_name) & (defect_types_df["id"] != selected_id)]
                            if not dupes.empty:
                                st.error(f"'{defect_name}' 불량 유형이 이미 존재합니다.")
                                return
                        
                        # 불량 유형 수정
                        with st.spinner("불량 유형을 수정 중입니다..."):
                            success = update_defect_type(selected_id, defect_name, defect_desc)
                            if success:
                                st.success(f"불량 유형 '{defect_name}'이(가) 수정되었습니다.")
                                time.sleep(1)  # 사용자가 성공 메시지를 볼 수 있도록 잠시 대기
                            else:
                                st.error("불량 유형 수정 중 오류가 발생했습니다.")
        
        # 삭제 탭
        with edit_tabs[1]:
            st.subheader("불량 유형 삭제")
            st.warning(f"'{selected_defect['name']}' 불량 유형을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")
            
            # 확인을 위한 이름 입력
            confirmation = st.text_input("삭제를 확인하려면 불량 유형 이름을 입력하세요", key="delete_confirmation")
            
            if st.button("불량 유형 삭제", key="delete_defect_button", type="primary", disabled=(confirmation != selected_defect['name'])):
                with st.spinner("불량 유형을 삭제 중입니다..."):
                    success = delete_defect_type(selected_id)
                    if success:
                        st.success(f"불량 유형 '{selected_defect['name']}'이(가) 삭제되었습니다.")
                        time.sleep(1)  # 사용자가 성공 메시지를 볼 수 있도록 잠시 대기
                    else:
                        st.error("불량 유형 삭제 중 오류가 발생했습니다.")

def add_defect_type(name, description=None):
    """새 불량 유형을 추가합니다."""
    try:
        # Supabase 클라이언트 연결
        supabase = get_supabase_client()
        
        # 새 불량 유형 데이터
        defect_data = {
            "name": name,
            "description": description if description else None
        }
        
        # defect_types 테이블에 데이터 삽입
        response = supabase.table("defect_types").insert(defect_data).execute()
        
        return True if response.data else False
    
    except ValueError as e:
        # 환경 변수 설정 오류 (이미 supabase_client.py에서 처리됨)
        return False
    except Exception as e:
        # 네트워크 오류를 포함한 일반적인 오류
        error_msg = str(e)
        if "getaddrinfo failed" in error_msg:
            st.warning("네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인하세요.")
            st.info("오프라인 모드로 작동합니다. 일부 기능이 제한될 수 있습니다.")
        else:
            st.error(f"불량 유형 추가 중 오류 발생: {error_msg}")
        return False

def update_defect_type(defect_id, name, description=None):
    """기존 불량 유형을 수정합니다."""
    try:
        # Supabase 클라이언트 연결
        supabase = get_supabase_client()
        
        # 수정할 불량 유형 데이터
        defect_data = {
            "name": name,
            "description": description if description else None,
            "updated_at": "now()"
        }
        
        # defect_types 테이블에서 데이터 업데이트
        response = supabase.table("defect_types").update(defect_data).eq("id", defect_id).execute()
        
        return True if response.data else False
    
    except ValueError as e:
        # 환경 변수 설정 오류 (이미 supabase_client.py에서 처리됨)
        return False
    except Exception as e:
        # 네트워크 오류를 포함한 일반적인 오류
        error_msg = str(e)
        if "getaddrinfo failed" in error_msg:
            st.warning("네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인하세요.")
            st.info("오프라인 모드로 작동합니다. 일부 기능이 제한될 수 있습니다.")
        else:
            st.error(f"불량 유형 수정 중 오류 발생: {error_msg}")
        return False

def delete_defect_type(defect_id):
    """불량 유형을 삭제합니다."""
    try:
        # Supabase 클라이언트 연결
        supabase = get_supabase_client()
        
        # defect_types 테이블에서 데이터 삭제
        response = supabase.table("defect_types").delete().eq("id", defect_id).execute()
        
        return True if response.data else False
    
    except ValueError as e:
        # 환경 변수 설정 오류 (이미 supabase_client.py에서 처리됨)
        return False
    except Exception as e:
        # 네트워크 오류를 포함한 일반적인 오류
        error_msg = str(e)
        if "getaddrinfo failed" in error_msg:
            st.warning("네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인하세요.")
            st.info("오프라인 모드로 작동합니다. 일부 기능이 제한될 수 있습니다.")
        else:
            st.error(f"불량 유형 삭제 중 오류 발생: {error_msg}")
        return False

def get_defect_type_name(defect_id, defect_types_df):
    """불량 유형 ID로 이름을 조회합니다."""
    if defect_types_df.empty:
        return "알 수 없음"
    
    defect = defect_types_df[defect_types_df["id"] == defect_id]
    if defect.empty:
        return "알 수 없음"
    
    return defect.iloc[0]["name"] 