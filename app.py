import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
import io
import re

# 페이지 설정
st.set_page_config(
    page_title="QC KPI 시스템",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐시 관련 설정 (서버 시작 시 캐시 완전히 비우기)
st.cache_data.clear()
st.cache_resource.clear()

# React 오류 방지를 위한 추가 설정
try:
    if 'cache_cleared' not in st.session_state:
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.cache_cleared = True
except:
    pass

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = "종합 대시보드"

# 모듈 가져오기
from pages.dashboard import show_dashboard
from pages.inspection_crud import show_inspection_crud
from pages.item_management import show_production_model_management
from pages.inspector_crud import show_inspector_crud
from pages.user_crud import show_user_crud
from pages.admin_management import show_admin_management
from pages.defect_type_management import show_defect_type_management
from pages.supabase_config import show_supabase_config
from pages.reports import show_reports, show_daily_report, show_weekly_report, show_monthly_report, show_yearly_report, show_dashboard as show_report_dashboard
from utils.supabase_client import get_supabase_client
import hashlib
import bcrypt

# .env 파일에서 환경 변수 로드 (강화된 버전)
try:
    # 여러 경로에서 .env 파일 로드 시도
    possible_env_paths = [
        '.env',
        'C:/CURSOR/QC_KPI/.env',
        os.path.join(os.getcwd(), '.env'),
        os.path.expanduser('~/.streamlit/.env')
    ]
    
    env_loaded = False
    for env_path in possible_env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            env_loaded = True
            break
    
    # 환경변수 값 확인
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    
    # .env 파일이 없거나 비어있으면 기본값 설정
    if not SUPABASE_URL or SUPABASE_URL == "your_supabase_url":
        os.environ["SUPABASE_URL"] = "your_supabase_url"
    if not SUPABASE_KEY or SUPABASE_KEY == "your_supabase_key":
        os.environ["SUPABASE_KEY"] = "your_supabase_key"
    
    # 디버그 정보 (필요시 활성화)
    if False:  # 디버그 모드 비활성화
        st.sidebar.write(f"🔧 ENV 로드됨: {env_loaded}")
        st.sidebar.write(f"🔧 SUPABASE_URL: {bool(SUPABASE_URL and SUPABASE_URL != 'your_supabase_url')}")
        st.sidebar.write(f"🔧 SUPABASE_KEY: {bool(SUPABASE_KEY and SUPABASE_KEY != 'your_supabase_key')}")
        st.sidebar.write(f"🔧 실제 URL: {SUPABASE_URL[:50]}..." if SUPABASE_URL else "URL 없음")
        st.sidebar.write(f"🔧 실제 KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "KEY 없음")
    
except Exception as e:
    st.error(f"환경 변수 로드 중 오류 발생: {str(e)}")
    
# 인증되지 않은 경우 로그인 화면 표시
if not st.session_state.authenticated:
    st.title("🏭 QC KPI 시스템")
    st.subheader("로그인")
    
    with st.form("login_form"):
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        submit_button = st.form_submit_button("로그인")
        
        if submit_button:
            if email and password:
                # 실제 데이터베이스 검증
                try:
                    supabase = get_supabase_client()
                    if supabase:
                        # users 테이블에서 먼저 확인
                        response = supabase.table('users').select('*').eq('email', email).execute()
                        
                        # users 테이블에 없으면 admins 테이블 확인
                        if not response.data:
                            response = supabase.table('admins').select('*').eq('email', email).execute()
                        
                        if response.data:
                            user_data = response.data[0]
                            
                            # 비밀번호 검증
                            password_valid = False
                            
                            # SHA256 해시 비교
                            if user_data.get('password_hash'):
                                input_hash = hashlib.sha256(password.encode()).hexdigest()
                                if user_data.get('password_hash') == input_hash:
                                    password_valid = True
                            
                            # 평문 비밀번호 비교 (개발용)
                            elif user_data.get('password') == password:
                                password_valid = True
                            
                            if password_valid and user_data.get('is_active', True):
                                st.session_state.authenticated = True
                                st.session_state.user_name = user_data.get('name', '사용자')
                                st.session_state.user_role = user_data.get('role', 'user')
                                st.success("로그인 성공!")
                                st.rerun()
                            else:
                                st.error("이메일 또는 비밀번호가 올바르지 않습니다.")
                        else:
                            st.error("이메일 또는 비밀번호가 올바르지 않습니다.")
                    else:
                        # Supabase 연결 실패 시 기본 테스트 계정
                        if email == "admin@company.com" and password == "admin123":
                            st.session_state.authenticated = True
                            st.session_state.user_name = "관리자"
                            st.session_state.user_role = "admin"  # "관리자" -> "admin"으로 변경
                            st.success("로그인 성공!")
                            st.rerun()
                        elif email == "user@company.com" and password == "user123":
                            st.session_state.authenticated = True
                            st.session_state.user_name = "사용자"
                            st.session_state.user_role = "user"  # "사용자" -> "user"로 변경
                            st.success("로그인 성공!")
                            st.rerun()
                        else:
                            st.error("이메일 또는 비밀번호가 잘못되었습니다.")
                
                except Exception as e:
                    st.error(f"로그인 중 오류 발생: {str(e)}")
                    # 오류 시 기본 테스트 계정으로 fallback
                    if email == "admin@company.com" and password == "admin123":
                        st.session_state.authenticated = True
                        st.session_state.user_name = "관리자"
                        st.session_state.user_role = "admin"  # "관리자" -> "admin"으로 변경
                        st.success("로그인 성공!")
                        st.rerun()
                    else:
                        st.error("이메일 또는 비밀번호가 잘못되었습니다.")
            else:
                st.error("이메일과 비밀번호를 모두 입력해주세요.")
    
    # 테스트 계정 안내
    st.info("""
    **테스트 계정:**
    - 관리자: admin@company.com / admin123
    - 사용자: user@company.com / user123
    """)
    
else:
    # 로그인 후 화면
    st.sidebar.title(f"환영합니다, {st.session_state.user_name}")
    st.sidebar.caption(f"권한: {st.session_state.user_role}")
    
    # 세션 상태에 리포트 설정 초기화
    if "report_end_date" not in st.session_state:
        st.session_state.report_end_date = datetime.now().date()
    if "report_model" not in st.session_state:
        st.session_state.report_model = "모든 모델"
    if "report_chart_type" not in st.session_state:
        st.session_state.report_chart_type = "라인 차트"
    
    # 사이드바 카테고리 및 메뉴
    st.sidebar.markdown("### 메뉴")
    
    # 관리자 메뉴 (admin, superadmin, 관리자 역할 모두 지원)
    if st.session_state.user_role in ["admin", "superadmin", "관리자"]:
        with st.sidebar.expander("⚙️ 관리자 메뉴", expanded=True):
            admin_cols = st.columns(1)
            if admin_cols[0].button("👥 사용자 관리", key="user_crud", use_container_width=True):
                st.session_state.selected_menu = "사용자 관리"
                st.rerun()
            if admin_cols[0].button("👨‍💼 관리자 관리", key="admin_mgmt", use_container_width=True):
                st.session_state.selected_menu = "관리자 관리"
                st.rerun()
            if admin_cols[0].button("👷 검사자 등록 및 관리", key="inspector_mgmt", use_container_width=True):
                st.session_state.selected_menu = "검사자 등록 및 관리"
                st.rerun()
            if admin_cols[0].button("🏭 생산모델 관리", key="model_mgmt", use_container_width=True):
                st.session_state.selected_menu = "생산모델 관리"
                st.rerun()
            if admin_cols[0].button("📋 불량 유형 관리", key="defect_type_mgmt", use_container_width=True):
                st.session_state.selected_menu = "불량 유형 관리"
                st.rerun()
            if admin_cols[0].button("🔧 Supabase 설정", key="supabase_config", use_container_width=True):
                st.session_state.selected_menu = "Supabase 설정"
                st.rerun()
    
    # 사용자 메뉴
    with st.sidebar.expander("📋 사용자 메뉴", expanded=True):
        user_cols = st.columns(1)
        if user_cols[0].button("📝 검사 데이터 입력", key="inspection_input", use_container_width=True):
            st.session_state.selected_menu = "검사 데이터 입력"
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
        show_inspection_crud()
        
    elif menu == "불량 유형 관리":
        show_defect_type_management()
        
    elif menu == "검사자 등록 및 관리":
        show_inspector_crud()
        
    elif menu == "보고서":
        show_reports()
        
    elif menu == "사용자 관리":
        show_user_crud()
        
    elif menu == "관리자 관리":
        show_admin_management()
        
    elif menu == "Supabase 설정":
        show_supabase_config()
        
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