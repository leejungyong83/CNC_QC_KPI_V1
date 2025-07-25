"""
교대조 UI 컴포넌트 모듈
- 교대조 정보 표시
- 교대조 필터링
- 교대조 상태 표시
"""

import streamlit as st
from datetime import date, datetime
from typing import Dict, Any, Optional, List
from utils.shift_manager import get_current_shift, get_shift_for_time, shift_manager
from utils.vietnam_timezone import get_vietnam_now

def show_current_shift_banner():
    """현재 교대조 정보를 배너로 표시"""
    current_shift = get_current_shift()
    current_time = get_vietnam_now()
    
    # 교대조에 따른 색상 설정
    if current_shift['work_period'] == 'DAY':
        shift_color = "🟡"  # 주간조는 노란색
        bg_color = "#FFF9C4"
    else:
        shift_color = "🔵"  # 야간조는 파란색  
        bg_color = "#E3F2FD"
    
    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid {'#FFC107' if current_shift['work_period'] == 'DAY' else '#2196F3'};
        margin-bottom: 20px;
    ">
        <h4 style="margin: 0; color: #333;">
            {shift_color} 현재 교대조: {current_shift['full_shift_name']}
        </h4>
        <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
            🕐 {current_time.strftime('%Y-%m-%d %H:%M:%S')} (베트남 시간) | 
            📅 작업일: {current_shift['work_date']}
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_shift_status_indicator(work_date: date = None, compact: bool = False):
    """교대조 상태 지시자"""
    if work_date is None:
        work_date = get_current_shift()['work_date']
    
    current_time = get_vietnam_now()
    current_shift = get_shift_for_time(current_time)
    
    # 주간조/야간조 진행 상황 계산
    day_start, day_end = shift_manager.get_shift_time_range(work_date, 'DAY')
    night_start, night_end = shift_manager.get_shift_time_range(work_date, 'NIGHT')
    
    if compact:
        # 컴팩트 버전
        if current_shift['work_period'] == 'DAY':
            progress = min(100, max(0, (current_time - day_start).total_seconds() / (day_end - day_start).total_seconds() * 100))
            st.progress(progress / 100, text=f"☀️ 주간조 진행률: {progress:.0f}%")
        else:
            progress = min(100, max(0, (current_time - night_start).total_seconds() / (night_end - night_start).total_seconds() * 100))
            st.progress(progress / 100, text=f"🌙 야간조 진행률: {progress:.0f}%")
    else:
        # 상세 버전
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**☀️ 주간조 (08:00~19:59)**")
            if current_shift['work_period'] == 'DAY':
                progress = min(100, max(0, (current_time - day_start).total_seconds() / (day_end - day_start).total_seconds() * 100))
                st.progress(progress / 100, text=f"진행률: {progress:.0f}%")
                st.caption(f"🕐 {day_start.strftime('%H:%M')} ~ {day_end.strftime('%H:%M')}")
            else:
                st.info("주간조 시간이 아닙니다")
        
        with col2:
            st.write("**🌙 야간조 (20:00~07:59)**")
            if current_shift['work_period'] == 'NIGHT':
                progress = min(100, max(0, (current_time - night_start).total_seconds() / (night_end - night_start).total_seconds() * 100))
                st.progress(progress / 100, text=f"진행률: {progress:.0f}%")
                st.caption(f"🕐 {night_start.strftime('%H:%M')} ~ {night_end.strftime('%H:%M')}")
            else:
                st.info("야간조 시간이 아닙니다")

def create_shift_filter(
    key_prefix: str = "shift_filter",
    show_date: bool = True,
    show_shift_type: bool = True,
    show_work_period: bool = True,
    default_date: date = None
) -> Dict[str, Any]:
    """교대조 필터링 컴포넌트"""
    
    if default_date is None:
        default_date = get_current_shift()['work_date']
    
    filters = {}
    
    # 컬럼 개수 계산
    col_count = sum([show_date, show_shift_type, show_work_period])
    if col_count == 0:
        return filters
    
    cols = st.columns(col_count)
    col_idx = 0
    
    # 날짜 필터
    if show_date:
        with cols[col_idx]:
            filters['work_date'] = st.date_input(
                "📅 작업일",
                value=default_date,
                key=f"{key_prefix}_date",
                help="분석할 작업일을 선택하세요 (08:00 기준)"
            )
        col_idx += 1
    
    # 교대조 타입 필터 (A/B)
    if show_shift_type:
        with cols[col_idx]:
            filters['shift_type'] = st.selectbox(
                "🏭 교대조 타입",
                ["전체", "A조", "B조"],
                key=f"{key_prefix}_type",
                help="A조/B조를 선택하세요"
            )
        col_idx += 1
    
    # 근무시간대 필터 (주간/야간)
    if show_work_period:
        with cols[col_idx]:
            filters['work_period'] = st.selectbox(
                "⏰ 근무시간대",
                ["전체", "주간조", "야간조"],
                key=f"{key_prefix}_period",
                help="주간조(08:00~19:59) 또는 야간조(20:00~07:59)"
            )
        col_idx += 1
    
    return filters

