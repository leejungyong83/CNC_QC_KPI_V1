"""
알림 시스템 모듈
검사 지연, 불량 발생, KPI 목표 미달성 등에 대한 알림 기능 제공
"""

import streamlit as st
from datetime import datetime, timedelta, date
from utils.supabase_client import get_supabase_client
import pandas as pd


class NotificationSystem:
    """알림 시스템 클래스"""
    
    def __init__(self):
        self.supabase = None
        try:
            self.supabase = get_supabase_client()
        except Exception:
            pass  # 연결 실패 시 None으로 유지
    
    def get_all_notifications(self):
        """모든 알림을 조회하여 반환"""
        notifications = []
        
        # 1. 검사 지연 알림
        delay_notifications = self._check_inspection_delays()
        notifications.extend(delay_notifications)
        
        # 2. 불량 발생 알림
        defect_notifications = self._check_defect_alerts()
        notifications.extend(defect_notifications)
        
        # 3. KPI 목표 미달성 알림
        kpi_notifications = self._check_kpi_alerts()
        notifications.extend(kpi_notifications)
        
        # 중요도 순으로 정렬 (critical > high > medium > low)
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        notifications.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return notifications
    
    def _check_inspection_delays(self):
        """검사 지연 알림 확인"""
        notifications = []
        
        if not self.supabase:
            return notifications
            
        try:
            # 최근 7일간 검사 실적이 없는 경우 지연으로 판단
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 최근 검사 실적 조회
            recent_inspections = self.supabase.table('inspection_data') \
                .select('inspection_date, count') \
                .gte('inspection_date', seven_days_ago) \
                .execute()
            
            recent_count = len(recent_inspections.data) if recent_inspections.data else 0
            
            if recent_count == 0:
                notifications.append({
                    'type': 'inspection_delay',
                    'priority': 'high',
                    'title': '🕐 검사 실적 지연',
                    'message': f'최근 7일간 검사 실적이 없습니다.',
                    'action': '검사 데이터 입력 필요',
                    'icon': '⏰',
                    'timestamp': datetime.now()
                })
            elif recent_count < 5:  # 주당 최소 5건 검사 권장
                notifications.append({
                    'type': 'inspection_low',
                    'priority': 'medium',
                    'title': '📉 검사 실적 부족',
                    'message': f'최근 7일간 검사 실적이 {recent_count}건으로 적습니다.',
                    'action': '검사 빈도 증가 권장',
                    'icon': '📊',
                    'timestamp': datetime.now()
                })
                
        except Exception as e:
            # 에러 발생 시 알림으로 처리하지 않음 (로그만 기록)
            pass
            
        return notifications
    
    def _check_defect_alerts(self):
        """불량 발생 알림 확인"""
        notifications = []
        
        if not self.supabase:
            return notifications
            
        try:
            # 최근 24시간 내 불량 발생 확인
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            defect_inspections = self.supabase.table('inspection_data') \
                .select('inspection_date, result, defect_quantity, model_id, inspector_id') \
                .eq('result', '불합격') \
                .gte('inspection_date', yesterday) \
                .execute()
            
            defects = defect_inspections.data if defect_inspections.data else []
            
            if len(defects) > 0:
                total_defects = sum(d.get('defect_quantity', 1) for d in defects)
                
                priority = 'critical' if len(defects) >= 5 else 'high' if len(defects) >= 3 else 'medium'
                
                notifications.append({
                    'type': 'defect_occurrence',
                    'priority': priority,
                    'title': '❌ 불량 발생 알림',
                    'message': f'최근 24시간 내 {len(defects)}건의 불량이 발생했습니다. (총 {total_defects}개)',
                    'action': '불량 원인 분석 및 개선 조치 필요',
                    'icon': '🚨',
                    'timestamp': datetime.now()
                })
                
        except Exception as e:
            pass
            
        return notifications
    
    def _check_kpi_alerts(self):
        """KPI 목표 미달성 알림 확인"""
        notifications = []
        
        if not self.supabase:
            return notifications
            
        try:
            # KPI 데이터 계산
            from pages.dashboard import calculate_kpi_data
            kpi_data = calculate_kpi_data()
            
            if kpi_data.get('data_status') == 'success':
                # 1. 불량률 목표 미달성 (목표: 2.0%)
                defect_rate = kpi_data.get('defect_rate', 0)
                target_defect_rate = 2.0
                
                if defect_rate > target_defect_rate:
                    priority = 'critical' if defect_rate > 5.0 else 'high'
                    notifications.append({
                        'type': 'kpi_defect_rate',
                        'priority': priority,
                        'title': '📈 불량률 목표 미달성',
                        'message': f'현재 불량률 {defect_rate:.3f}%가 목표 {target_defect_rate}%를 초과했습니다.',
                        'action': '품질 개선 조치 필요',
                        'icon': '⚠️',
                        'timestamp': datetime.now()
                    })
                
                # 2. 검사 효율성 목표 미달성 (목표: 95%)
                efficiency = kpi_data.get('inspection_efficiency', 0)
                target_efficiency = 95.0
                
                if efficiency < target_efficiency:
                    priority = 'high' if efficiency < 80.0 else 'medium'
                    notifications.append({
                        'type': 'kpi_efficiency',
                        'priority': priority,
                        'title': '📉 검사 효율성 목표 미달성',
                        'message': f'현재 검사 효율성 {efficiency:.1f}%가 목표 {target_efficiency}%에 미달했습니다.',
                        'action': '검사 프로세스 개선 필요',
                        'icon': '🎯',
                        'timestamp': datetime.now()
                    })
                
                # 3. 검사 건수 부족 (최근 30일 기준)
                total_inspections = kpi_data.get('total_inspections', 0)
                min_inspections = 30  # 월 최소 30건 검사 권장
                
                if total_inspections < min_inspections:
                    notifications.append({
                        'type': 'kpi_volume',
                        'priority': 'medium',
                        'title': '📊 검사 볼륨 부족',
                        'message': f'최근 30일 검사 건수 {total_inspections}건이 권장 기준 {min_inspections}건에 미달했습니다.',
                        'action': '검사 계획 재검토 필요',
                        'icon': '📋',
                        'timestamp': datetime.now()
                    })
                    
        except Exception as e:
            pass
            
        return notifications
    
    def show_notification_panel(self):
        """알림 패널을 Streamlit에 표시"""
        notifications = self.get_all_notifications()
        
        if not notifications:
            st.success("✅ 현재 알림이 없습니다. 모든 시스템이 정상 작동 중입니다.")
            return
        
        # 중요도별 색상 및 아이콘
        priority_styles = {
            'critical': {'color': 'red', 'bg': '#ffebee'},
            'high': {'color': 'orange', 'bg': '#fff3e0'},
            'medium': {'color': 'blue', 'bg': '#e3f2fd'},
            'low': {'color': 'gray', 'bg': '#f5f5f5'}
        }
        
        st.subheader(f"🔔 알림 센터 ({len(notifications)}개)")
        
        for notification in notifications:
            priority = notification['priority']
            style = priority_styles.get(priority, priority_styles['medium'])
            
            with st.container():
                st.markdown(f"""
                <div style="
                    border-left: 4px solid {style['color']};
                    background-color: {style['bg']};
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 0 5px 5px 0;
                ">
                    <h4 style="margin: 0; color: {style['color']};">
                        {notification['icon']} {notification['title']} 
                        <span style="font-size: 0.7em; background: {style['color']}; color: white; padding: 2px 6px; border-radius: 3px;">
                            {priority.upper()}
                        </span>
                    </h4>
                    <p style="margin: 5px 0;">{notification['message']}</p>
                    <p style="margin: 0; font-style: italic; color: #666;">
                        💡 {notification['action']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # 알림 요약 통계
        critical_count = sum(1 for n in notifications if n['priority'] == 'critical')
        high_count = sum(1 for n in notifications if n['priority'] == 'high')
        
        if critical_count > 0:
            st.error(f"🚨 **긴급 알림 {critical_count}개**: 즉시 조치가 필요합니다!")
        elif high_count > 0:
            st.warning(f"⚠️ **중요 알림 {high_count}개**: 우선 처리가 필요합니다.")
        else:
            st.info("ℹ️ 모든 알림이 일반 수준입니다.")


def show_notification_sidebar():
    """사이드바에 간단한 알림 표시"""
    notification_system = NotificationSystem()
    notifications = notification_system.get_all_notifications()
    
    if notifications:
        critical_count = sum(1 for n in notifications if n['priority'] == 'critical')
        high_count = sum(1 for n in notifications if n['priority'] == 'high')
        
        total_count = len(notifications)
        
        if critical_count > 0:
            st.sidebar.error(f"🚨 긴급 알림 {critical_count}개")
        elif high_count > 0:
            st.sidebar.warning(f"⚠️ 중요 알림 {high_count}개")
        else:
            st.sidebar.info(f"🔔 알림 {total_count}개")
        
        return total_count
    else:
        st.sidebar.success("✅ 알림 없음")
        return 0 