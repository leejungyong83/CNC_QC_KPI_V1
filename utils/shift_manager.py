"""
교대조 관리 모듈
- 하루 정의: 08:00 ~ 다음날 07:59
- 주간조: 08:00 ~ 19:59 (A/B SHIFT)
- 야간조: 20:00 ~ 07:59 (A/B SHIFT)
- 교대 시간: 20:00
"""

from datetime import datetime, timedelta, time
from typing import Tuple, Dict, Any
from utils.vietnam_timezone import get_vietnam_now
import pytz

class ShiftManager:
    """교대조 관리 클래스"""
    
    # 시간 상수 정의
    DAY_START_HOUR = 8      # 하루 시작: 08:00
    DAY_START_MINUTE = 0
    SHIFT_CHANGE_HOUR = 20  # 교대 시간: 20:00  
    SHIFT_CHANGE_MINUTE = 0
    NIGHT_END_HOUR = 7      # 야간조 종료: 07:59
    NIGHT_END_MINUTE = 59
    DAY_END_HOUR = 19       # 주간조 종료: 19:59
    DAY_END_MINUTE = 59
    
    # 교대조 타입
    SHIFT_TYPES = {
        'A': 'A조',
        'B': 'B조'
    }
    
    # 근무 시간대
    WORK_PERIODS = {
        'DAY': '주간',
        'NIGHT': '야간'
    }
    
    def __init__(self):
        self.vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    
    def get_current_shift_info(self, input_time: datetime = None) -> Dict[str, Any]:
        """현재 시점의 교대조 정보를 반환"""
        if input_time is None:
            input_time = get_vietnam_now()
        
        # timezone-aware 객체로 변환
        if input_time.tzinfo is None:
            input_time = self.vietnam_tz.localize(input_time)
        
        work_period = self.get_work_period(input_time)
        work_date = self.get_work_date(input_time)
        shift_type = self.determine_shift_type(input_time, work_date)
        
        return {
            'datetime': input_time,
            'work_date': work_date,
            'work_period': work_period,
            'work_period_name': self.WORK_PERIODS[work_period],
            'shift_type': shift_type,
            'shift_name': f"{self.SHIFT_TYPES[shift_type]} {self.WORK_PERIODS[work_period]}",
            'full_shift_name': f"{work_date.strftime('%Y-%m-%d')} {self.SHIFT_TYPES[shift_type]} {self.WORK_PERIODS[work_period]}"
        }
    
    def get_work_period(self, input_time: datetime) -> str:
        """근무 시간대 판별 (주간/야간)"""
        current_time = input_time.time()
        
        # 주간조 시간: 08:00 ~ 19:59
        day_start = time(self.DAY_START_HOUR, self.DAY_START_MINUTE)
        day_end = time(self.DAY_END_HOUR, self.DAY_END_MINUTE)
        
        if day_start <= current_time <= day_end:
            return 'DAY'
        else:
            return 'NIGHT'
    
    def get_work_date(self, input_time: datetime) -> datetime:
        """작업일 계산 (08:00 기준으로 하루 시작)"""
        current_time = input_time.time()
        day_start = time(self.DAY_START_HOUR, self.DAY_START_MINUTE)
        
        if current_time >= day_start:
            # 08:00 이후면 당일이 작업일
            return input_time.date()
        else:
            # 08:00 이전이면 전날이 작업일 (야간조)
            return (input_time - timedelta(days=1)).date()
    
    def determine_shift_type(self, input_time: datetime, work_date: datetime) -> str:
        """A/B 교대조 판별 (간단한 방식: 날짜 기준 홀짝)"""
        # 실제 환경에서는 별도의 교대조 스케줄 테이블을 사용해야 함
        # 현재는 단순히 날짜 기준으로 A/B 교대
        if work_date.day % 2 == 1:
            return 'A'
        else:
            return 'B'
    
    def get_shift_time_range(self, work_date: datetime, work_period: str) -> Tuple[datetime, datetime]:
        """특정 교대조의 시작/종료 시간 계산"""
        work_date_dt = datetime.combine(work_date, time(0, 0))
        work_date_dt = self.vietnam_tz.localize(work_date_dt)
        
        if work_period == 'DAY':
            # 주간조: 당일 08:00 ~ 19:59
            start_time = work_date_dt.replace(
                hour=self.DAY_START_HOUR, 
                minute=self.DAY_START_MINUTE,
                second=0,
                microsecond=0
            )
            end_time = work_date_dt.replace(
                hour=self.DAY_END_HOUR,
                minute=self.DAY_END_MINUTE,
                second=59,
                microsecond=999999
            )
        else:
            # 야간조: 당일 20:00 ~ 다음날 07:59
            start_time = work_date_dt.replace(
                hour=self.SHIFT_CHANGE_HOUR,
                minute=self.SHIFT_CHANGE_MINUTE,
                second=0,
                microsecond=0
            )
            end_time = (work_date_dt + timedelta(days=1)).replace(
                hour=self.NIGHT_END_HOUR,
                minute=self.NIGHT_END_MINUTE,
                second=59,
                microsecond=999999
            )
        
        return start_time, end_time
    
    def get_daily_time_range(self, work_date: datetime) -> Tuple[datetime, datetime]:
        """하루 전체 시간 범위 (08:00 ~ 다음날 07:59)"""
        work_date_dt = datetime.combine(work_date, time(0, 0))
        work_date_dt = self.vietnam_tz.localize(work_date_dt)
        
        start_time = work_date_dt.replace(
            hour=self.DAY_START_HOUR,
            minute=self.DAY_START_MINUTE,
            second=0,
            microsecond=0
        )
        end_time = (work_date_dt + timedelta(days=1)).replace(
            hour=self.NIGHT_END_HOUR,
            minute=self.NIGHT_END_MINUTE,
            second=59,
            microsecond=999999
        )
        
        return start_time, end_time
    
    def format_shift_display(self, shift_info: Dict[str, Any]) -> str:
        """교대조 정보를 표시용 문자열로 포맷"""
        return f"{shift_info['work_date'].strftime('%Y-%m-%d')} {shift_info['shift_name']}"
    
    def is_same_work_day(self, time1: datetime, time2: datetime) -> bool:
        """두 시간이 같은 작업일인지 확인"""
        work_date1 = self.get_work_date(time1)
        work_date2 = self.get_work_date(time2)
        return work_date1 == work_date2
    
    def get_shift_statistics_query_params(self, work_date: datetime, work_period: str = None) -> Dict[str, Any]:
        """교대조별 통계 조회용 파라미터 생성"""
        if work_period:
            # 특정 교대조만
            start_time, end_time = self.get_shift_time_range(work_date, work_period)
        else:
            # 하루 전체
            start_time, end_time = self.get_daily_time_range(work_date)
        
        return {
            'start_datetime': start_time.isoformat(),
            'end_datetime': end_time.isoformat(),
            'work_date': work_date.strftime('%Y-%m-%d'),
            'work_period': work_period
        }

# 전역 인스턴스
shift_manager = ShiftManager()

# 편의 함수들
def get_current_shift() -> Dict[str, Any]:
    """현재 교대조 정보 조회"""
    return shift_manager.get_current_shift_info()

def get_shift_for_time(input_time: datetime) -> Dict[str, Any]:
    """특정 시간의 교대조 정보 조회"""
    return shift_manager.get_current_shift_info(input_time)

def is_day_shift(input_time: datetime = None) -> bool:
    """주간조 여부 확인"""
    if input_time is None:
        input_time = get_vietnam_now()
    return shift_manager.get_work_period(input_time) == 'DAY'

def is_night_shift(input_time: datetime = None) -> bool:
    """야간조 여부 확인"""
    if input_time is None:
        input_time = get_vietnam_now()
    return shift_manager.get_work_period(input_time) == 'NIGHT'

def get_work_date_for_time(input_time: datetime = None) -> datetime:
    """특정 시간의 작업일 조회"""
    if input_time is None:
        input_time = get_vietnam_now()
    return shift_manager.get_work_date(input_time) 