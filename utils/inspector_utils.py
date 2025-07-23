"""
검사자 관련 유틸리티 함수들
"""

import streamlit as st


def get_all_inspectors():
    """모든 검사자 정보를 반환하는 함수"""
    # 세션 상태에 검사자 데이터가 없으면 초기화
    if "inspectors_data" not in st.session_state:
        initialize_inspector_data()
    
    return st.session_state.inspectors_data


def initialize_inspector_data():
    """검사자 데이터 초기화"""
    if "inspectors_data" not in st.session_state:
        st.session_state.inspectors_data = [
            {"id": "dlwjddyd83@gmail.com", "name": "관리자", "department": "관리부", "process": "관리", "created_at": "2024-01-01", "last_login": "2025-02-28 14:33:13", "status": "활성"},
            {"id": "user", "name": "일반사용자1", "department": "관리부", "process": "관리", "created_at": "2024-01-02", "last_login": "2024-01-14 00:00:00", "status": "활성"},
            {"id": "inspector1", "name": "검사자1", "department": "생산부", "process": "선반", "created_at": "2024-02-01", "last_login": "2024-02-20 00:00:00", "status": "활성"},
            {"id": "inspector2", "name": "검사자2", "department": "품질부", "process": "밀링", "created_at": "2024-02-10", "last_login": "2024-02-15 00:00:00", "status": "비활성"},
        ] 