"""
알림 시스템 모듈
검사 지연, 불량 발생, KPI 목표 미달성 등에 대한 알림 기능 제공
"""

import streamlit as st
from datetime import datetime, timedelta, date
from utils.supabase_client import get_supabase_client
from utils.vietnam_timezone import get_vietnam_now
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
            # 최근 7일간 검사가 없는 경우 경고
            seven_days_ago = (get_vietnam_now() - timedelta(days=7)).strftime('%Y-%m-%d')
            today = get_vietnam_now().strftime('%Y-%m-%d')
            
            result = self.supabase.table('inspection_data') \
                .select('inspection_date') \
                .gte('inspection_date', seven_days_ago) \
                .lte('inspection_date', today) \
                .execute()
            
            if not result.data:
                notifications.append({
                    'type': 'inspection_delay',
                    'priority': 'high',
                    'title': '⏰ 검사 지연 경고',
                    'message': '최근 7일간 검사 실적이 없습니다.',
                    'action': '검사 일정 확인 필요',
                    'icon': '⚠️',
                    'timestamp': get_vietnam_now()
                })
            
            # 어제 검사가 없는 경우
            yesterday = (get_vietnam_now() - timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_result = self.supabase.table('inspection_data') \
                .select('inspection_date') \
                .eq('inspection_date', yesterday) \
                .execute()
            
            if not yesterday_result.data:
                notifications.append({
                    'type': 'daily_missing',
                    'priority': 'medium',
                    'title': '📅 어제 검사 실적 없음',
                    'message': f'어제({yesterday}) 검사 실적이 기록되지 않았습니다.',
                    'action': '검사 실적 입력 확인',
                    'icon': '📝',
                    'timestamp': get_vietnam_now()
                })
                
        except Exception as e:
            # 오류 발생 시 알림 추가
            notifications.append({
                'type': 'system_error',
                'priority': 'low',
                'title': '🔧 시스템 확인 필요',
                'message': f'검사 지연 확인 중 오류: {str(e)}',
                'action': '시스템 관리자 연락',
                'icon': '🔧',
                'timestamp': get_vietnam_now()
            })
        
        return notifications
    
    def _check_defect_alerts(self):
        """불량 발생 알림 확인"""
        notifications = []
        
        if not self.supabase:
            return notifications
            
        try:
            # 오늘 불량 발생 확인
            today = get_vietnam_now().strftime('%Y-%m-%d')
            
            defect_result = self.supabase.table('inspection_data') \
                .select('result, defect_quantity') \
                .eq('inspection_date', today) \
                .eq('result', '불합격') \
                .execute()
            
            if defect_result.data:
                total_defects = sum(item.get('defect_quantity', 0) for item in defect_result.data)
                
                if total_defects > 0:
                    priority = 'critical' if total_defects > 10 else 'high'
                    notifications.append({
                        'type': 'defect_alert',
                        'priority': priority,
                        'title': '🚨 오늘 불량 발생',
                        'message': f'오늘 총 {total_defects}개의 불량이 발생했습니다.',
                        'action': '불량 원인 분석 필요',
                        'icon': '⚠️',
                        'timestamp': get_vietnam_now()
                    })
                
        except Exception as e:
            notifications.append({
                'type': 'system_error',
                'priority': 'low',
                'title': '🔧 시스템 확인 필요',
                'message': f'불량 알림 확인 중 오류: {str(e)}',
                'action': '시스템 관리자 연락',
                'icon': '🔧',
                'timestamp': get_vietnam_now()
            })
        
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
                # 1. 불량률 목표 미달성 (목표: 0.02%)
                defect_rate = kpi_data.get('defect_rate', 0)
                target_defect_rate = 0.02
                
                if defect_rate > target_defect_rate:
                    priority = 'critical' if defect_rate > 2.0 else 'high'
                    notifications.append({
                        'type': 'kpi_defect_rate',
                        'priority': priority,
                        'title': '📈 불량률 목표 미달성',
                        'message': f'현재 불량률 {defect_rate:.3f}%가 목표 {target_defect_rate}%를 초과했습니다.',
                        'action': '품질 개선 조치 필요',
                        'icon': '⚠️',
                        'timestamp': get_vietnam_now()
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
                        'timestamp': get_vietnam_now()
                    })
                
                # 3. 검사 건수 부족 (최근 30일 기준)
                total_inspections = kpi_data.get('total_inspections', 0)
                min_inspections = 30  # 월 최소 30건 검사 권장
                
                if total_inspections < min_inspections:
                    notifications.append({
                        'type': 'kpi_inspections',
                        'priority': 'medium',
                        'title': '📊 검사 건수 부족',
                        'message': f'최근 30일간 검사 건수 {total_inspections}건이 권장 기준 {min_inspections}건에 미달했습니다.',
                        'action': '검사 스케줄 조정 검토',
                        'icon': '📈',
                        'timestamp': get_vietnam_now()
                    })
                
        except Exception as e:
            notifications.append({
                'type': 'system_error',
                'priority': 'low',
                'title': '🔧 시스템 확인 필요',
                'message': f'KPI 알림 확인 중 오류: {str(e)}',
                'action': '시스템 관리자 연락',
                'icon': '🔧',
                'timestamp': get_vietnam_now()
            })
        
        return notifications
    
    def show_notification_panel(self):
        """알림 패널 표시 (사이드바용)"""
        notifications = self.get_all_notifications()
        
        if notifications:
            st.sidebar.markdown("### 🔔 알림")
            
            # 중요도별 카운트
            critical_count = len([n for n in notifications if n['priority'] == 'critical'])
            high_count = len([n for n in notifications if n['priority'] == 'high'])
            
            if critical_count > 0:
                st.sidebar.error(f"🚨 긴급: {critical_count}건")
            if high_count > 0:
                st.sidebar.warning(f"⚠️ 중요: {high_count}건")
            
            # 최근 3개 알림만 표시
            for notification in notifications[:3]:
                icon = notification.get('icon', '📢')
                title = notification['title']
                message = notification['message']
                
                st.sidebar.markdown(f"{icon} **{title}**")
                st.sidebar.caption(message)
                
            if len(notifications) > 3:
                st.sidebar.info(f"📝 총 {len(notifications)}개 알림 (알림센터에서 전체 확인)")
        else:
            st.sidebar.success("✅ 모든 시스템 정상")

# 전역 인스턴스 생성
notification_system = NotificationSystem() 