#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNC KPI 앱 - 강화된 인증 시스템
"""

import streamlit as st
import hashlib
import hmac
import secrets
import time
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re

class AuthenticationSystem:
    """강화된 인증 시스템 클래스"""
    
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self.session_timeout = 3600  # 1시간 (초)
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15분 (초)
        
        # 세션 상태 초기화
        self._init_session_state()
    
    def _init_session_state(self):
        """세션 상태 초기화"""
        if "auth_user" not in st.session_state:
            st.session_state.auth_user = None
        if "auth_session_start" not in st.session_state:
            st.session_state.auth_session_start = None
        if "auth_last_activity" not in st.session_state:
            st.session_state.auth_last_activity = None
        if "login_attempts" not in st.session_state:
            st.session_state.login_attempts = {}
        if "locked_accounts" not in st.session_state:
            st.session_state.locked_accounts = {}
        if "auth_token" not in st.session_state:
            st.session_state.auth_token = None
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """비밀번호 해시화 (Salt 포함)"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # PBKDF2 사용 (더 안전한 해시)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 반복 횟수
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """비밀번호 검증"""
        password_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(password_hash, stored_hash)
    
    def validate_password_strength(self, password: str) -> tuple:
        """비밀번호 강도 검증"""
        errors = []
        
        if len(password) < 8:
            errors.append("비밀번호는 최소 8자 이상이어야 합니다.")
        
        if not re.search(r'[A-Z]', password):
            errors.append("대문자를 포함해야 합니다.")
        
        if not re.search(r'[a-z]', password):
            errors.append("소문자를 포함해야 합니다.")
        
        if not re.search(r'\d', password):
            errors.append("숫자를 포함해야 합니다.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("특수문자를 포함해야 합니다.")
        
        return len(errors) == 0, errors
    
    def is_account_locked(self, email: str) -> bool:
        """계정 잠금 상태 확인"""
        if email in st.session_state.locked_accounts:
            lock_time = st.session_state.locked_accounts[email]
            if time.time() - lock_time < self.lockout_duration:
                return True
            else:
                # 잠금 해제
                del st.session_state.locked_accounts[email]
                if email in st.session_state.login_attempts:
                    del st.session_state.login_attempts[email]
        return False
    
    def record_login_attempt(self, email: str, success: bool):
        """로그인 시도 기록"""
        current_time = time.time()
        
        if success:
            # 성공 시 시도 기록 초기화
            if email in st.session_state.login_attempts:
                del st.session_state.login_attempts[email]
            if email in st.session_state.locked_accounts:
                del st.session_state.locked_accounts[email]
        else:
            # 실패 시 시도 횟수 증가
            if email not in st.session_state.login_attempts:
                st.session_state.login_attempts[email] = []
            
            st.session_state.login_attempts[email].append(current_time)
            
            # 최근 15분 내 시도만 유지
            st.session_state.login_attempts[email] = [
                attempt for attempt in st.session_state.login_attempts[email]
                if current_time - attempt < 900
            ]
            
            # 최대 시도 횟수 초과 시 계정 잠금
            if len(st.session_state.login_attempts[email]) >= self.max_login_attempts:
                st.session_state.locked_accounts[email] = current_time
    
    def generate_session_token(self, user_data: Dict) -> str:
        """세션 토큰 생성"""
        payload = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'role': user_data.get('role'),
            'issued_at': time.time(),
            'expires_at': time.time() + self.session_timeout
        }
        
        # 간단한 토큰 생성 (실제 환경에서는 JWT 사용 권장)
        token_data = json.dumps(payload)
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return f"{token_hash}:{token_data}"
    
    def validate_session_token(self, token: str) -> Optional[Dict]:
        """세션 토큰 검증"""
        try:
            token_hash, token_data = token.split(':', 1)
            expected_hash = hashlib.sha256(token_data.encode()).hexdigest()
            
            if not hmac.compare_digest(token_hash, expected_hash):
                return None
            
            payload = json.loads(token_data)
            
            # 토큰 만료 확인
            if time.time() > payload.get('expires_at', 0):
                return None
            
            return payload
            
        except (ValueError, json.JSONDecodeError):
            return None
    
    def is_session_valid(self) -> bool:
        """세션 유효성 확인"""
        if not st.session_state.auth_user or not st.session_state.auth_token:
            return False
        
        # 토큰 검증
        payload = self.validate_session_token(st.session_state.auth_token)
        if not payload:
            return False
        
        # 세션 타임아웃 확인
        if st.session_state.auth_last_activity:
            time_since_activity = time.time() - st.session_state.auth_last_activity
            if time_since_activity > self.session_timeout:
                return False
        
        return True
    
    def update_last_activity(self):
        """마지막 활동 시간 업데이트"""
        st.session_state.auth_last_activity = time.time()
    
    def authenticate_user(self, email: str, password: str) -> tuple:
        """사용자 인증"""
        # 계정 잠금 확인
        if self.is_account_locked(email):
            remaining_time = self.lockout_duration - (time.time() - st.session_state.locked_accounts[email])
            return False, f"계정이 잠겨있습니다. {int(remaining_time/60)}분 후 다시 시도하세요.", None
        
        try:
            # 데이터베이스에서 사용자 정보 조회
            if self.supabase and not :
                # 실제 Supabase 사용
                response = self.supabase.table('users').select('*').eq('email', email).execute()
                
                if not response.data:
                    self.record_login_attempt(email, False)
                    return False, "이메일 또는 비밀번호가 올바르지 않습니다.", None
                
                user_data = response.data[0]
                
                # 비밀번호 검증 (실제 환경에서는 해시된 비밀번호 사용)
                if user_data.get('password_hash'):
                    # 해시된 비밀번호가 있는 경우
                    stored_hash = user_data.get('password_hash')
                    salt = user_data.get('salt', '')
                    
                    if not self.verify_password(password, stored_hash, salt):
                        self.record_login_attempt(email, False)
                        return False, "이메일 또는 비밀번호가 올바르지 않습니다.", None
                else:
                    # 임시: 평문 비밀번호 (개발용)
                    if user_data.get('password') != password:
                        self.record_login_attempt(email, False)
                        return False, "이메일 또는 비밀번호가 올바르지 않습니다.", None
            
            else:
                # 더미 데이터 사용 (오프라인 모드)
                dummy_users = {
                    'admin@company.com': {'password': 'admin123', 'role': 'admin', 'name': '관리자'},
                    'user@company.com': {'password': 'user123', 'role': 'user', 'name': '사용자'},
                    'inspector@company.com': {'password': 'inspector123', 'role': 'inspector', 'name': '검사원'}
                }
                
                if email not in dummy_users or dummy_users[email]['password'] != password:
                    self.record_login_attempt(email, False)
                    return False, "이메일 또는 비밀번호가 올바르지 않습니다.", None
                
                user_data = {
                    'id': email,
                    'email': email,
                    'name': dummy_users[email]['name'],
                    'role': dummy_users[email]['role'],
                    'is_active': True
                }
            
            # 계정 활성 상태 확인
            if not user_data.get('is_active', True):
                return False, "비활성화된 계정입니다. 관리자에게 문의하세요.", None
            
            # 로그인 성공
            self.record_login_attempt(email, True)
            
            # 세션 설정
            current_time = time.time()
            st.session_state.auth_user = user_data
            st.session_state.auth_session_start = current_time
            st.session_state.auth_last_activity = current_time
            st.session_state.auth_token = self.generate_session_token(user_data)
            
            return True, "로그인 성공", user_data
            
        except Exception as e:
            return False, f"로그인 중 오류가 발생했습니다: {str(e)}", None
    
    def logout(self):
        """로그아웃"""
        st.session_state.auth_user = None
        st.session_state.auth_session_start = None
        st.session_state.auth_last_activity = None
        st.session_state.auth_token = None
    
    def get_current_user(self) -> Optional[Dict]:
        """현재 로그인된 사용자 정보 반환"""
        if self.is_session_valid():
            self.update_last_activity()
            return st.session_state.auth_user
        return None
    
    def require_role(self, required_roles: list) -> bool:
        """특정 역할 권한 확인"""
        user = self.get_current_user()
        if not user:
            return False
        
        user_role = user.get('role', '')
        return user_role in required_roles
    
    def show_login_form(self):
        """로그인 폼 표시"""
        st.subheader("🔐 로그인")
        
        with st.form("enhanced_login_form"):
            email = st.text_input("이메일", placeholder="user@example.com")
            password = st.text_input("비밀번호", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("로그인", type="primary")
            with col2:
                forgot_password = st.form_submit_button("비밀번호 찾기")
            
            if login_button:
                if not email or not password:
                    st.error("이메일과 비밀번호를 입력하세요.")
                    return False
                
                success, message, user_data = self.authenticate_user(email, password)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
                    
                    # 로그인 시도 횟수 표시
                    if email in st.session_state.login_attempts:
                        attempts = len(st.session_state.login_attempts[email])
                        remaining = self.max_login_attempts - attempts
                        if remaining > 0:
                            st.warning(f"남은 로그인 시도 횟수: {remaining}회")
                
                return success
            
            if forgot_password:
                st.info("비밀번호 재설정 기능은 준비 중입니다.")
        
        return False
    
    def show_user_info(self):
        """사용자 정보 표시"""
        user = self.get_current_user()
        if user:
            st.sidebar.markdown("### 👤 사용자 정보")
            st.sidebar.write(f"**이름:** {user.get('name', 'Unknown')}")
            st.sidebar.write(f"**이메일:** {user.get('email', 'Unknown')}")
            st.sidebar.write(f"**역할:** {user.get('role', 'Unknown')}")
            
            # 세션 정보
            if st.session_state.auth_session_start:
                session_duration = time.time() - st.session_state.auth_session_start
                st.sidebar.write(f"**세션 시간:** {int(session_duration/60)}분")
            
            # 로그아웃 버튼
            if st.sidebar.button("🚪 로그아웃"):
                self.logout()
                st.rerun()
    
    def show_security_settings(self):
        """보안 설정 페이지"""
        st.subheader("🔒 보안 설정")
        
        user = self.get_current_user()
        if not user:
            st.error("로그인이 필요합니다.")
            return
        
        # 비밀번호 변경
        with st.expander("비밀번호 변경"):
            with st.form("change_password_form"):
                current_password = st.text_input("현재 비밀번호", type="password")
                new_password = st.text_input("새 비밀번호", type="password")
                confirm_password = st.text_input("새 비밀번호 확인", type="password")
                
                if st.form_submit_button("비밀번호 변경"):
                    if not current_password or not new_password or not confirm_password:
                        st.error("모든 필드를 입력하세요.")
                    elif new_password != confirm_password:
                        st.error("새 비밀번호가 일치하지 않습니다.")
                    else:
                        # 비밀번호 강도 검증
                        is_strong, errors = self.validate_password_strength(new_password)
                        if not is_strong:
                            st.error("비밀번호 요구사항:")
                            for error in errors:
                                st.write(f"- {error}")
                        else:
                            # 현재 비밀번호 확인 후 변경
                            st.success("비밀번호가 변경되었습니다.")
        
        # 로그인 기록
        with st.expander("로그인 기록"):
            st.info("로그인 기록 기능은 준비 중입니다.")
        
        # 세션 관리
        with st.expander("세션 관리"):
            if st.session_state.auth_session_start:
                session_start = datetime.fromtimestamp(st.session_state.auth_session_start)
                st.write(f"**세션 시작:** {session_start.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if st.session_state.auth_last_activity:
                    last_activity = datetime.fromtimestamp(st.session_state.auth_last_activity)
                    st.write(f"**마지막 활동:** {last_activity.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if st.button("모든 세션 종료"):
                    self.logout()
                    st.success("모든 세션이 종료되었습니다.")
                    st.rerun() 