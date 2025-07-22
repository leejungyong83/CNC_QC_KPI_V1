import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import io
import re

# UI 컴포넌트 import
try:
    from utils.ui_components import apply_global_styles, std_components
except ImportError:
    print("⚠️ UI 컴포넌트를 불러올 수 없습니다.")
    def apply_global_styles():
        pass
    class std_components:
        @staticmethod
        def page_header(title, subtitle=""):
            st.title(title)
            if subtitle:
                st.markdown(subtitle)

# 모바일 감지 및 페이지 설정
is_mobile_mode = st.session_state.get('is_mobile', False)

if is_mobile_mode:
    st.set_page_config(
        page_title="CNC QC Mobile",
        page_icon="📱", 
        layout="centered",
        initial_sidebar_state="collapsed"
    )
else:
    st.set_page_config(
        page_title="QC KPI 시스템",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# 개발자 도구 및 디버그 메뉴 숨김 처리
st.markdown("""
<style>
    /* Streamlit 개발자 도구 및 페이지 목록 숨김 */
    .stSidebar .stSelectbox,
    .stSidebar .element-container:first-child,
    .css-1d391kg,
    .css-1y4p8pa,
    .css-17lntkn,
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    .stSidebar > div:first-child > div:first-child {
        display: none !important;
    }
    
    /* 상단 툴바 관련 요소 숨김 */
    .stDeployButton,
    .stDecoration,
    header[data-testid="stHeader"],
    .stToolbar {
        display: none !important;
    }
    
    /* 사이드바 상단 여백 조정 */
    .stSidebar .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* 메인 영역 상단 여백 조정 */
    .stAppViewContainer > .main .block-container {
        padding-top: 1rem !important;
    }
    
    /* 사이드바 버튼 간격 최적화 */
    .stSidebar .stButton > button {
        margin-bottom: 0.3rem !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.85rem !important;
        white-space: nowrap !important;
    }
    
    /* 사이드바 expander 여백 최적화 */
    .stSidebar .streamlit-expanderHeader {
        padding: 0.3rem 0.5rem !important;
    }
    
    /* 사이드바 제목 및 캡션 여백 조정 */
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 캐시 관련 설정 (안전한 캐시 관리)
try:
    # 개발 환경에서만 캐시 클리어
    if os.environ.get('STREAMLIT_CLOUD') != 'true':
        st.cache_data.clear()
        st.cache_resource.clear()
except Exception:
    pass

# 세션별 캐시 관리
try:
    if 'cache_cleared' not in st.session_state:
        st.session_state.cache_cleared = True
except Exception:
    pass

# 전역 스타일 적용
try:
    apply_global_styles()
except Exception as e:
    st.error(f"스타일 로딩 실패: {str(e)}")
    # 기본 스타일 적용
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

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
from pages.inspection_input import show_inspection_input
from pages.item_management import show_production_model_management
from pages.inspector_crud import show_inspector_crud
from pages.user_crud import show_user_crud
from pages.admin_management import show_admin_management
from pages.defect_type_management import show_defect_type_management
from pages.supabase_config import show_supabase_config
from pages.reports import show_reports, show_dashboard, show_daily_report, show_weekly_report, show_monthly_report, show_defect_analysis, get_inspection_data
from utils.supabase_client import get_supabase_client
import hashlib
import bcrypt

# Streamlit Cloud 환경변수 로드 (secrets.toml 우선)
try:
    # Streamlit Cloud에서는 st.secrets 사용
    if hasattr(st, 'secrets'):
        SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
        SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
        
        if SUPABASE_URL:
            os.environ["SUPABASE_URL"] = SUPABASE_URL
        if SUPABASE_KEY:
            os.environ["SUPABASE_KEY"] = SUPABASE_KEY
    
    # 로컬 환경에서는 .env 파일 사용
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        load_dotenv('.env', override=True)
    
    # 환경변수 최종 확인
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    
    # 기본값 설정 (개발용)
    if not SUPABASE_URL or SUPABASE_URL == "your_supabase_url":
        os.environ["SUPABASE_URL"] = "your_supabase_url"
    if not SUPABASE_KEY or SUPABASE_KEY == "your_supabase_key":
        os.environ["SUPABASE_KEY"] = "your_supabase_key"
    
except Exception as e:
    st.error(f"환경 변수 로드 중 오류 발생: {str(e)}")
    # Fallback to default values for testing
    os.environ["SUPABASE_URL"] = "your_supabase_url"
    os.environ["SUPABASE_KEY"] = "your_supabase_key"
    
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
                                st.session_state.selected_menu = "종합 대시보드"  # 로그인 시 종합 대시보드로 이동
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
                            st.session_state.selected_menu = "종합 대시보드"  # 로그인 시 종합 대시보드로 이동
                            st.success("로그인 성공!")
                            st.rerun()
                        elif email == "user@company.com" and password == "user123":
                            st.session_state.authenticated = True
                            st.session_state.user_name = "사용자"
                            st.session_state.user_role = "user"  # "사용자" -> "user"로 변경
                            st.session_state.selected_menu = "종합 대시보드"  # 로그인 시 종합 대시보드로 이동
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
                        st.session_state.selected_menu = "종합 대시보드"  # 로그인 시 종합 대시보드로 이동
                        st.success("로그인 성공!")
                        st.rerun()
                    else:
                        st.error("이메일 또는 비밀번호가 잘못되었습니다.")
            else:
                st.error("이메일과 비밀번호를 모두 입력해주세요.")
    
    # 테스트 계정 안내 숨김 처리 (사용자 요청)
    
else:
    # 로그인 후 화면
    st.sidebar.title(f"환영합니다, {st.session_state.user_name}")
    st.sidebar.caption(f"권한: {st.session_state.user_role}")
    

    
    # 사이드바 카테고리 및 메뉴
    st.sidebar.markdown("### 메뉴")
    
    # 관리자 메뉴 (admin, superadmin, 관리자 역할 모두 지원)
    if st.session_state.user_role in ["admin", "superadmin", "관리자"]:
        with st.sidebar.expander("⚙️ 관리자 메뉴", expanded=True):
            if st.button("👥 사용자관리", key="user_crud", use_container_width=True):
                st.session_state.selected_menu = "사용자 관리"
                st.rerun()
            if st.button("👨‍💼 관리자관리", key="admin_mgmt", use_container_width=True):
                st.session_state.selected_menu = "관리자 관리"
                st.rerun()
            if st.button("👷 검사자관리", key="inspector_mgmt", use_container_width=True):
                st.session_state.selected_menu = "검사자 등록 및 관리"
                st.rerun()
            if st.button("🏭 생산모델관리", key="model_mgmt", use_container_width=True):
                st.session_state.selected_menu = "생산모델 관리"
                st.rerun()
            if st.button("📋 불량유형관리", key="defect_type_mgmt", use_container_width=True):
                st.session_state.selected_menu = "불량 유형 관리"
                st.rerun()
            if st.button("🔧 Supabase설정", key="supabase_config", use_container_width=True):
                st.session_state.selected_menu = "Supabase 설정"
                st.rerun()
            if st.button("🛠️ 시스템상태", key="system_health", use_container_width=True):
                st.session_state.selected_menu = "시스템 상태"
                st.rerun()
            if st.button("⚡ 성능모니터링", key="performance_monitor", use_container_width=True):
                st.session_state.selected_menu = "성능 모니터링"
                st.rerun()
            if st.button("📋 자동보고서", key="auto_reports", use_container_width=True):
                st.session_state.selected_menu = "자동 보고서"
                st.rerun()
            if st.button("📈 고급분석", key="advanced_analytics", use_container_width=True):
                st.session_state.selected_menu = "고급 분석"
                st.rerun()
    
    # 사용자 메뉴 (expander에서 제거하여 직접 노출) - 2024-01-20 수정
    st.sidebar.markdown("### 📝 데이터입력")
    if st.sidebar.button("📝 검사데이터입력", key="inspection_input", use_container_width=True):
        st.session_state.selected_menu = "검사 데이터 입력"
        st.rerun()
    
    # 리포트 메뉴 (개별 메뉴로 노출)
    st.sidebar.markdown("### 📊 리포트")
    if st.sidebar.button("📈 종합대시보드", key="dashboard", use_container_width=True):
        st.session_state.selected_menu = "종합 대시보드"
        st.rerun()
    if st.sidebar.button("📅 일별분석", key="daily_analysis", use_container_width=True):
        st.session_state.selected_menu = "일별 분석"
        st.rerun()
    if st.sidebar.button("📆 주별분석", key="weekly_analysis", use_container_width=True):
        st.session_state.selected_menu = "주별 분석"
        st.rerun()
    if st.sidebar.button("📊 월별분석", key="monthly_analysis", use_container_width=True):
        st.session_state.selected_menu = "월별 분석"
        st.rerun()
    if st.sidebar.button("🔍 불량분석", key="defect_analysis", use_container_width=True):
        st.session_state.selected_menu = "불량 분석"
        st.rerun()
    
    # 알림 시스템 (새로 추가)
    st.sidebar.markdown("### 🔔 알림")
    
    # 사이드바 알림 요약 표시
    try:
        from utils.notification_system import show_notification_sidebar
        notification_count = show_notification_sidebar()
    except Exception:
        notification_count = 0
    
    if st.sidebar.button("🔔 알림센터", key="notification_center", use_container_width=True):
        st.session_state.selected_menu = "알림 센터"
        st.rerun()
    
    # 파일 관리 (새로 추가)
    st.sidebar.markdown("### 📁 파일")
    if st.sidebar.button("📥 파일관리", key="file_management", use_container_width=True):
        st.session_state.selected_menu = "파일 관리"
        st.rerun()
    
    # 모바일 모드 전환 (새로 추가)
    st.sidebar.markdown("### 📱 모바일")
    if st.sidebar.button("📱 모바일 모드", key="mobile_mode", use_container_width=True):
        st.session_state.is_mobile = True
        st.session_state.selected_menu = "모바일 모드"
        st.rerun()
    

    
    # 로그아웃 버튼
    if st.sidebar.button("🚪 로그아웃"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.session_state.selected_menu = "종합 대시보드"  # 로그아웃 시 초기 메뉴 설정
        st.rerun()
    
    # 선택한 메뉴에 따른 화면 표시
    menu = st.session_state.selected_menu
    
    # 공통 필터 파라미터 설정 (리포트용)
    today = datetime.now().date()
    filter_params = {
        'start_date': today - timedelta(days=30),
        'end_date': today,
        'model': "전체 모델",
        'inspector': "전체 검사자",
        'process': "전체 공정"
    }
    
    if menu == "종합 대시보드":
        show_dashboard(filter_params)
        
    elif menu == "일별 분석":
        show_daily_report(filter_params)
        
    elif menu == "주별 분석":
        show_weekly_report(filter_params)
        
    elif menu == "월별 분석":
        show_monthly_report(filter_params)
        
    elif menu == "불량 분석":
        show_defect_analysis(filter_params)
        
    elif menu == "생산모델 관리":
        show_production_model_management()
        
    elif menu == "검사 데이터 입력":
        show_inspection_input()
        
    elif menu == "알림 센터":
        from pages.notifications import show_notifications
        show_notifications()
        
    elif menu == "파일 관리":
        from utils.file_manager import show_file_management
        show_file_management()
        
    elif menu == "모바일 모드":
        from pages.mobile_page import show_mobile_page
        show_mobile_page()
        
    elif menu == "불량 유형 관리":
        show_defect_type_management()
        
    elif menu == "검사자 등록 및 관리":
        show_inspector_crud()
        
    elif menu == "사용자 관리":
        show_user_crud()
        
    elif menu == "관리자 관리":
        show_admin_management()
        
    elif menu == "Supabase 설정":
        show_supabase_config()
        
    elif menu == "시스템 상태":
        from pages.system_health import show_system_health
        show_system_health()
        
    elif menu == "성능 모니터링":
        from pages.performance import show_performance
        show_performance()
        
    elif menu == "자동 보고서":
        from pages.auto_reports import show_auto_reports
        show_auto_reports()
        
    elif menu == "고급 분석":
        from pages.advanced_analytics import show_advanced_analytics
        show_advanced_analytics() 