def show_shift_comparison_cards(day_data: Dict, night_data: Dict):
    """교대조 비교 카드 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        # 주간조 카드
        if day_data.get('data_status') == 'success':
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #FFF8E1 0%, #FFE082 100%);
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid #FFC107;
                margin-bottom: 10px;
            ">
                <h3 style="margin: 0; color: #E65100;">☀️ 주간조</h3>
                <p style="margin: 5px 0; color: #BF360C; font-size: 16px; font-weight: bold;">
                    검사: {day_data['total_inspections']}건 | 불량률: {day_data['defect_rate']:.3f}%
                </p>
                <p style="margin: 0; color: #E65100; font-size: 14px;">
                    효율성: {day_data['inspection_efficiency']:.1f}% | 수량: {day_data['total_inspected_qty']}개
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #F5F5F5;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                color: #757575;
            ">
                <h3 style="margin: 0;">☀️ 주간조</h3>
                <p style="margin: 5px 0;">데이터 없음</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # 야간조 카드
        if night_data.get('data_status') == 'success':
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #E3F2FD 0%, #64B5F6 100%);
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid #2196F3;
                margin-bottom: 10px;
            ">
                <h3 style="margin: 0; color: #0D47A1;">🌙 야간조</h3>
                <p style="margin: 5px 0; color: #1565C0; font-size: 16px; font-weight: bold;">
                    검사: {night_data['total_inspections']}건 | 불량률: {night_data['defect_rate']:.3f}%
                </p>
                <p style="margin: 0; color: #0D47A1; font-size: 14px;">
                    효율성: {night_data['inspection_efficiency']:.1f}% | 수량: {night_data['total_inspected_qty']}개
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #F5F5F5;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                color: #757575;
            ">
                <h3 style="margin: 0;">🌙 야간조</h3>
                <p style="margin: 5px 0;">데이터 없음</p>
            </div>
            """, unsafe_allow_html=True)

def show_shift_timeline(work_date: date = None):
    """교대조 타임라인 표시"""
    if work_date is None:
        work_date = get_current_shift()['work_date']
    
    current_time = get_vietnam_now()
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_total_minutes = current_hour * 60 + current_minute
    
    # 24시간 타임라인 생성
    st.subheader("🕐 교대조 타임라인")
    
    # HTML로 타임라인 생성
    timeline_html = """
    <div style="position: relative; width: 100%; height: 60px; background: #f0f0f0; border-radius: 5px; margin: 10px 0;">
        <!-- 주간조 영역 (08:00~19:59) -->
        <div style="
            position: absolute;
            left: 33.33%;
            width: 50%;
            height: 100%;
            background: linear-gradient(90deg, #FFF8E1, #FFE082);
            border-radius: 5px;
            border: 2px solid #FFC107;
        "></div>
        
        <!-- 야간조 영역 1 (00:00~07:59) -->
        <div style="
            position: absolute;
            left: 0%;
            width: 33.33%;
            height: 100%;
            background: linear-gradient(90deg, #E3F2FD, #64B5F6);
            border-radius: 5px 0 0 5px;
            border: 2px solid #2196F3;
        "></div>
        
        <!-- 야간조 영역 2 (20:00~23:59) -->
        <div style="
            position: absolute;
            left: 83.33%;
            width: 16.67%;
            height: 100%;
            background: linear-gradient(90deg, #E3F2FD, #64B5F6);
            border-radius: 0 5px 5px 0;
            border: 2px solid #2196F3;
        "></div>
        
        <!-- 현재 시간 마커 -->
        <div style="
            position: absolute;
            left: {current_position}%;
            width: 3px;
            height: 100%;
            background: #E53E3E;
            border-radius: 1px;
        "></div>
        
        <!-- 시간 라벨 -->
        <div style="position: absolute; top: 65px; left: 0%; font-size: 12px; color: #666;">00:00</div>
        <div style="position: absolute; top: 65px; left: 33.33%; font-size: 12px; color: #666;">08:00</div>
        <div style="position: absolute; top: 65px; left: 50%; font-size: 12px; color: #666;">12:00</div>
        <div style="position: absolute; top: 65px; left: 83.33%; font-size: 12px; color: #666;">20:00</div>
        <div style="position: absolute; top: 65px; right: 0%; font-size: 12px; color: #666;">24:00</div>
    </div>
    """.format(current_position=current_total_minutes / 1440 * 100)
    
    st.markdown(timeline_html, unsafe_allow_html=True)
    
    # 범례
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟡 **주간조**: 08:00 ~ 19:59")
    with col2:
        st.markdown("🔵 **야간조**: 20:00 ~ 07:59")
    with col3:
        st.markdown(f"🔴 **현재**: {current_time.strftime('%H:%M')}")

