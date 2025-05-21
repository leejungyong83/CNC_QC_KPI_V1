import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# 캐시 관련 설정 (서버 시작 시 캐시 완전히 비우기)
st.cache_data.clear()
st.cache_resource.clear()

# 모듈 가져오기
from pages.dashboard import show_dashboard
from pages.inspection_input import show_inspection_input
from pages.item_management import show_production_model_management
from pages.defect_management import show_defect_management
from pages.inspector_management import show_inspector_management
from pages.user_management import show_user_management
from pages.reports import show_reports, show_daily_report, show_weekly_report, show_monthly_report, show_yearly_report, show_dashboard as show_report_dashboard

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="CNC 품질 검사 KPI 앱",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시 비우기 (중요 - 페이지 설정 후에도 다시 한번 캐시 비우기)
st.cache_data.clear()
st.cache_resource.clear()

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# 제목
st.title("CNC 품질 검사 KPI 앱")

# 로그인 상태에 따른 화면 표시
if not st.session_state.authenticated:
    # 로그인 화면
    with st.form("login_form"):
        st.subheader("로그인")
        username = st.text_input("사용자 이름")
        password = st.text_input("비밀번호", type="password")
        submit_button = st.form_submit_button("로그인")
        
        if submit_button:
            # 여기서는 간단한 예시로 처리 (실제로는 Supabase 인증 사용 예정)
            if username == "admin" and password == "admin":
                st.session_state.authenticated = True
                st.session_state.user_role = "관리자"
                st.session_state.user_name = username
                st.rerun()
            else:
                st.error("사용자 이름 또는 비밀번호가 올바르지 않습니다.")
