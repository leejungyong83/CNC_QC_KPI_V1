"""
알림 센터 페이지
시스템의 모든 알림을 표시하고 관리하는 페이지
"""

import streamlit as st
from utils.notification_system import NotificationSystem
from datetime import datetime, timedelta


def show_notifications():
    """알림 센터 페이지 표시"""
    st.title("🔔 알림 센터")
    
    # 알림 시스템 초기화
    notification_system = NotificationSystem()
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📢 전체 알림", "⚙️ 알림 설정", "📊 알림 통계"])
    
    with tab1:
        show_all_notifications(notification_system)
    
    with tab2:
        show_notification_settings()
    
    with tab3:
        show_notification_statistics(notification_system)


def show_all_notifications(notification_system):
    """전체 알림 표시"""
    st.subheader("📢 전체 알림")
    
    # 새로고침 버튼
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 새로고침", help="알림 목록을 새로고침합니다"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("자동 새로고침", help="30초마다 자동으로 새로고침")
    
    # 자동 새로고침 (실제 운영에서는 WebSocket 등 더 효율적인 방법 권장)
    if auto_refresh:
        st.info("ℹ️ 자동 새로고침이 활성화되었습니다. (30초 간격)")
        # 실제 자동 새로고침 구현은 복잡하므로 사용자가 수동으로 새로고침하도록 안내
    
    # 알림 표시
    notification_system.show_notification_panel()
    
    # 추가 정보
    with st.expander("ℹ️ 알림 시스템 정보"):
        st.write("**알림 종류:**")
        st.write("- 🕐 **검사 지연**: 7일간 검사 실적 없음")
        st.write("- ❌ **불량 발생**: 24시간 내 불량 발생")
        st.write("- 📈 **불량률 초과**: 목표 2.0% 초과")
        st.write("- 📉 **검사 효율성 미달**: 목표 95% 미달")
        st.write("- 📊 **검사 볼륨 부족**: 월 30건 미달")
        st.write("")
        st.write("**중요도 레벨:**")
        st.write("- 🔴 **CRITICAL**: 즉시 조치 필요")
        st.write("- 🟠 **HIGH**: 우선 처리 필요")
        st.write("- 🔵 **MEDIUM**: 일반 처리")
        st.write("- ⚪ **LOW**: 참고 사항")


def show_notification_settings():
    """알림 설정"""
    st.subheader("⚙️ 알림 설정")
    
    st.info("💡 알림 설정 기능은 향후 버전에서 제공될 예정입니다.")
    
    # 기본 설정 UI (향후 구현)
    with st.expander("🔧 알림 임계값 설정 (예시)"):
        st.write("**검사 지연 기준:**")
        delay_days = st.slider("검사 실적 없음 기준 (일)", 1, 14, 7)
        min_weekly_inspections = st.slider("주당 최소 검사 건수", 1, 20, 5)
        
        st.write("**불량률 임계값:**")
        target_defect_rate = st.slider("목표 불량률 (%)", 0.5, 5.0, 2.0, 0.1)
        critical_defect_rate = st.slider("긴급 불량률 (%)", 3.0, 10.0, 5.0, 0.1)
        
        st.write("**검사 효율성 임계값:**")
        target_efficiency = st.slider("목표 검사 효율성 (%)", 80, 100, 95)
        low_efficiency = st.slider("낮은 효율성 기준 (%)", 50, 90, 80)
        
        st.write("**검사 볼륨 기준:**")
        min_monthly_inspections = st.slider("월 최소 검사 건수", 10, 100, 30)
        
        if st.button("설정 저장 (향후 구현)"):
            st.success("설정이 저장되었습니다. (시뮬레이션)")
    
    with st.expander("📧 알림 수신 설정 (향후 구현)"):
        st.checkbox("이메일 알림 활성화", value=True)
        st.checkbox("SMS 알림 활성화", value=False)
        st.checkbox("웹 푸시 알림 활성화", value=True)
        
        st.text_input("알림 이메일 주소", value="admin@company.com")
        st.text_input("SMS 번호", value="010-0000-0000")
        
        if st.button("알림 설정 저장 (향후 구현)"):
            st.success("알림 설정이 저장되었습니다. (시뮬레이션)")


def show_notification_statistics(notification_system):
    """알림 통계"""
    st.subheader("📊 알림 통계")
    
    # 현재 알림 가져오기
    notifications = notification_system.get_all_notifications()
    
    if not notifications:
        st.info("📊 현재 활성 알림이 없어 통계를 표시할 수 없습니다.")
        return
    
    # 알림 통계 계산
    total_count = len(notifications)
    critical_count = sum(1 for n in notifications if n['priority'] == 'critical')
    high_count = sum(1 for n in notifications if n['priority'] == 'high')
    medium_count = sum(1 for n in notifications if n['priority'] == 'medium')
    low_count = sum(1 for n in notifications if n['priority'] == 'low')
    
    # 타입별 통계
    type_counts = {}
    for notification in notifications:
        ntype = notification['type']
        type_counts[ntype] = type_counts.get(ntype, 0) + 1
    
    # 통계 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**중요도별 알림 수:**")
        
        # 중요도별 메트릭
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("🔴 긴급", critical_count)
            st.metric("🔵 일반", medium_count)
        with metric_col2:
            st.metric("🟠 중요", high_count)
            st.metric("⚪ 낮음", low_count)
    
    with col2:
        st.write("**유형별 알림 수:**")
        
        type_names = {
            'inspection_delay': '🕐 검사 지연',
            'inspection_low': '📉 검사 부족',
            'defect_occurrence': '❌ 불량 발생',
            'kpi_defect_rate': '📈 불량률 초과',
            'kpi_efficiency': '📉 효율성 미달',
            'kpi_volume': '📊 볼륨 부족'
        }
        
        for ntype, count in type_counts.items():
            type_name = type_names.get(ntype, ntype)
            st.write(f"**{type_name}**: {count}건")
    
    # 알림 추세 (가상 데이터 - 향후 실제 로그 데이터로 교체)
    st.write("**알림 추세 (최근 7일):**")
    st.info("💡 알림 추세 분석 기능은 향후 버전에서 제공될 예정입니다.")
    
    # 개선 제안
    if critical_count > 0:
        st.error(f"🚨 **즉시 조치 필요**: {critical_count}개의 긴급 알림이 있습니다.")
        st.write("**권장 조치:**")
        for notification in notifications:
            if notification['priority'] == 'critical':
                st.write(f"- {notification['title']}: {notification['action']}")
    
    elif high_count > 0:
        st.warning(f"⚠️ **우선 처리 권장**: {high_count}개의 중요 알림이 있습니다.")
    else:
        st.success("✅ 심각한 알림이 없습니다. 시스템이 안정적으로 운영되고 있습니다.")


if __name__ == "__main__":
    show_notifications() 