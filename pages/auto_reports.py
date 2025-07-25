"""
자동 보고서 관리 페이지
보고서 생성, 미리보기, 이메일 발송 관리 기능
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.report_generator import report_generator, auto_scheduler
from typing import List

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)


def show_auto_reports():
    """자동 보고서 페이지 표시"""
    st.title("📋 자동 보고서 생성")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 보고서 생성", "📧 이메일 설정", "⏰ 스케줄 관리", "📈 보고서 히스토리"])
    
    with tab1:
        show_report_generation()
    
    with tab2:
        show_email_settings()
    
    with tab3:
        show_schedule_management()
    
    with tab4:
        show_report_history()


def show_report_generation():
    """보고서 생성 탭"""
    st.subheader("📊 보고서 생성 및 미리보기")
    
    # 보고서 유형 선택
    report_type = st.selectbox(
        "보고서 유형 선택",
        options=["일별 보고서", "주별 보고서", "월별 보고서"],
        help="생성할 보고서 유형을 선택하세요"
    )
    
    col1, col2 = st.columns(2)
    
    # 날짜 선택 (베트남 시간대 기준)
    vietnam_today = get_vietnam_date()
    
    if report_type == "일별 보고서":
        with col1:
            target_date = st.date_input(
                "보고서 날짜",
                value=vietnam_today - timedelta(days=1),
                help="보고서를 생성할 날짜를 선택하세요"
            )
        
        with col2:
            if st.button("📋 일별 보고서 생성", use_container_width=True):
                generate_and_show_daily_report(target_date)
    
    elif report_type == "주별 보고서":
        with col1:
            end_date = st.date_input(
                "주말 날짜 (토요일)",
                value=vietnam_today - timedelta(days=1),
                help="주의 마지막 날짜를 선택하세요"
            )
        
        with col2:
            if st.button("📋 주별 보고서 생성", use_container_width=True):
                generate_and_show_weekly_report(end_date)
    
    elif report_type == "월별 보고서":
        vietnam_now = get_vietnam_now()
        with col1:
            year = st.number_input(
                "연도",
                min_value=2020,
                max_value=2030,
                value=vietnam_now.year,
                step=1
            )
        
        with col2:
            month = st.number_input(
                "월",
                min_value=1,
                max_value=12,
                value=vietnam_now.month,
                step=1
            )
        
        if st.button("📋 월별 보고서 생성", use_container_width=True):
            generate_and_show_monthly_report(year, month)
    
    # 미리보기 영역
    if 'current_report_html' in st.session_state:
        st.write("---")
        st.subheader("📄 보고서 미리보기")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 이메일 발송", use_container_width=True):
                show_email_send_dialog()
        
        with col2:
            if st.button("💾 HTML 다운로드", use_container_width=True):
                download_html_report()
        
        with col3:
            if st.button("🔄 새로고침", use_container_width=True):
                del st.session_state['current_report_html']
                st.rerun()
        
        # HTML 미리보기
        st.components.v1.html(
            st.session_state['current_report_html'],
            height=800,
            scrolling=True
        )


def generate_and_show_daily_report(target_date: date):
    """일별 보고서 생성 및 표시"""
    with st.spinner("일별 보고서 생성 중..."):
        try:
            html_content, pdf_data = report_generator.generate_daily_report(target_date)
            
            # 세션에 저장
            st.session_state['current_report_html'] = html_content
            st.session_state['current_report_type'] = "daily"
            st.session_state['current_report_date'] = target_date
            st.session_state['current_report_data'] = pdf_data
            
            st.success(f"✅ {target_date.strftime('%Y년 %m월 %d일')} 일별 보고서가 생성되었습니다!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 보고서 생성 실패: {str(e)}")


def generate_and_show_weekly_report(end_date: date):
    """주별 보고서 생성 및 표시"""
    with st.spinner("주별 보고서 생성 중..."):
        try:
            html_content, pdf_data = report_generator.generate_weekly_report(end_date)
            
            start_date = end_date - timedelta(days=6)
            
            # 세션에 저장
            st.session_state['current_report_html'] = html_content
            st.session_state['current_report_type'] = "weekly"
            st.session_state['current_report_date'] = end_date
            st.session_state['current_report_data'] = pdf_data
            
            st.success(f"✅ {start_date.strftime('%m/%d')} ~ {end_date.strftime('%m/%d')} 주별 보고서가 생성되었습니다!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 보고서 생성 실패: {str(e)}")


def generate_and_show_monthly_report(year: int, month: int):
    """월별 보고서 생성 및 표시"""
    with st.spinner("월별 보고서 생성 중..."):
        try:
            html_content, pdf_data = report_generator.generate_monthly_report(year, month)
            
            # 세션에 저장
            st.session_state['current_report_html'] = html_content
            st.session_state['current_report_type'] = "monthly"
            st.session_state['current_report_date'] = f"{year}-{month:02d}"
            st.session_state['current_report_data'] = pdf_data
            
            st.success(f"✅ {year}년 {month}월 월별 보고서가 생성되었습니다!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 보고서 생성 실패: {str(e)}")


def show_email_send_dialog():
    """이메일 발송 다이얼로그"""
    st.subheader("📧 보고서 이메일 발송")
    
    # 수신자 입력
    recipient_emails = st.text_area(
        "수신자 이메일 (여러 개는 줄바꿈으로 구분)",
        placeholder="example1@company.com\nexample2@company.com",
        help="보고서를 받을 이메일 주소를 입력하세요"
    )
    
    # 이메일 제목 커스터마이징
    default_subject = f"[CNC QC] {st.session_state['current_report_type']} 보고서"
    email_subject = st.text_input(
        "이메일 제목",
        value=default_subject,
        help="이메일 제목을 수정할 수 있습니다"
    )
    
    # 발송 버튼
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 이메일 발송", use_container_width=True):
            if recipient_emails.strip():
                email_list = [email.strip() for email in recipient_emails.split('\n') if email.strip()]
                send_report_email(email_list, email_subject)
            else:
                st.error("수신자 이메일을 입력해주세요.")
    
    with col2:
        if st.button("❌ 취소", use_container_width=True):
            st.rerun()


def send_report_email(email_list: List[str], subject: str):
    """보고서 이메일 발송"""
    with st.spinner("이메일 발송 중..."):
        try:
            from utils.report_generator import EmailSender
            email_sender = EmailSender()
            
            html_content = st.session_state['current_report_html']
            attachment_data = st.session_state['current_report_data']
            report_date = st.session_state['current_report_date']
            report_type = st.session_state['current_report_type']
            
            attachment_name = f"{report_type}_report_{report_date}.html"
            
            success_count = 0
            failed_emails = []
            
            for email in email_list:
                if email_sender.send_report(
                    recipient_email=email,
                    subject=subject,
                    html_content=html_content,
                    attachment_data=attachment_data,
                    attachment_name=attachment_name
                ):
                    success_count += 1
                else:
                    failed_emails.append(email)
            
            # 결과 표시
            if success_count > 0:
                st.success(f"✅ {success_count}개 이메일 발송 완료!")
            
            if failed_emails:
                st.error(f"❌ 발송 실패: {', '.join(failed_emails)}")
            
            # 발송 기록 저장
            save_email_history(email_list, subject, success_count, failed_emails)
            
        except Exception as e:
            st.error(f"❌ 이메일 발송 중 오류: {str(e)}")


def download_html_report():
    """HTML 보고서 다운로드"""
    if 'current_report_html' in st.session_state:
        html_content = st.session_state['current_report_html']
        report_date = st.session_state['current_report_date']
        report_type = st.session_state['current_report_type']
        
        filename = f"{report_type}_report_{report_date}.html"
        
        st.download_button(
            label="💾 HTML 파일 다운로드",
            data=html_content.encode('utf-8'),
            file_name=filename,
            mime="text/html",
            use_container_width=True
        )


def show_email_settings():
    """이메일 설정 탭"""
    st.subheader("📧 이메일 발송 설정")
    
    # 현재 설정 표시
    st.write("### 🔧 SMTP 설정")
    
    # 설정 상태 확인
    try:
        smtp_configured = bool(st.secrets.get("EMAIL_USER") and st.secrets.get("EMAIL_PASSWORD"))
    except:
        smtp_configured = False
    
    if smtp_configured:
        st.success("✅ 이메일 설정이 구성되어 있습니다.")
        
        # 설정 정보 표시 (비밀번호는 마스킹)
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**SMTP 서버:** {st.secrets.get('SMTP_SERVER', 'smtp.gmail.com')}")
            st.info(f"**포트:** {st.secrets.get('SMTP_PORT', 587)}")
        
        with col2:
            email_user = st.secrets.get("EMAIL_USER", "")
            masked_email = email_user[:3] + "*" * (len(email_user) - 6) + email_user[-3:] if len(email_user) > 6 else email_user
            st.info(f"**발송자 이메일:** {masked_email}")
            st.info("**비밀번호:** " + "*" * 12)
    else:
        st.warning("⚠️ 이메일 설정이 구성되지 않았습니다.")
        
        with st.expander("📋 이메일 설정 방법"):
            st.write("""
            **Streamlit Cloud 또는 로컬 환경에서 이메일 설정 방법:**
            
            1. **Streamlit Cloud의 경우:**
               - 앱 설정에서 Secrets 탭으로 이동
               - 다음 형식으로 추가:
               ```toml
               EMAIL_USER = "your-email@gmail.com"
               EMAIL_PASSWORD = "your-app-password"
               SMTP_SERVER = "smtp.gmail.com"
               SMTP_PORT = 587
               ```
            
            2. **로컬 환경의 경우:**
               - `.streamlit/secrets.toml` 파일 생성
               - 위와 같은 형식으로 설정 추가
            
            3. **Gmail 사용 시:**
               - 2단계 인증 활성화 필요
               - 앱 비밀번호 생성 후 `EMAIL_PASSWORD`에 입력
            
            **보안 주의사항:**
            - 절대 소스코드에 직접 비밀번호를 입력하지 마세요
            - Streamlit Secrets 기능을 반드시 사용하세요
            """)
    
    # 테스트 이메일 발송
    st.write("---")
    st.write("### 🧪 테스트 이메일 발송")
    
    if smtp_configured:
        test_email = st.text_input(
            "테스트 수신 이메일",
            placeholder="test@example.com",
            help="테스트 이메일을 받을 주소를 입력하세요"
        )
        
        if st.button("📧 테스트 이메일 발송", use_container_width=True):
            if test_email:
                send_test_email(test_email)
            else:
                st.error("테스트 이메일 주소를 입력해주세요.")
    else:
        st.info("이메일 설정을 완료한 후 테스트할 수 있습니다.")
    
    # 수신자 그룹 관리
    st.write("---")
    st.write("### 👥 수신자 그룹 관리")
    
    manage_recipient_groups()


def send_test_email(test_email: str):
    """테스트 이메일 발송"""
    with st.spinner("테스트 이메일 발송 중..."):
        try:
            from utils.report_generator import EmailSender
            email_sender = EmailSender()
            
            test_html = """
            <html>
            <body>
                <h2>🧪 CNC QC KPI 시스템 테스트 이메일</h2>
                <p>이메일 설정이 정상적으로 구성되었습니다!</p>
                <p><strong>발송 시간:</strong> {}</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    이 메일은 CNC QC KPI 시스템에서 자동 발송된 테스트 메일입니다.
                </p>
            </body>
            </html>
            """.format(get_vietnam_display_time())
            
            success = email_sender.send_report(
                recipient_email=test_email,
                subject="[CNC QC] 이메일 설정 테스트",
                html_content=test_html
            )
            
            if success:
                st.success(f"✅ 테스트 이메일이 {test_email}로 발송되었습니다!")
            else:
                st.error("❌ 테스트 이메일 발송에 실패했습니다.")
                
        except Exception as e:
            st.error(f"❌ 테스트 이메일 발송 중 오류: {str(e)}")


def manage_recipient_groups():
    """수신자 그룹 관리"""
    # 세션 상태에서 수신자 그룹 가져오기
    if 'recipient_groups' not in st.session_state:
        st.session_state.recipient_groups = {
            "관리팀": ["manager1@company.com", "manager2@company.com"],
            "품질팀": ["quality1@company.com", "quality2@company.com"],
            "생산팀": ["production1@company.com"]
        }
    
    groups = st.session_state.recipient_groups
    
    # 기존 그룹 표시
    if groups:
        st.write("**기존 수신자 그룹:**")
        
        for group_name, emails in groups.items():
            with st.expander(f"📧 {group_name} ({len(emails)}명)"):
                for email in emails:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {email}")
                    with col2:
                        if st.button("삭제", key=f"del_{group_name}_{email}"):
                            groups[group_name].remove(email)
                            if not groups[group_name]:  # 그룹이 비어있으면 삭제
                                del groups[group_name]
                            st.rerun()
                
                # 그룹에 이메일 추가
                new_email = st.text_input(f"이메일 추가", key=f"add_{group_name}")
                if st.button(f"추가", key=f"add_btn_{group_name}"):
                    if new_email and new_email not in groups[group_name]:
                        groups[group_name].append(new_email)
                        st.rerun()
                
                # 그룹 삭제
                if st.button(f"'{group_name}' 그룹 삭제", key=f"del_group_{group_name}"):
                    del groups[group_name]
                    st.rerun()
    
    # 새 그룹 추가
    st.write("---")
    st.write("**새 수신자 그룹 추가:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_group_name = st.text_input("그룹 이름")
    
    with col2:
        new_group_emails = st.text_area(
            "이메일 목록 (줄바꿈으로 구분)",
            placeholder="email1@company.com\nemail2@company.com"
        )
    
    if st.button("📧 새 그룹 추가", use_container_width=True):
        if new_group_name and new_group_emails:
            email_list = [email.strip() for email in new_group_emails.split('\n') if email.strip()]
            groups[new_group_name] = email_list
            st.success(f"✅ '{new_group_name}' 그룹이 추가되었습니다!")
            st.rerun()
        else:
            st.error("그룹 이름과 이메일 목록을 모두 입력해주세요.")


def show_schedule_management():
    """스케줄 관리 탭"""
    st.subheader("⏰ 자동 보고서 스케줄 관리")
    
    st.info("""
    ℹ️ **Streamlit 환경 제한사항**
    
    Streamlit은 백그라운드 작업을 지원하지 않아 완전 자동화된 스케줄링이 어렵습니다.
    현재는 **수동 실행** 방식으로 구현되어 있으며, 향후 별도 스케줄러 서비스 구축을 권장합니다.
    """)
    
    # 스케줄 설정
    st.write("### 📅 보고서 발송 스케줄")
    
    # 일별 보고서
    with st.expander("📊 일별 보고서 설정", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            daily_enabled = st.checkbox("일별 보고서 활성화", value=False)
            daily_time = st.time_input("발송 시간", value=datetime.strptime("09:00", "%H:%M").time())
        
        with col2:
            daily_recipients = st.selectbox(
                "수신자 그룹",
                options=list(st.session_state.get('recipient_groups', {}).keys()) + ["직접 입력"],
                key="daily_recipients"
            )
            
            if daily_recipients == "직접 입력":
                daily_emails = st.text_area(
                    "수신자 이메일",
                    placeholder="email1@company.com\nemail2@company.com",
                    key="daily_emails"
                )
        
        if st.button("📧 오늘 일별 보고서 수동 발송", use_container_width=True):
            execute_daily_report_schedule(daily_recipients)
    
    # 주별 보고서
    with st.expander("📊 주별 보고서 설정"):
        col1, col2 = st.columns(2)
        
        with col1:
            weekly_enabled = st.checkbox("주별 보고서 활성화", value=False)
            weekly_day = st.selectbox("발송 요일", options=["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"])
        
        with col2:
            weekly_recipients = st.selectbox(
                "수신자 그룹",
                options=list(st.session_state.get('recipient_groups', {}).keys()) + ["직접 입력"],
                key="weekly_recipients"
            )
        
        if st.button("📧 이번 주 주별 보고서 수동 발송", use_container_width=True):
            execute_weekly_report_schedule(weekly_recipients)
    
    # 월별 보고서
    with st.expander("📊 월별 보고서 설정"):
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_enabled = st.checkbox("월별 보고서 활성화", value=False)
            monthly_day = st.number_input("발송일 (매월)", min_value=1, max_value=28, value=1)
        
        with col2:
            monthly_recipients = st.selectbox(
                "수신자 그룹",
                options=list(st.session_state.get('recipient_groups', {}).keys()) + ["직접 입력"],
                key="monthly_recipients"
            )
        
        if st.button("📧 지난 달 월별 보고서 수동 발송", use_container_width=True):
            execute_monthly_report_schedule(monthly_recipients)
    
    # 스케줄 상태 표시
    st.write("---")
    st.write("### 📋 현재 스케줄 상태")
    
    schedule_status = {
        "일별 보고서": "활성화" if daily_enabled else "비활성화",
        "주별 보고서": "활성화" if weekly_enabled else "비활성화",
        "월별 보고서": "활성화" if monthly_enabled else "비활성화"
    }
    
    status_df = pd.DataFrame([
        {"보고서 유형": k, "상태": v, "마지막 실행": "수동 실행"}
        for k, v in schedule_status.items()
    ])
    
    st.dataframe(status_df, use_container_width=True)


def execute_daily_report_schedule(recipients_group: str):
    """일별 보고서 스케줄 실행"""
    try:
        # 수신자 목록 가져오기
        if recipients_group == "직접 입력":
            email_input = st.session_state.get('daily_emails', '')
            recipient_emails = [email.strip() for email in email_input.split('\n') if email.strip()]
        else:
            recipient_emails = st.session_state.get('recipient_groups', {}).get(recipients_group, [])
        
        if not recipient_emails:
            st.error("수신자 이메일이 설정되지 않았습니다.")
            return
        
        # 일별 보고서 발송
        success = auto_scheduler.schedule_daily_report(recipient_emails)
        
        if success:
            st.success(f"✅ 일별 보고서가 {len(recipient_emails)}명에게 발송되었습니다!")
            save_schedule_history("daily", recipient_emails, True)
        else:
            st.error("❌ 일별 보고서 발송에 실패했습니다.")
            save_schedule_history("daily", recipient_emails, False)
            
    except Exception as e:
        st.error(f"❌ 일별 보고서 실행 중 오류: {str(e)}")


def execute_weekly_report_schedule(recipients_group: str):
    """주별 보고서 스케줄 실행"""
    try:
        # 수신자 목록 가져오기
        recipient_emails = st.session_state.get('recipient_groups', {}).get(recipients_group, [])
        
        if not recipient_emails:
            st.error("수신자 이메일이 설정되지 않았습니다.")
            return
        
        # 주별 보고서 발송
        success = auto_scheduler.schedule_weekly_report(recipient_emails)
        
        if success:
            st.success(f"✅ 주별 보고서가 {len(recipient_emails)}명에게 발송되었습니다!")
            save_schedule_history("weekly", recipient_emails, True)
        else:
            st.error("❌ 주별 보고서 발송에 실패했습니다.")
            save_schedule_history("weekly", recipient_emails, False)
            
    except Exception as e:
        st.error(f"❌ 주별 보고서 실행 중 오류: {str(e)}")


def execute_monthly_report_schedule(recipients_group: str):
    """월별 보고서 스케줄 실행"""
    try:
        # 수신자 목록 가져오기
        recipient_emails = st.session_state.get('recipient_groups', {}).get(recipients_group, [])
        
        if not recipient_emails:
            st.error("수신자 이메일이 설정되지 않았습니다.")
            return
        
        # 월별 보고서 발송
        success = auto_scheduler.schedule_monthly_report(recipient_emails)
        
        if success:
            st.success(f"✅ 월별 보고서가 {len(recipient_emails)}명에게 발송되었습니다!")
            save_schedule_history("monthly", recipient_emails, True)
        else:
            st.error("❌ 월별 보고서 발송에 실패했습니다.")
            save_schedule_history("monthly", recipient_emails, False)
            
    except Exception as e:
        st.error(f"❌ 월별 보고서 실행 중 오류: {str(e)}")


def save_email_history(email_list: List[str], subject: str, success_count: int, failed_emails: List[str]):
    """이메일 발송 기록 저장"""
    if 'email_history' not in st.session_state:
        st.session_state.email_history = []
    
    history_entry = {
        'timestamp': get_vietnam_now(),
        'type': 'manual',
        'recipients': email_list,
        'subject': subject,
        'success_count': success_count,
        'failed_count': len(failed_emails),
        'failed_emails': failed_emails
    }
    
    st.session_state.email_history.append(history_entry)
    
    # 최대 50개 기록만 유지
    if len(st.session_state.email_history) > 50:
        st.session_state.email_history = st.session_state.email_history[-50:]


def save_schedule_history(report_type: str, recipients: List[str], success: bool):
    """스케줄 실행 기록 저장"""
    if 'schedule_history' not in st.session_state:
        st.session_state.schedule_history = []
    
    history_entry = {
        'timestamp': get_vietnam_now(),
        'report_type': report_type,
        'recipients_count': len(recipients),
        'success': success
    }
    
    st.session_state.schedule_history.append(history_entry)
    
    # 최대 30개 기록만 유지
    if len(st.session_state.schedule_history) > 30:
        st.session_state.schedule_history = st.session_state.schedule_history[-30:]


def show_report_history():
    """보고서 히스토리 탭"""
    st.subheader("📈 보고서 발송 히스토리")
    
    # 이메일 발송 기록
    email_history = st.session_state.get('email_history', [])
    schedule_history = st.session_state.get('schedule_history', [])
    
    # 통계 요약
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_emails = len(email_history)
        st.metric("총 발송 건수", total_emails)
    
    with col2:
        successful_emails = sum(1 for h in email_history if h['success_count'] > 0)
        st.metric("성공 건수", successful_emails)
    
    with col3:
        total_recipients = sum(h['success_count'] for h in email_history)
        st.metric("총 수신자", total_recipients)
    
    with col4:
        if email_history:
            success_rate = (successful_emails / total_emails * 100)
            st.metric("성공률", f"{success_rate:.1f}%")
        else:
            st.metric("성공률", "0%")
    
    # 상세 히스토리
    st.write("---")
    st.write("### 📋 발송 기록 상세")
    
    if email_history or schedule_history:
        # 모든 기록 통합
        all_history = []
        
        for h in email_history:
            all_history.append({
                '시간': h['timestamp'].strftime('%Y-%m-%d %H:%M'),
                '유형': '수동 발송',
                '제목': h['subject'][:50] + '...' if len(h['subject']) > 50 else h['subject'],
                '수신자': f"{h['success_count']}명",
                '상태': '성공' if h['success_count'] > 0 else '실패'
            })
        
        for h in schedule_history:
            all_history.append({
                '시간': h['timestamp'].strftime('%Y-%m-%d %H:%M'),
                '유형': f"자동 {h['report_type']}",
                '제목': f"{h['report_type']} 보고서",
                '수신자': f"{h['recipients_count']}명",
                '상태': '성공' if h['success'] else '실패'
            })
        
        # 시간순 정렬
        all_history.sort(key=lambda x: x['시간'], reverse=True)
        
        # 최근 20개만 표시
        recent_history = all_history[:20]
        
        if recent_history:
            df = pd.DataFrame(recent_history)
            st.dataframe(df, use_container_width=True)
        
        # 기록 정리 버튼
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 이메일 기록 정리", use_container_width=True):
                st.session_state.email_history = []
                st.success("✅ 이메일 발송 기록이 정리되었습니다.")
                st.rerun()
        
        with col2:
            if st.button("🧹 스케줄 기록 정리", use_container_width=True):
                st.session_state.schedule_history = []
                st.success("✅ 스케줄 실행 기록이 정리되었습니다.")
                st.rerun()
    
    else:
        st.info("아직 발송 기록이 없습니다.")


if __name__ == "__main__":
    show_auto_reports() 