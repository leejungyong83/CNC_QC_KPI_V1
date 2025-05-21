import streamlit as st
import pandas as pd
from datetime import datetime

# 페이지 진입 시 캐시 비우기
st.cache_data.clear()
st.cache_resource.clear()

# 초기 데이터 정의
INITIAL_ADMIN_DATA = [
    {"id": "dlwjddyd83@gmail.com", "name": "이정봉", "role": "관리자"},
    {"id": "jinuk.cho@gmail.com", "name": "조진욱", "role": "관리자"},
    {"id": "haeunkim20170805@gmail.com", "name": "김은희", "role": "관리자"},
    {"id": "zetooo1972@gmail.com", "name": "박영일", "role": "관리자"},
]

INITIAL_USER_DATA = [
    {"id": "dangthuymai04198@gmail.com", "name": "dang thuy mai", "department": "office"},
    {"id": "nguyulemao252@gmail.com", "name": "TRAN VAN THANH", "department": "office"},
    {"id": "tranvaninh@gmail.com", "name": "tran van minh", "department": "leader"},
    {"id": "admin@example.com", "name": "관리자", "department": "admin"},
    {"id": "nguyenquangha0511@gmail.com", "name": "NGUYỄN QUANG HÀ", "department": "CNC"},
    {"id": "hoa379488@gmail.com", "name": "LÂM THỊ NGỌC HOA", "department": "CNC"},
    {"id": "nguyenhongthanh210498@gmail.com", "name": "nguyen hong hanh", "department": "CNC"},
    {"id": "Boocavalli@gmail.com", "name": "NGUYỄN THỊ ÁNH NGUYỆT", "department": "CNC"},
    {"id": "sthiyen7@gmail.com", "name": "sen thi yen", "department": "CNC"},
    {"id": "nguyenthiphuong20102004@gmail.com", "name": "NGUYỄN THỊ PHƯƠNG", "department": "CNC"},
]

# 세션 상태 초기화
if "admin_data" not in st.session_state:
    st.session_state.admin_data = INITIAL_ADMIN_DATA.copy()
if "user_data" not in st.session_state:
    st.session_state.user_data = INITIAL_USER_DATA.copy()
if "admin_edit_success" not in st.session_state:
    st.session_state.admin_edit_success = False
if "admin_add_success" not in st.session_state:
    st.session_state.admin_add_success = False
if "admin_delete_success" not in st.session_state:
    st.session_state.admin_delete_success = False

# 관리자 수정 콜백 함수
def update_admin_info(admin_id, new_name, new_role, change_password=False, new_password=None):
    for i, admin in enumerate(st.session_state.admin_data):
        if admin["id"] == admin_id:
            st.session_state.admin_data[i]["name"] = new_name
            st.session_state.admin_data[i]["role"] = new_role
            st.session_state.admin_edit_success = True
            return True
    return False

# 관리자 추가 콜백 함수
def add_new_admin(admin_id, admin_name, password):
    st.session_state.admin_data.append({
        "id": admin_id,
        "name": admin_name,
        "role": "관리자"
    })
    st.session_state.admin_add_success = True

# 관리자 삭제 콜백 함수
def delete_admin(admin_id):
    st.session_state.admin_data = [admin for admin in st.session_state.admin_data if admin["id"] != admin_id]
    st.session_state.admin_delete_success = True

def show_user_management():
    """관리자 및 사용자 관리 페이지를 표시합니다."""
    st.header("🔑 관리자 및 사용자 관리")
    
    # 탭 생성
    admin_tab, user_tab = st.tabs(["관리자 관리", "사용자 관리"])
    
    # 관리자 관리 탭
    with admin_tab:
        show_admin_management()
    
    # 사용자 관리 탭
    with user_tab:
        show_user_tab_content()

