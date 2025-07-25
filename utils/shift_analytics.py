"""
교대조 기준 분석 유틸리티
- 하루 정의: 08:00 ~ 다음날 07:59 기준 분석
- 교대조별 불량률 계산
- 일일 불량률 집계 (08:00~07:59 기준)
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from utils.vietnam_timezone import get_vietnam_now
from utils.shift_manager import shift_manager, get_shift_for_time
from utils.supabase_client import get_supabase_client
from utils.data_converter import convert_supabase_data_timezone

class ShiftAnalytics:
    """교대조 기준 분석 클래스"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def get_daily_defect_rate(self, work_date: date = None) -> Dict[str, Any]:
        """일일 불량률 계산 (08:00~07:59 기준)"""
        if work_date is None:
            work_date = get_shift_for_time(get_vietnam_now())['work_date']
        
        # 하루 전체 시간 범위 계산
        start_time, end_time = shift_manager.get_daily_time_range(work_date)
        
        try:
            # 해당 작업일의 모든 검사 데이터 조회
            result = self.supabase.table('inspection_data') \
                .select('result, total_inspected, defect_quantity, quantity, created_at, shift') \
                .gte('created_at', start_time.isoformat()) \
                .lte('created_at', end_time.isoformat()) \
                .execute()
            
            inspections = result.data if result.data else []
            
            # 베트남 시간으로 변환
            converted_inspections = convert_supabase_data_timezone(inspections)
            
            # 집계 계산
            total_inspections = len(converted_inspections)
            total_inspected_qty = 0
            total_defect_qty = 0
            pass_count = 0
            
            for inspection in converted_inspections:
                # 수량 정보
                inspected_qty = inspection.get('total_inspected') or inspection.get('quantity') or 0
                defect_qty = inspection.get('defect_quantity') or 0
                
                total_inspected_qty += inspected_qty
                total_defect_qty += defect_qty
                
                # 합격 건수
                if inspection.get('result') == '합격':
                    pass_count += 1
            
            # 불량률 계산
            defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
            inspection_efficiency = (pass_count / total_inspections * 100) if total_inspections > 0 else 0.0
            
            return {
                'work_date': work_date,
                'period': f"{start_time.strftime('%m/%d %H:%M')} ~ {end_time.strftime('%m/%d %H:%M')}",
                'total_inspections': total_inspections,
                'total_inspected_qty': total_inspected_qty,
                'total_defect_qty': total_defect_qty,
                'defect_rate': round(defect_rate, 3),
                'inspection_efficiency': round(inspection_efficiency, 1),
                'data_status': 'success'
            }
            
        except Exception as e:
            return {
                'work_date': work_date,
                'error': str(e),
                'data_status': 'error'
            }
    
    def get_shift_defect_rate(self, work_date: date, work_period: str) -> Dict[str, Any]:
        """교대조별 불량률 계산"""
        # 교대조 시간 범위 계산
        start_time, end_time = shift_manager.get_shift_time_range(work_date, work_period)
        
        try:
            # 해당 교대조의 검사 데이터 조회
            result = self.supabase.table('inspection_data') \
                .select('result, total_inspected, defect_quantity, quantity, created_at, shift, inspector_id') \
                .gte('created_at', start_time.isoformat()) \
                .lte('created_at', end_time.isoformat()) \
                .execute()
            
            inspections = result.data if result.data else []
            converted_inspections = convert_supabase_data_timezone(inspections)
            
            # 집계 계산
            total_inspections = len(converted_inspections)
            total_inspected_qty = 0
            total_defect_qty = 0
            pass_count = 0
            
            # 검사자별 통계
            inspector_stats = {}
            
            for inspection in converted_inspections:
                # 수량 정보
                inspected_qty = inspection.get('total_inspected') or inspection.get('quantity') or 0
                defect_qty = inspection.get('defect_quantity') or 0
                inspector_id = inspection.get('inspector_id')
                
                total_inspected_qty += inspected_qty
                total_defect_qty += defect_qty
                
                # 합격 건수
                if inspection.get('result') == '합격':
                    pass_count += 1
                
                # 검사자별 통계
                if inspector_id:
                    if inspector_id not in inspector_stats:
                        inspector_stats[inspector_id] = {
                            'inspections': 0,
                            'inspected_qty': 0,
                            'defect_qty': 0,
                            'pass_count': 0
                        }
                    
                    inspector_stats[inspector_id]['inspections'] += 1
                    inspector_stats[inspector_id]['inspected_qty'] += inspected_qty
                    inspector_stats[inspector_id]['defect_qty'] += defect_qty
                    if inspection.get('result') == '합격':
                        inspector_stats[inspector_id]['pass_count'] += 1
            
            # 불량률 계산
            defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
            inspection_efficiency = (pass_count / total_inspections * 100) if total_inspections > 0 else 0.0
            
            # 검사자별 성과 계산
            inspector_performance = []
            for inspector_id, stats in inspector_stats.items():
                if stats['inspected_qty'] > 0:
                    inspector_defect_rate = (stats['defect_qty'] / stats['inspected_qty'] * 100)
                    inspector_efficiency = (stats['pass_count'] / stats['inspections'] * 100)
                    
                    inspector_performance.append({
                        'inspector_id': inspector_id,
                        'inspections': stats['inspections'],
                        'inspected_qty': stats['inspected_qty'],
                        'defect_rate': round(inspector_defect_rate, 3),
                        'efficiency': round(inspector_efficiency, 1)
                    })
            
            return {
                'work_date': work_date,
                'work_period': work_period,
                'period_name': shift_manager.WORK_PERIODS[work_period],
                'time_range': f"{start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}",
                'total_inspections': total_inspections,
                'total_inspected_qty': total_inspected_qty,
                'total_defect_qty': total_defect_qty,
                'defect_rate': round(defect_rate, 3),
                'inspection_efficiency': round(inspection_efficiency, 1),
                'inspector_performance': inspector_performance,
                'data_status': 'success'
            }
            
        except Exception as e:
            return {
                'work_date': work_date,
                'work_period': work_period,
                'error': str(e),
                'data_status': 'error'
            }
    
    def get_weekly_shift_summary(self, end_date: date = None, days: int = 7) -> Dict[str, Any]:
        """주간 교대조별 요약"""
        if end_date is None:
            end_date = get_shift_for_time(get_vietnam_now())['work_date']
        
        start_date = end_date - timedelta(days=days-1)
        
        daily_summaries = []
        shift_totals = {'DAY': {'inspections': 0, 'defect_qty': 0, 'inspected_qty': 0}, 
                       'NIGHT': {'inspections': 0, 'defect_qty': 0, 'inspected_qty': 0}}
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # 주간조 데이터
            day_data = self.get_shift_defect_rate(current_date, 'DAY')
            # 야간조 데이터  
            night_data = self.get_shift_defect_rate(current_date, 'NIGHT')
            
            daily_summaries.append({
                'date': current_date,
                'day_shift': day_data,
                'night_shift': night_data
            })
            
            # 주간 총합 계산
            if day_data['data_status'] == 'success':
                shift_totals['DAY']['inspections'] += day_data['total_inspections']
                shift_totals['DAY']['defect_qty'] += day_data['total_defect_qty']
                shift_totals['DAY']['inspected_qty'] += day_data['total_inspected_qty']
            
            if night_data['data_status'] == 'success':
                shift_totals['NIGHT']['inspections'] += night_data['total_inspections']
                shift_totals['NIGHT']['defect_qty'] += night_data['total_defect_qty']
                shift_totals['NIGHT']['inspected_qty'] += night_data['total_inspected_qty']
        
        # 주간 평균 불량률 계산
        day_avg_defect_rate = (shift_totals['DAY']['defect_qty'] / shift_totals['DAY']['inspected_qty'] * 100) \
                              if shift_totals['DAY']['inspected_qty'] > 0 else 0.0
        night_avg_defect_rate = (shift_totals['NIGHT']['defect_qty'] / shift_totals['NIGHT']['inspected_qty'] * 100) \
                                if shift_totals['NIGHT']['inspected_qty'] > 0 else 0.0
        
        return {
            'period': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            'daily_summaries': daily_summaries,
            'week_totals': {
                'day_shift': {
                    **shift_totals['DAY'],
                    'avg_defect_rate': round(day_avg_defect_rate, 3)
                },
                'night_shift': {
                    **shift_totals['NIGHT'],
                    'avg_defect_rate': round(night_avg_defect_rate, 3)
                }
            }
        }
    
    def compare_shifts_performance(self, work_date: date = None) -> Dict[str, Any]:
        """교대조별 성과 비교"""
        if work_date is None:
            work_date = get_shift_for_time(get_vietnam_now())['work_date']
        
        day_data = self.get_shift_defect_rate(work_date, 'DAY')
        night_data = self.get_shift_defect_rate(work_date, 'NIGHT')
        
        comparison = {
            'work_date': work_date,
            'day_shift': day_data,
            'night_shift': night_data
        }
        
        # 비교 분석
        if day_data['data_status'] == 'success' and night_data['data_status'] == 'success':
            comparison['analysis'] = {
                'better_defect_rate': 'DAY' if day_data['defect_rate'] < night_data['defect_rate'] else 'NIGHT',
                'better_efficiency': 'DAY' if day_data['inspection_efficiency'] > night_data['inspection_efficiency'] else 'NIGHT',
                'defect_rate_diff': abs(day_data['defect_rate'] - night_data['defect_rate']),
                'efficiency_diff': abs(day_data['inspection_efficiency'] - night_data['inspection_efficiency'])
            }
        
        return comparison

# 전역 인스턴스
shift_analytics = ShiftAnalytics()

# 편의 함수들
def get_today_defect_rate() -> Dict[str, Any]:
    """오늘 일일 불량률 조회"""
    return shift_analytics.get_daily_defect_rate()

def get_shift_performance(work_date: date = None, work_period: str = None) -> Dict[str, Any]:
    """교대조별 성과 조회"""
    if work_date is None:
        work_date = get_shift_for_time(get_vietnam_now())['work_date']
    
    if work_period:
        return shift_analytics.get_shift_defect_rate(work_date, work_period)
    else:
        return shift_analytics.compare_shifts_performance(work_date) 