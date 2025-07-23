#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNC KPI 앱 - 2단계 인증(2FA) 시스템
"""

import streamlit as st
import pyotp
import qrcode
import io
import base64
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# 베트남 시간대 유틸리티 import  
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)

class TwoFactorAuth:
    """2단계 인증 시스템 클래스"""
    
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self.app_name = "CNC KPI App"
        self.issuer_name = "CNC Quality Control"
        
        # 세션 상태 초기화
        self._init_session_state()
    
    def _init_session_state(self):
        """세션 상태 초기화"""
        if "totp_secrets" not in st.session_state:
            st.session_state.totp_secrets = {}
        if "backup_codes" not in st.session_state:
            st.session_state.backup_codes = {}
        if "2fa_enabled_users" not in st.session_state:
            st.session_state["2fa_enabled_users"] = set()
        if "pending_2fa_verification" not in st.session_state:
            st.session_state.pending_2fa_verification = {}
    
    def generate_secret_key(self, user_email: str) -> str:
        """사용자별 비밀 키 생성"""
        secret = pyotp.random_base32()
        st.session_state.totp_secrets[user_email] = secret
        return secret
    
    def generate_qr_code(self, user_email: str, secret_key: str) -> str:
        """QR 코드 생성"""
        # TOTP URI 생성
        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
        
        # QR 코드 생성
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # 이미지로 변환
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Base64로 인코딩
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    
    def generate_backup_codes(self, user_email: str, count: int = 10) -> list:
        """백업 코드 생성"""
        backup_codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()  # 8자리 백업 코드
            backup_codes.append(code)
        
        st.session_state.backup_codes[user_email] = backup_codes.copy()
        return backup_codes
    
    def verify_totp_code(self, user_email: str, code: str) -> bool:
        """TOTP 코드 검증"""
        if user_email not in st.session_state.totp_secrets:
            return False
        
        secret = st.session_state.totp_secrets[user_email]
        totp = pyotp.TOTP(secret)
        
        # 시간 허용 오차 (30초 전후)
        return totp.verify(code, valid_window=1)
    
    def verify_backup_code(self, user_email: str, code: str) -> bool:
        """백업 코드 검증 (일회용)"""
        if user_email not in st.session_state.backup_codes:
            return False
        
        backup_codes = st.session_state.backup_codes[user_email]
        code_upper = code.upper().strip()
        
        if code_upper in backup_codes:
            # 사용된 백업 코드 제거
            backup_codes.remove(code_upper)
            st.session_state.backup_codes[user_email] = backup_codes
            return True
        
        return False
    
    def is_2fa_enabled(self, user_email: str) -> bool:
        """2FA 활성화 상태 확인"""
        return user_email in st.session_state["2fa_enabled_users"]
    
    def enable_2fa(self, user_email: str):
        """2FA 활성화"""
        st.session_state["2fa_enabled_users"].add(user_email)
    
    def disable_2fa(self, user_email: str):
        """2FA 비활성화"""
        if user_email in st.session_state["2fa_enabled_users"]:
            st.session_state["2fa_enabled_users"].remove(user_email)
        
        # 관련 데이터 삭제
        if user_email in st.session_state.totp_secrets:
            del st.session_state.totp_secrets[user_email]
        if user_email in st.session_state.backup_codes:
            del st.session_state.backup_codes[user_email]
    
    def show_2fa_setup(self, user_email: str):
        """2FA 설정 페이지"""
        st.subheader("🔐 2단계 인증 설정")
        
        if self.is_2fa_enabled(user_email):
            st.success("✅ 2단계 인증이 활성화되어 있습니다.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 백업 코드 재생성"):
                    backup_codes = self.generate_backup_codes(user_email)
                    st.success("새로운 백업 코드가 생성되었습니다!")
                    
                    st.warning("⚠️ 백업 코드를 안전한 곳에 저장하세요!")
                    for i, code in enumerate(backup_codes, 1):
                        st.code(f"{i:2d}. {code}")
            
            with col2:
                if st.button("❌ 2FA 비활성화", type="secondary"):
                    self.disable_2fa(user_email)
                    st.success("2단계 인증이 비활성화되었습니다.")
                    st.rerun()
        
        else:
            st.info("2단계 인증을 설정하여 계정 보안을 강화하세요.")
            
            if st.button("🔒 2FA 설정 시작"):
                st.session_state.setup_2fa_step = 1
                st.rerun()
            
            # 2FA 설정 단계
            if "setup_2fa_step" in st.session_state:
                self._show_2fa_setup_steps(user_email)
    
    def _show_2fa_setup_steps(self, user_email: str):
        """2FA 설정 단계별 안내"""
        step = st.session_state.get("setup_2fa_step", 1)
        
        if step == 1:
            st.markdown("### 1단계: 인증 앱 설치")
            st.write("다음 중 하나의 인증 앱을 설치하세요:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("📱 **Google Authenticator**")
                st.write("- Android/iOS 지원")
                st.write("- 무료")
            
            with col2:
                st.write("🔐 **Microsoft Authenticator**")
                st.write("- Android/iOS 지원")
                st.write("- 무료")
            
            with col3:
                st.write("🛡️ **Authy**")
                st.write("- 다중 기기 지원")
                st.write("- 백업 기능")
            
            if st.button("다음 단계"):
                st.session_state.setup_2fa_step = 2
                st.rerun()
        
        elif step == 2:
            st.markdown("### 2단계: QR 코드 스캔")
            
            # 비밀 키 생성
            if user_email not in st.session_state.totp_secrets:
                secret_key = self.generate_secret_key(user_email)
            else:
                secret_key = st.session_state.totp_secrets[user_email]
            
            # QR 코드 생성 및 표시
            qr_code_img = self.generate_qr_code(user_email, secret_key)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("인증 앱으로 다음 QR 코드를 스캔하세요:")
                st.markdown(
                    f'<img src="data:image/png;base64,{qr_code_img}" width="200">',
                    unsafe_allow_html=True
                )
            
            with col2:
                st.write("**수동 입력용 키:**")
                st.code(secret_key)
                st.write("QR 코드를 스캔할 수 없는 경우 위 키를 수동으로 입력하세요.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("이전 단계"):
                    st.session_state.setup_2fa_step = 1
                    st.rerun()
            
            with col2:
                if st.button("다음 단계"):
                    st.session_state.setup_2fa_step = 3
                    st.rerun()
        
        elif step == 3:
            st.markdown("### 3단계: 인증 코드 확인")
            
            with st.form("verify_2fa_setup"):
                st.write("인증 앱에서 생성된 6자리 코드를 입력하세요:")
                verification_code = st.text_input(
                    "인증 코드",
                    max_chars=6,
                    placeholder="123456"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("이전 단계"):
                        st.session_state.setup_2fa_step = 2
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("확인"):
                        if self.verify_totp_code(user_email, verification_code):
                            # 2FA 활성화
                            self.enable_2fa(user_email)
                            
                            # 백업 코드 생성
                            backup_codes = self.generate_backup_codes(user_email)
                            
                            st.success("✅ 2단계 인증이 성공적으로 설정되었습니다!")
                            
                            # 백업 코드 표시
                            st.warning("⚠️ 다음 백업 코드를 안전한 곳에 저장하세요!")
                            st.write("인증 앱을 사용할 수 없을 때 이 코드들을 사용할 수 있습니다.")
                            
                            for i, code in enumerate(backup_codes, 1):
                                st.code(f"{i:2d}. {code}")
                            
                            # 설정 완료
                            if "setup_2fa_step" in st.session_state:
                                del st.session_state.setup_2fa_step
                            
                            st.rerun()
                        else:
                            st.error("❌ 인증 코드가 올바르지 않습니다. 다시 시도하세요.")
    
    def show_2fa_verification(self, user_email: str) -> bool:
        """2FA 인증 화면"""
        st.subheader("🔐 2단계 인증")
        st.write(f"**{user_email}** 계정의 2단계 인증을 완료하세요.")
        
        with st.form("2fa_verification_form"):
            st.write("인증 앱에서 생성된 6자리 코드를 입력하거나 백업 코드를 사용하세요:")
            
            verification_code = st.text_input(
                "인증 코드",
                max_chars=8,  # 백업 코드는 8자리
                placeholder="123456 또는 백업코드"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                verify_button = st.form_submit_button("인증", type="primary")
            
            with col2:
                cancel_button = st.form_submit_button("취소")
            
            if verify_button:
                if not verification_code:
                    st.error("인증 코드를 입력하세요.")
                    return False
                
                # TOTP 코드 확인
                if len(verification_code) == 6 and verification_code.isdigit():
                    if self.verify_totp_code(user_email, verification_code):
                        st.success("✅ 인증 성공!")
                        return True
                    else:
                        st.error("❌ 인증 코드가 올바르지 않습니다.")
                        return False
                
                # 백업 코드 확인
                elif len(verification_code) == 8:
                    if self.verify_backup_code(user_email, verification_code):
                        st.success("✅ 백업 코드 인증 성공!")
                        st.warning("⚠️ 백업 코드가 사용되었습니다. 남은 백업 코드를 확인하세요.")
                        return True
                    else:
                        st.error("❌ 백업 코드가 올바르지 않거나 이미 사용되었습니다.")
                        return False
                
                else:
                    st.error("❌ 올바른 형식의 코드를 입력하세요. (6자리 숫자 또는 8자리 백업코드)")
                    return False
            
            if cancel_button:
                return False
        
        # 도움말
        with st.expander("❓ 도움말"):
            st.write("**인증 앱 코드를 사용할 수 없나요?**")
            st.write("- 백업 코드를 사용하세요 (8자리)")
            st.write("- 인증 앱의 시간이 정확한지 확인하세요")
            st.write("- 관리자에게 문의하세요")
        
        return False
    
    def require_2fa_verification(self, user_email: str) -> bool:
        """2FA 인증 필요 여부 확인"""
        if not self.is_2fa_enabled(user_email):
            return True  # 2FA가 비활성화된 경우 통과
        
        # 이미 인증된 경우 확인
        verification_key = f"2fa_verified_{user_email}"
        if verification_key in st.session_state:
            # 인증 시간 확인 (30분 유효)
            verification_time = st.session_state[verification_key]
            if time.time() - verification_time < 1800:  # 30분
                return True
        
        # 2FA 인증 필요
        return self.show_2fa_verification(user_email)
    
    def mark_2fa_verified(self, user_email: str):
        """2FA 인증 완료 표시"""
        verification_key = f"2fa_verified_{user_email}"
        st.session_state[verification_key] = time.time()
    
    def get_backup_codes_count(self, user_email: str) -> int:
        """남은 백업 코드 개수 반환"""
        if user_email in st.session_state.backup_codes:
            return len(st.session_state.backup_codes[user_email])
        return 0 