def show_admin_management():
    """관리자 관리 탭의 내용을 표시합니다."""
    # 관리자 계정 목록
    st.subheader("관리자 계정 목록")
    
    # 관리자 목록 표시
    st.dataframe(
        st.session_state.admin_data,
        column_config={
            "id": st.column_config.TextColumn("아이디", width="medium"),
            "name": st.column_config.TextColumn("이름", width="medium"),
            "role": st.column_config.TextColumn("권한", width="medium"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # 성공 메시지 표시
    if st.session_state.admin_edit_success:
        st.success("관리자 정보가 수정되었습니다.")
        st.session_state.admin_edit_success = False
    
    if st.session_state.admin_add_success:
        st.success("새 관리자가 추가되었습니다.")
        st.session_state.admin_add_success = False
        
    if st.session_state.admin_delete_success:
        st.success("관리자가 삭제되었습니다.")
        st.session_state.admin_delete_success = False
    
    # 새 관리자 추가
    with st.expander("새 관리자 추가", expanded=False):
        st.subheader("새 관리자 추가")
        
        # 폼 대신 직접 필드 배치
        admin_id = st.text_input("아이디(이메일)", key="new_admin_id")
        
        # 비밀번호와 확인은 같은 행에 배치
        password_col1, password_col2 = st.columns(2)
        with password_col1:
            password = st.text_input("비밀번호", type="password", key="new_admin_password")
        with password_col2:
            password_confirm = st.text_input("비밀번호 확인", type="password", key="new_admin_password_confirm")
        
        admin_name = st.text_input("이름", key="new_admin_name")
        
        if st.button("추가", key="admin_add_button"):
            if not admin_id or not password or not admin_name:
                st.error("모든 필드를 입력해주세요.")
            elif password != password_confirm:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                add_new_admin(admin_id, admin_name, password)
                st.rerun()
    
    # 관리자 정보 수정
    with st.expander("관리자 정보 수정", expanded=True):
        st.subheader("관리자 정보 수정")
        
        # 수정할 관리자 선택
        admin_options = [f"{admin['id']}" for admin in st.session_state.admin_data]
        if admin_options:  # 관리자가 존재할 경우에만
            selected_admin_id = st.selectbox("수정할 관리자 선택", admin_options, key="admin_edit_select")
            
            # 선택된 관리자의 정보 가져오기
            selected_admin_info = None
            for admin in st.session_state.admin_data:
                if admin['id'] == selected_admin_id:
                    selected_admin_info = admin
                    break
            
            if selected_admin_info:
                # 수정할 정보 입력
                edit_name = st.text_input("이름", value=selected_admin_info['name'], key="admin_edit_name")
                edit_role = st.selectbox("권한", ["관리자", "슈퍼관리자"], 
                                        index=0 if selected_admin_info['role'] == "관리자" else 1, 
                                        key="admin_edit_role")
                
                # 비밀번호 변경 옵션
                change_password = st.checkbox("비밀번호 변경", key="admin_change_password")
                
                if change_password:
                    edit_password_col1, edit_password_col2 = st.columns(2)
                    with edit_password_col1:
                        edit_password = st.text_input("새 비밀번호", type="password", key="admin_edit_password")
                    with edit_password_col2:
                        edit_password_confirm = st.text_input("새 비밀번호 확인", type="password", key="admin_edit_password_confirm")
                
                if st.button("수정", key="admin_edit_button"):
                    if not edit_name:
                        st.error("이름을 입력해주세요.")
                    elif change_password and (not edit_password or not edit_password_confirm):
                        st.error("새 비밀번호를 입력해주세요.")
                    elif change_password and edit_password != edit_password_confirm:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        # 관리자 정보 업데이트
                        update_admin_info(
                            selected_admin_id, 
                            edit_name, 
                            edit_role, 
                            change_password=change_password, 
                            new_password=edit_password if change_password else None
                        )
                        st.rerun()
        else:
            st.info("관리자가 존재하지 않습니다.")
    
    # 관리자 삭제
    with st.expander("관리자 삭제", expanded=False):
        st.subheader("관리자 삭제")
        
        # 드롭다운 대신 선택 상자
        if admin_options:  # 관리자가 존재할 경우에만
            selected_admin = st.selectbox("삭제할 관리자 선택", admin_options, key="admin_delete_select")
            
            if st.button("삭제", key="admin_delete_button"):
                delete_admin(selected_admin)
                st.rerun()
        else:
            st.info("삭제할 관리자가 없습니다.")

def show_user_tab_content():
    """사용자 관리 탭의 내용을 표시합니다."""
    # 사용자 계정 목록
    st.subheader("사용자 계정 목록")
    
    # 사용자 목록 표시
    st.dataframe(
        st.session_state.user_data,
        column_config={
            "id": st.column_config.TextColumn("아이디", width="medium"),
            "name": st.column_config.TextColumn("이름", width="medium"),
            "department": st.column_config.TextColumn("부서", width="medium"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # 새 사용자 추가
    st.subheader("새 사용자 추가")
    
    # 폼 대신 직접 필드 배치
    user_id = st.text_input("아이디(이메일)", key="user_id_input")
    
    # 비밀번호와 확인은 같은 행에 배치
    password_col1, password_col2 = st.columns(2)
    with password_col1:
        user_password = st.text_input("비밀번호", type="password", key="user_password_input")
    with password_col2:
        user_password_confirm = st.text_input("비밀번호 확인", type="password", key="user_password_confirm_input")
    
    user_name = st.text_input("이름", key="user_name_input")
    user_department = st.text_input("부서", key="user_department_input")
    
    if st.button("추가", key="user_add_button"):
        if not user_id or not user_password or not user_name or not user_department:
            st.error("모든 필드를 입력해주세요.")
        elif user_password != user_password_confirm:
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            # 세션 상태에 새 사용자 추가
            st.session_state.user_data.append({
                "id": user_id,
                "name": user_name,
                "department": user_department
            })
            st.success(f"사용자 {user_name}({user_id})이(가) 추가되었습니다.")
            st.rerun()
    
    # 사용자 삭제
    st.subheader("사용자 삭제")
    
    # 삭제할 사용자 선택
    user_options = [f"{user['id']}" for user in st.session_state.user_data]
    if user_options:  # 사용자가 존재할 경우에만
        selected_user = st.selectbox("삭제할 사용자 선택", user_options)
        
        if st.button("삭제", key="user_delete_button"):
            # 세션 상태에서 사용자 삭제
            st.session_state.user_data = [user for user in st.session_state.user_data if user['id'] != selected_user]
            st.success(f"사용자 {selected_user}이(가) 삭제되었습니다.")
            st.rerun() 