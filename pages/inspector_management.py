import streamlit as st
import pandas as pd
import datetime

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)
from utils.inspector_utils import get_all_inspectors

def show_inspector_management():
    """검사자 등록 및 관리 페이지"""
    st.title("🔑 검사자 등록 및 관리")
    
    # 초기 데이터 설정
    initialize_inspector_data()
    
    # 탭 생성
    tabs = st.tabs(["검사자 목록", "신규 검사자 등록", "검사자 통계"])
    
    with tabs[0]:
        show_inspector_list()
    
    with tabs[1]:
        show_inspector_registration()
    
    with tabs[2]:
        show_inspector_statistics()

def initialize_inspector_data():
    """검사자 데이터 초기화 (로컬 확장 버전)"""
    # 기본 검사자 데이터 초기화는 utils에서 처리
    from utils.inspector_utils import initialize_inspector_data as init_base_data
    init_base_data()
    
    # 필터 상태 초기화
    if "filter_dept" not in st.session_state:
        st.session_state.filter_dept = "전체"
    if "filter_process" not in st.session_state:
        st.session_state.filter_process = "전체"
    if "filter_status" not in st.session_state:
        st.session_state.filter_status = "전체"

def show_inspector_list():
    """등록된 검사자 목록 페이지"""
    # 글로벌 CSS 스타일 추가
    st.markdown("""
    <style>
    .red-border {
        border: 2px solid red;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .inspector-card {
        padding: 10px;
        margin-bottom: 15px;
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("등록된 검사자 목록")
    
    # 필터링된 데이터 가져오기
    filtered_data = filter_inspectors(
        st.session_state.filter_dept,
        st.session_state.filter_process,
        st.session_state.filter_status,
        ""
    )
    
    # 테이블 형식의 검사자 목록
    if filtered_data:
        df = pd.DataFrame(filtered_data)
        st.dataframe(
            df,
            column_config={
                "id": st.column_config.TextColumn("아이디", width="medium"),
                "name": st.column_config.TextColumn("이름", width="medium"),
                "department": st.column_config.TextColumn("부서", width="medium"),
                "process": st.column_config.TextColumn("공정", width="medium"),
                "created_at": st.column_config.TextColumn("계정생성일", width="medium"),
                "last_login": st.column_config.TextColumn("최근접속일", width="medium"),
                "status": st.column_config.TextColumn("상태", width="small"),
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("등록된 검사자가 없습니다.")
    
    # 필터 섹션
    st.markdown("---")
    st.subheader("검사자 필터링")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.filter_dept = st.selectbox(
            "부서 필터", 
            options=["전체", "관리부", "생산부", "품질부"],
            key="dept_filter"
        )
    
    with col2:
        st.session_state.filter_process = st.selectbox(
            "공정 필터", 
            options=["전체", "관리", "선반", "밀링", "연삭"],
            key="process_filter"
        )
    
    with col3:
        st.session_state.filter_status = st.selectbox(
            "상태 필터", 
            options=["전체", "활성", "비활성", "휴면"],
            key="status_filter"
        )
    
    # 검색어 필드
    search = st.text_input("검색어", placeholder="아이디 또는 이름으로 검색", key="inspector_search")
    
    # 필터 버튼 행
    filter_col1, filter_col2 = st.columns([1, 1])
    with filter_col1:
        filter_button = st.button("필터 적용", key="apply_filter", type="primary", use_container_width=True)
    
    with filter_col2:
        reset_button = st.button("필터 초기화", key="reset_filter", use_container_width=True)
        
        if reset_button:
            st.session_state.filter_dept = "전체"
            st.session_state.filter_process = "전체"
            st.session_state.filter_status = "전체"
            st.rerun()
    
    # 현재 필터 상태로 필터링된 데이터
    search_filtered_data = filter_inspectors(
        st.session_state.filter_dept,
        st.session_state.filter_process,
        st.session_state.filter_status,
        search if search else ""
    )
    
    st.markdown("---")
    
    # 빨간색 테두리 카드 목록
    st.subheader("카드 형식 목록")
    
    # 필터링된 검사자 목록 표시
    if search_filtered_data:
        if search:
            st.success(f"검색 결과: {len(search_filtered_data)}명의 검사자")
        
        # 카드 형태 목록 표시
        for i, inspector in enumerate(search_filtered_data):
            # HTML로 빨간색 테두리가 있는 카드 생성
            card_html = f"""
            <div class="red-border">
                <div class="inspector-card">
                    <table width="100%">
                        <tr>
                            <td width="33%"><strong>아이디:</strong> {inspector['id']}</td>
                            <td width="33%"><strong>부서:</strong> {inspector['department']}</td>
                            <td width="33%"><strong>생성일:</strong> {inspector['created_at']}</td>
                        </tr>
                        <tr>
                            <td width="33%"><strong>이름:</strong> {inspector['name']}</td>
                            <td width="33%"><strong>공정:</strong> {inspector['process']}</td>
                            <td width="33%"><strong>상태:</strong> {inspector['status']}</td>
                        </tr>
                    </table>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 삭제 버튼은 스트림릿으로 구현 (HTML 내부에 넣을 수 없음)
            if st.button("삭제", key=f"delete_{i}", type="primary"):
                st.session_state.inspectors_data = [
                    insp for insp in st.session_state.inspectors_data if insp["id"] != inspector["id"]
                ]
                st.success(f"검사자 '{inspector['name']}'이(가) 삭제되었습니다.")
                st.rerun()
    else:
        st.info("조건에 맞는 검사자가 없습니다.")
    
    # 검사자 삭제 섹션
    st.markdown("---")
    st.subheader("검사자 삭제")
    
    if st.session_state.inspectors_data:
        # 검사자 목록으로 옵션 생성
        inspector_options = ["선택하세요"] + [f"{insp['id']} - {insp['name']} ({insp['department']})" for insp in st.session_state.inspectors_data]
        selected_inspector = st.selectbox("삭제할 검사자 선택", inspector_options, key="inspector_to_delete")
        
        if selected_inspector != "선택하세요":
            # 선택된 검사자 ID 추출
            inspector_id = selected_inspector.split(" - ")[0]
            
            # 선택된 검사자 정보 표시
            selected_data = next((insp for insp in st.session_state.inspectors_data if insp["id"] == inspector_id), None)
            if selected_data:
                st.write("**삭제할 검사자 정보:**")
                
                # 정보를 컬럼으로 표시
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**아이디**: {selected_data['id']}")
                    st.info(f"**이름**: {selected_data['name']}")
                    st.info(f"**부서**: {selected_data['department']}")
                with col2:
                    st.info(f"**공정**: {selected_data['process']}")
                    st.info(f"**계정생성일**: {selected_data['created_at']}")
                    st.info(f"**상태**: {selected_data['status']}")
                
                # 삭제 확인
                st.warning("⚠️ 주의: 삭제한 검사자 정보는 복구할 수 없습니다.")
                if st.button("검사자 삭제", key="delete_inspector_button", type="primary"):
                    # 검사자 삭제
                    st.session_state.inspectors_data = [
                        insp for insp in st.session_state.inspectors_data if insp["id"] != inspector_id
                    ]
                    st.success(f"검사자 '{selected_data['name']}'이(가) 삭제되었습니다.")
                    st.rerun()
    else:
        st.info("등록된 검사자가 없습니다.")

def filter_inspectors(dept, process, status, search_text=""):
    """검사자 데이터 필터링"""
    filtered_data = st.session_state.inspectors_data.copy()
    
    # 부서 필터 적용
    if dept != "전체":
        filtered_data = [insp for insp in filtered_data if insp["department"] == dept]
    
    # 공정 필터 적용
    if process != "전체":
        filtered_data = [insp for insp in filtered_data if insp["process"] == process]
    
    # 상태 필터 적용
    if status != "전체":
        filtered_data = [insp for insp in filtered_data if insp["status"] == status]
    
    # 검색어 필터 적용
    if search_text:
        filtered_data = [
            insp for insp in filtered_data 
            if search_text.lower() in insp["id"].lower() or search_text.lower() in insp["name"].lower()
        ]
    
    return filtered_data

def search_inspectors(search_text):
    """검사자 검색"""
    if not search_text:
        return []
    
    return [
        insp for insp in st.session_state.inspectors_data 
        if search_text.lower() in insp["id"].lower() or search_text.lower() in insp["name"].lower()
    ]

def show_inspector_registration():
    """신규 검사자 등록 페이지"""
    st.header("신규 검사자 등록")
    
    # 검사자 등록 폼
    with st.form(key="inspector_form"):
        inspector_id = st.text_input("아이디", key="new_inspector_id")
        name = st.text_input("이름", key="new_inspector_name")
        department = st.selectbox("부서", options=["", "관리부", "생산부", "품질부"], key="new_inspector_dept")
        process = st.selectbox("공정", options=["", "관리", "선반", "밀링", "연삭"], key="new_inspector_process")
        status = st.selectbox("상태", options=["활성", "비활성", "휴면"], index=0, key="new_inspector_status")
        
        # 제출 버튼
        submit = st.form_submit_button("검사자 등록")
        
        if submit:
            if not inspector_id or not name or not department or not process:
                st.error("모든 필드를 입력해주세요.")
            else:
                # 중복 ID 확인
                existing_ids = [insp["id"] for insp in st.session_state.inspectors_data]
                if inspector_id in existing_ids:
                    st.error(f"'{inspector_id}' ID가 이미 존재합니다. 다른 ID를 사용해주세요.")
                else:
                    # 새 검사자 추가 (베트남 시간대 기준)
                    current_date = get_vietnam_date().strftime("%Y-%m-%d")
                    
                    new_inspector = {
                        "id": inspector_id,
                        "name": name,
                        "department": department,
                        "process": process,
                        "created_at": current_date,
                        "last_login": f"{current_date} 00:00:00",
                        "status": status
                    }
                    
                    st.session_state.inspectors_data.append(new_inspector)
                    st.success(f"검사자 '{name}'이(가) 등록되었습니다.")
                    
                    # 폼 리셋을 위한 키 생성
                    st.session_state.form_submitted = True
                    st.rerun()

def show_inspector_statistics():
    """검사자 통계 페이지"""
    st.header("검사자 통계")
    
    # 검사자 데이터로 DataFrame 생성
    if st.session_state.inspectors_data:
        df = pd.DataFrame(st.session_state.inspectors_data)
        
        # 부서별 검사자 수
        st.subheader("부서별 검사자 수")
        dept_counts = df["department"].value_counts().reset_index()
        dept_counts.columns = ["부서", "검사자 수"]
        
        if not dept_counts.empty:
            st.bar_chart(dept_counts, x="부서", y="검사자 수")
            st.table(dept_counts)
        else:
            st.info("부서별 데이터가 없습니다.")
        
        # 공정별 검사자 수
        st.subheader("공정별 검사자 수")
        process_counts = df["process"].value_counts().reset_index()
        process_counts.columns = ["공정", "검사자 수"]
        
        if not process_counts.empty:
            st.bar_chart(process_counts, x="공정", y="검사자 수")
            st.table(process_counts)
        else:
            st.info("공정별 데이터가 없습니다.")
        
        # 상태별 검사자 수
        st.subheader("상태별 검사자 수")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["상태", "검사자 수"]
        
        if not status_counts.empty:
            st.bar_chart(status_counts, x="상태", y="검사자 수")
            st.table(status_counts)
        else:
            st.info("상태별 데이터가 없습니다.")
    else:
        st.info("검사자 데이터가 없습니다.")