else:
    # 로그인 후 화면
    st.sidebar.title(f"환영합니다, {st.session_state.user_name}")
    st.sidebar.caption(f"권한: {st.session_state.user_role}")
    
    # 세션 상태에 현재 선택된 메뉴 저장
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = "종합 대시보드"  # 초기 화면을 종합 대시보드로 변경
    
    # 세션 상태에 리포트 설정 초기화
    if "report_end_date" not in st.session_state:
        st.session_state.report_end_date = datetime.now().date()
    if "report_model" not in st.session_state:
        st.session_state.report_model = "모든 모델"
    if "report_chart_type" not in st.session_state:
        st.session_state.report_chart_type = "라인 차트"
    
    # 사이드바 카테고리 및 메뉴
    st.sidebar.markdown("### 메뉴")
    
    # 관리자 메뉴
    with st.sidebar.expander("⚙️ 관리자 메뉴", expanded=True):
        admin_cols = st.columns(1)
        if admin_cols[0].button("👤 관리자 및 사용자 관리", key="user_mgmt", use_container_width=True):
            st.session_state.selected_menu = "사용자 관리"
            st.rerun()
        if admin_cols[0].button("👷 검사자 등록 및 관리", key="inspector_mgmt", use_container_width=True):
            st.session_state.selected_menu = "검사자 등록 및 관리"
            st.rerun()
        if admin_cols[0].button("🏭 생산모델 관리", key="model_mgmt", use_container_width=True):
            st.session_state.selected_menu = "생산모델 관리"
            st.rerun()
    
    # 사용자 메뉴
    with st.sidebar.expander("📋 사용자 메뉴", expanded=True):
        user_cols = st.columns(1)
        if user_cols[0].button("📝 검사 데이터 입력", key="inspection_input", use_container_width=True):
            st.session_state.selected_menu = "검사 데이터 입력"
            st.rerun()
        if user_cols[0].button("❌ 불량 관리", key="defect_mgmt", use_container_width=True):
            st.session_state.selected_menu = "불량 관리"
            st.rerun()
        if user_cols[0].button("🔧 설비 정보", key="equipment_info", use_container_width=True):
            st.session_state.selected_menu = "설비 정보"
            st.rerun()
    
    # 리포트 메뉴
    with st.sidebar.expander("📊 리포트 메뉴", expanded=True):
        report_cols = st.columns(1)
        if report_cols[0].button("📈 종합 대시보드", key="report_dashboard", use_container_width=True):
            st.session_state.selected_menu = "종합 대시보드"
            st.rerun()
        if report_cols[0].button("📅 일간 리포트", key="daily_report", use_container_width=True):
            st.session_state.selected_menu = "일간 리포트"
            st.rerun()
        if report_cols[0].button("📆 주간 리포트", key="weekly_report", use_container_width=True):
            st.session_state.selected_menu = "주간 리포트"
            st.rerun()
        if report_cols[0].button("📊 월간 리포트", key="monthly_report", use_container_width=True):
            st.session_state.selected_menu = "월간 리포트"
            st.rerun()
        if report_cols[0].button("📋 연간 리포트", key="yearly_report", use_container_width=True):
            st.session_state.selected_menu = "연간 리포트"
            st.rerun()
    
    # 리포트 메뉴 선택 시 리포트 설정 표시
    report_menus = ["종합 대시보드", "일간 리포트", "주간 리포트", "월간 리포트", "연간 리포트"]
    if st.session_state.selected_menu in report_menus:
        with st.sidebar:
            st.markdown("---")
            st.subheader("리포트 설정")
            # 종료일 설정
            end_date = st.date_input("종료일", value=st.session_state.report_end_date, key="report_date_input")
            st.session_state.report_end_date = end_date
            
            # 모델 선택
            model = st.selectbox(
                "모델 선택", 
                ["모든 모델", "모델A", "모델B", "모델C", "모델D", "모델E"],
                index=["모든 모델", "모델A", "모델B", "모델C", "모델D", "모델E"].index(st.session_state.report_model),
                key="report_model_select"
            )
            st.session_state.report_model = model
            
            # 차트 타입 선택
            chart_type = st.selectbox(
                "차트 타입",
                ["라인 차트", "바 차트", "파이 차트", "복합 차트"],
                index=["라인 차트", "바 차트", "파이 차트", "복합 차트"].index(st.session_state.report_chart_type),
                key="report_chart_type_select"
            )
            st.session_state.report_chart_type = chart_type
    
    # 로그아웃 버튼
    if st.sidebar.button("🚪 로그아웃"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.session_state.selected_menu = "종합 대시보드"  # 로그아웃 시 초기 메뉴 설정
        st.rerun()
    
    # 선택한 메뉴에 따른 화면 표시
    menu = st.session_state.selected_menu
    
    if menu == "종합 대시보드":
        st.header("종합 대시보드")
        show_report_dashboard(st.session_state.report_end_date, st.session_state.report_model, st.session_state.report_chart_type)
        
    elif menu == "생산모델 관리":
        show_production_model_management()
        
    elif menu == "검사 데이터 입력":
        show_inspection_input()
        
    elif menu == "불량 관리":
        show_defect_management()
        
    elif menu == "검사자 등록 및 관리":
        show_inspector_management()
        
    elif menu == "보고서":
        show_reports()
        
    elif menu == "설비 정보":
        st.header("설비 정보")
        st.info("이 기능은 개발 중입니다.")
        
    elif menu == "사용자 관리":
        show_user_management()
        
    # 리포트 관련 메뉴
    elif menu == "일간 리포트":
        st.header("일간 리포트")
        show_daily_report(st.session_state.report_end_date, st.session_state.report_model, st.session_state.report_chart_type)
        
    elif menu == "주간 리포트":
        st.header("주간 리포트")
        show_weekly_report(st.session_state.report_end_date, st.session_state.report_model, st.session_state.report_chart_type)
        
    elif menu == "월간 리포트":
        st.header("월간 리포트")
        show_monthly_report(st.session_state.report_end_date, st.session_state.report_model, st.session_state.report_chart_type)
        
    elif menu == "연간 리포트":
        st.header("연간 리포트")
        show_yearly_report(st.session_state.report_end_date, st.session_state.report_model, st.session_state.report_chart_type) 