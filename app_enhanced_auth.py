#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNC KPI 앱 - 강화된 인증 시스템 적용 버전
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# 강화된 인증 시스템 import
from utils.auth_system import AuthenticationSystem
from utils.two_factor_auth import TwoFactorAuth
from utils.supabase_client import get_supabase_client

# 기존 페이지들 import
from pages.dashboard import show_dashboard
from pages.inspection_input import show_inspection_input
from pages.inspection_crud import show_inspection_crud
from pages.inspector_crud import show_inspector_crud
from pages.user_crud import show_user_crud
from pages.admin_management import show_admin_management
from pages.item_management import show_production_model_management
from pages.defect_type_management import show_defect_type_management
from pages.reports import show_reports
from pages.supabase_config import show_supabase_config
from pages.inspector_management import show_inspector_management

# 페이지 설정
st.set_page_config(
    page_title="CNC 품질 검사 KPI 앱 - 강화된 보안",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #f8f9fa;
    }
    .security-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    .warning-badge {
        background-color: #ffc107;
        color: #212529;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """메인 애플리케이션"""
    
    # Supabase 클라이언트 초기화
    supabase = get_supabase_client()
    
    # 인증 시스템 초기화
    auth_system = AuthenticationSystem(supabase)
    two_factor_auth = TwoFactorAuth(supabase)
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🔧 CNC 품질 검사 KPI 앱</h1>
        <p>강화된 보안 시스템 적용 버전</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 현재 사용자 확인
    current_user = auth_system.get_current_user()
    
    if not current_user:
        # 로그인 화면
        show_login_page(auth_system, two_factor_auth)
    else:
        # 2FA 인증 확인
        user_email = current_user.get('email', '')
        
        if two_factor_auth.is_2fa_enabled(user_email):
            if not two_factor_auth.require_2fa_verification(user_email):
                return  # 2FA 인증 대기 중
            else:
                two_factor_auth.mark_2fa_verified(user_email)
        
        # 메인 애플리케이션 화면
        show_main_app(auth_system, two_factor_auth, current_user, supabase)

def show_login_page(auth_system, two_factor_auth):
    """로그인 페이지"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # 보안 기능 안내
        st.markdown("### 🔐 보안 기능")
        st.markdown("""
        - ✅ 강화된 비밀번호 정책
        - ✅ 로그인 시도 제한 (5회)
        - ✅ 계정 잠금 보호 (15분)
        - ✅ 세션 타임아웃 (1시간)
        - ✅ 2단계 인증 지원
        - ✅ 안전한 토큰 관리
        """)
        
        st.markdown("---")
        
        # 로그인 폼
        auth_system.show_login_form()
        
        # 테스트 계정 안내
        with st.expander("🧪 테스트 계정"):
            st.write("**관리자 계정:**")
            st.code("이메일: admin@company.com\n비밀번호: admin123")
            
            st.write("**일반 사용자 계정:**")
            st.code("이메일: user@company.com\n비밀번호: user123")
            
            st.write("**검사원 계정:**")
            st.code("이메일: inspector@company.com\n비밀번호: inspector123")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_main_app(auth_system, two_factor_auth, current_user, supabase):
    """메인 애플리케이션 화면"""
    
    # 사이드바에 사용자 정보 표시
    with st.sidebar:
        # 사용자 정보
        st.markdown("### 👤 사용자 정보")
        user_name = current_user.get('name', 'Unknown')
        user_email = current_user.get('email', 'Unknown')
        user_role = current_user.get('role', 'Unknown')
        
        st.write(f"**이름:** {user_name}")
        st.write(f"**이메일:** {user_email}")
        st.write(f"**역할:** {user_role}")
        
        # 보안 상태 표시
        if two_factor_auth.is_2fa_enabled(user_email):
            st.markdown('<span class="security-badge">🔐 2FA 활성화</span>', unsafe_allow_html=True)
            backup_count = two_factor_auth.get_backup_codes_count(user_email)
            st.write(f"백업 코드: {backup_count}개 남음")
        else:
            st.markdown('<span class="warning-badge">⚠️ 2FA 비활성화</span>', unsafe_allow_html=True)
        
        # 세션 정보
        if st.session_state.auth_session_start:
            session_duration = time.time() - st.session_state.auth_session_start
            st.write(f"**세션 시간:** {int(session_duration/60)}분")
        
        st.markdown("---")
    
    # 메뉴 설정
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = "종합 대시보드"
    
    # 역할별 메뉴 구성
    menu_items = get_menu_items_by_role(user_role)
    
    # 사이드바 메뉴
    with st.sidebar:
        st.markdown("### 📋 메뉴")
        
        for category, items in menu_items.items():
            st.markdown(f"**{category}**")
            for item in items:
                if st.button(item, key=f"menu_{item}", use_container_width=True):
                    st.session_state.selected_menu = item
                    st.rerun()
            st.markdown("")
        
        # 보안 설정 메뉴
        st.markdown("**🔒 보안 설정**")
        if st.button("2단계 인증 설정", key="2fa_settings", use_container_width=True):
            st.session_state.selected_menu = "2단계 인증 설정"
            st.rerun()
        
        if st.button("보안 설정", key="security_settings", use_container_width=True):
            st.session_state.selected_menu = "보안 설정"
            st.rerun()
        
        st.markdown("---")
        
        # 로그아웃 버튼
        if st.button("🚪 로그아웃", type="secondary", use_container_width=True):
            auth_system.logout()
            st.rerun()
    
    # 선택된 메뉴에 따른 페이지 표시
    selected_menu = st.session_state.selected_menu
    
    # 권한 확인
    if not has_permission(user_role, selected_menu):
        st.error("❌ 이 페이지에 접근할 권한이 없습니다.")
        st.info(f"현재 권한: {user_role}")
        return
    
    # 페이지 라우팅
    if selected_menu == "종합 대시보드":
        show_dashboard()
    elif selected_menu == "검사 데이터 입력":
        show_inspection_input(supabase)
    elif selected_menu == "검사실적 관리":
        show_inspection_crud(supabase)
    elif selected_menu == "검사자 관리":
        show_inspector_crud(supabase)
    elif selected_menu == "사용자 관리":
        if auth_system.require_role(['admin', 'superadmin']):
            show_user_crud(supabase)
        else:
            st.error("관리자 권한이 필요합니다.")
    elif selected_menu == "관리자 관리":
        if auth_system.require_role(['superadmin']):
            show_admin_management(supabase)
        else:
            st.error("최고 관리자 권한이 필요합니다.")
    elif selected_menu == "생산모델 관리":
        show_production_model_management(supabase)
    elif selected_menu == "불량유형 관리":
        show_defect_type_management(supabase)
    elif selected_menu == "보고서":
        show_reports()
    elif selected_menu == "Supabase 설정":
        if auth_system.require_role(['admin', 'superadmin']):
            show_supabase_config()
        else:
            st.error("관리자 권한이 필요합니다.")
    elif selected_menu == "검사자 관리 (구)":
        show_inspector_management()
    elif selected_menu == "2단계 인증 설정":
        two_factor_auth.show_2fa_setup(user_email)
    elif selected_menu == "보안 설정":
        auth_system.show_security_settings()
    else:
        st.error("알 수 없는 메뉴입니다.")

def get_menu_items_by_role(user_role):
    """역할별 메뉴 항목 반환"""
    
    base_menus = {
        "📊 대시보드": ["종합 대시보드"],
        "📝 검사 관리": ["검사 데이터 입력", "검사실적 관리"],
        "📋 보고서": ["보고서"]
    }
    
    if user_role in ['inspector', 'user']:
        # 검사원/일반 사용자: 기본 메뉴만
        return base_menus
    
    elif user_role == 'manager':
        # 매니저: 검사자 관리 추가
        base_menus["👥 인력 관리"] = ["검사자 관리"]
        base_menus["🔧 시스템 관리"] = ["생산모델 관리", "불량유형 관리"]
        return base_menus
    
    elif user_role == 'admin':
        # 관리자: 대부분 메뉴 접근
        base_menus["👥 인력 관리"] = ["검사자 관리", "사용자 관리"]
        base_menus["🔧 시스템 관리"] = ["생산모델 관리", "불량유형 관리", "Supabase 설정"]
        base_menus["🔧 레거시"] = ["검사자 관리 (구)"]
        return base_menus
    
    elif user_role == 'superadmin':
        # 최고 관리자: 모든 메뉴 접근
        base_menus["👥 인력 관리"] = ["검사자 관리", "사용자 관리", "관리자 관리"]
        base_menus["🔧 시스템 관리"] = ["생산모델 관리", "불량유형 관리", "Supabase 설정"]
        base_menus["🔧 레거시"] = ["검사자 관리 (구)"]
        return base_menus
    
    else:
        # 알 수 없는 역할: 기본 메뉴만
        return base_menus

def has_permission(user_role, menu_item):
    """메뉴 항목에 대한 권한 확인"""
    
    # 모든 사용자가 접근 가능한 메뉴
    public_menus = [
        "종합 대시보드", "검사 데이터 입력", "검사실적 관리", 
        "보고서", "2단계 인증 설정", "보안 설정"
    ]
    
    if menu_item in public_menus:
        return True
    
    # 검사원/매니저 이상 접근 가능
    inspector_plus_menus = ["검사자 관리", "생산모델 관리", "불량유형 관리"]
    if menu_item in inspector_plus_menus and user_role in ['inspector', 'manager', 'admin', 'superadmin']:
        return True
    
    # 관리자 이상 접근 가능
    admin_menus = ["사용자 관리", "Supabase 설정", "검사자 관리 (구)"]
    if menu_item in admin_menus and user_role in ['admin', 'superadmin']:
        return True
    
    # 최고 관리자만 접근 가능
    superadmin_menus = ["관리자 관리"]
    if menu_item in superadmin_menus and user_role == 'superadmin':
        return True
    
    return False

if __name__ == "__main__":
    main() 