def show_shift_work_calendar(work_date: date = None, days_before: int = 3, days_after: int = 3):
    """교대조 근무 달력 (간단한 형태)"""
    if work_date is None:
        work_date = get_current_shift()['work_date']
    
    st.subheader("📅 교대조 근무 달력")
    
    from datetime import timedelta
    
    # 날짜 범위 생성
    start_date = work_date - timedelta(days=days_before)
    dates = [start_date + timedelta(days=i) for i in range(days_before + days_after + 1)]
    
    # 달력 표시
    cols = st.columns(len(dates))
    
    for i, check_date in enumerate(dates):
        with cols[i]:
            # 해당 날짜의 교대조 정보 계산
            date_shift_info = get_shift_for_time(
                get_vietnam_now().replace(
                    year=check_date.year,
                    month=check_date.month,
                    day=check_date.day,
                    hour=12  # 주간조 시간으로 확인
                )
            )
            
            # 현재 날짜 표시
            is_today = check_date == work_date
            bg_color = "#E8F5E8" if is_today else "#F8F9FA"
            border_color = "#4CAF50" if is_today else "#DEE2E6"
            
            st.markdown(f"""
            <div style="
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 10px;
                text-align: center;
                margin: 2px;
            ">
                <div style="font-size: 14px; font-weight: bold; color: #333;">
                    {check_date.strftime('%m/%d')}
                </div>
                <div style="font-size: 12px; color: #666;">
                    {check_date.strftime('%a')}
                </div>
                <div style="font-size: 16px; margin: 5px 0;">
                    {date_shift_info['shift_type']}조
                </div>
                <div style="font-size: 10px; color: #888;">
                    주간/야간
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_shift_legend():
    """교대조 범례 표시"""
    st.markdown("""
    ### 📋 교대조 안내
    
    **🕐 시간 정의:**
    - **하루**: 08:00 ~ 다음날 07:59
    - **주간조**: 08:00 ~ 19:59 (12시간)
    - **야간조**: 20:00 ~ 07:59 (12시간)
    
    **🏭 교대조 구분:**
    - **A조**: 홀수 날짜 (1일, 3일, 5일...)
    - **B조**: 짝수 날짜 (2일, 4일, 6일...)
    
    **🎯 성과 지표:**
    - **불량률 목표**: 0.02% 이하
    - **검사 효율성**: 95% 이상
    """)

# 편의 함수들
def get_shift_color(work_period: str) -> str:
    """교대조에 따른 색상 반환"""
    return "#FFC107" if work_period == 'DAY' else "#2196F3"

def get_shift_emoji(work_period: str) -> str:
    """교대조에 따른 이모지 반환"""
    return "☀️" if work_period == 'DAY' else "🌙"

def format_shift_display(shift_info: Dict[str, Any], include_date: bool = True) -> str:
    """교대조 정보를 표시용 문자열로 포맷"""
    emoji = get_shift_emoji(shift_info['work_period'])
    if include_date:
        return f"{emoji} {shift_info['work_date']} {shift_info['shift_name']}"
    else:
        return f"{emoji} {shift_info['shift_name']}" 