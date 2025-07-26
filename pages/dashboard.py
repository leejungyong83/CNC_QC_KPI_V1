import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import numpy as np
from utils.supabase_client import get_supabase_client
from utils.vietnam_timezone import get_vietnam_now, get_vietnam_display_time, get_vietnam_date
from utils.data_converter import convert_supabase_data_timezone, convert_dataframe_timezone
from utils.defect_utils import get_defect_type_names
from utils.shift_manager import get_current_shift, get_shift_for_time
from utils.shift_analytics import shift_analytics, get_today_defect_rate
from utils.shift_ui_components import (
    show_current_shift_banner, 
    show_shift_status_indicator,
    show_shift_comparison_cards,
    show_shift_timeline
)

def show_dashboard():
    """대시보드 메인 페이지"""
    st.title("📊 CNC QC KPI 대시보드")
    
    # 현재 교대조 정보 배너
    show_current_shift_banner()
    
    # 교대조 타임라인
    with st.expander("🕐 오늘 교대조 타임라인", expanded=False):
        show_shift_timeline()
    
    # KPI 메트릭 표시
    try:
        # 교대조 기준 오늘 KPI 계산
        today_kpi = get_today_defect_rate()
        
        if today_kpi['data_status'] == 'success':
            # KPI 카드 표시
            col1, col2, col3, col4 = st.columns(4)
            
            
            with col1:
                st.metric(
                    label="📊 오늘 불량률",
                    value=f"{today_kpi['defect_rate']:.3f}%",
                    delta=f"목표: 0.02%" if today_kpi['defect_rate'] <= 0.02 else f"+{today_kpi['defect_rate']-0.02:.3f}%",
                    delta_color="normal" if today_kpi['defect_rate'] <= 0.02 else "inverse"
                )
            
            with col2:
                st.metric(
                    label="🎯 검사 효율성",
                    value=f"{today_kpi['inspection_efficiency']:.1f}%",
                    delta=f"목표: 95%" if today_kpi['inspection_efficiency'] >= 95 else f"{today_kpi['inspection_efficiency']-95:.1f}%",
                    delta_color="normal" if today_kpi['inspection_efficiency'] >= 95 else "inverse"
                )
            
            with col3:
                st.metric(
                    label="📝 총 검사건수",
                    value=f"{today_kpi['total_inspections']}건",
                    delta=f"검사수량: {today_kpi['total_inspected_qty']}개"
                )
            
            with col4:
                st.metric(
                    label="❌ 불량수량",
                    value=f"{today_kpi['total_defect_qty']}개",
                    delta=f"작업일: {today_kpi['work_date']}"
                )
            
            # 시간 범위 정보
            st.caption(f"📅 집계 기준: {today_kpi['period']} (하루 = 08:00~다음날 07:59)")
            
        else:
            st.warning("⚠️ 오늘 검사 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"❌ KPI 데이터 로딩 오류: {str(e)}")
        # 폴백으로 기존 KPI 표시
        show_fallback_kpi()
    
    # 추가 KPI 정보 (수량 기준)
    if today_kpi.get('data_status') == 'success' and today_kpi.get('total_inspected_qty', 0) > 0:
        total_qty = today_kpi['total_inspected_qty']
        pass_qty = total_qty - today_kpi['total_defect_qty']
        quantity_pass_rate = (pass_qty / total_qty * 100) if total_qty > 0 else 0
        st.info(f"📊 **수량 기준 합격률**: {quantity_pass_rate:.1f}% (합격: {pass_qty:,}개 / 총검사: {total_qty:,}개)")
    
    # BEST/WORST 검사자 섹션 추가
    st.markdown("---")
    show_inspector_performance()
    
    # 교대조별 성과 비교 섹션 (개선된 UI)
    st.markdown("---")
    show_enhanced_shift_comparison()
    
    # 기간 선택기 및 차트들
    st.markdown("---")
    show_dashboard_charts()

def show_inspector_performance():
    """BEST/WORST 검사자 성과 표시"""
    st.subheader("🏆 검사자 성과")
    
    try:
        # 실제 데이터 조회
        performance_data = get_inspector_performance_data()
        
        if performance_data and len(performance_data) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # BEST 검사자 (첫 번째 = 합격률 최고)
                best_inspector = performance_data[0]
                st.success("🏅 **BEST 검사자**")
                st.write(f"👤 **{best_inspector['name']}** ({best_inspector['employee_id']})")
                st.write(f"✅ 합격률: **{best_inspector['pass_rate']:.1f}%**")
                st.write(f"📊 검사 건수: **{best_inspector['total_inspections']}건**")
                st.write(f"🎯 불량률: **{best_inspector['defect_rate']:.2f}%**")
            
            with col2:
                # WORST 검사자 (마지막 = 합격률 최저, 단 2명 이상인 경우만)
                if len(performance_data) > 1:
                    worst_inspector = performance_data[-1]
                    st.warning("📈 **개선 필요 검사자**")
                    st.write(f"👤 **{worst_inspector['name']}** ({worst_inspector['employee_id']})")
                    st.write(f"❌ 합격률: **{worst_inspector['pass_rate']:.1f}%**")
                    st.write(f"📊 검사 건수: **{worst_inspector['total_inspections']}건**")
                    st.write(f"🎯 불량률: **{worst_inspector['defect_rate']:.2f}%**")
                else:
                    st.info("📊 **단일 검사자**")
                    st.write("비교할 다른 검사자가 없습니다.")
            
            # 전체 검사자 성과 요약 (접을 수 있는 형태)
            if len(performance_data) > 2:
                with st.expander(f"📊 전체 검사자 성과 순위 ({len(performance_data)}명)"):
                    for i, data in enumerate(performance_data, 1):
                        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}위"
                        st.write(f"{rank_emoji} {data['name']} ({data['employee_id']}) - 합격률: {data['pass_rate']:.1f}%, 검사건수: {data['total_inspections']}건")
        else:
            # 실제 데이터가 없을 때 기본 안내
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("📊 **BEST 검사자**")
                st.write("검사 실적 데이터가 없습니다.")
                
            with col2:
                st.info("📊 **개선 필요 검사자**")
                st.write("검사 실적 데이터가 없습니다.")
            
            st.warning("⚠️ 검사자 성과를 확인하려면 검사 실적을 먼저 입력해주세요.")
            st.info("💡 '📝 검사데이터입력' 메뉴에서 검사 실적을 추가할 수 있습니다.")
            
    except Exception as e:
        st.error(f"❌ 검사자 성과 데이터 조회 중 오류: {str(e)}")
        
        # 에러 발생 시에도 기본 안내 제공
        with st.expander("🔧 문제 해결 방법"):
            st.write("**가능한 원인:**")
            st.write("- Supabase 데이터베이스 연결 문제")
            st.write("- inspectors 또는 inspection_data 테이블이 없음")
            st.write("- 검사 실적 데이터가 없음")
            st.write("")
            st.write("**해결 방법:**")
            st.write("1. 'Supabase 설정' 메뉴에서 데이터베이스 연결 확인")
            st.write("2. '검사자 등록 및 관리' 메뉴에서 검사자 등록")
            st.write("3. '📝 검사데이터입력' 메뉴에서 검사 실적 입력")

def show_kpi_alerts():
    """KPI 알림 표시"""
    st.subheader("🚨 KPI 알림")
    
    try:
        # 실제 KPI 데이터 계산
        kpi_data = calculate_kpi_data()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 불량율 KPI
            current_defect_rate = kpi_data['defect_rate']
            target_defect_rate = 0.02  # 목표 불량율 0.02%
            
            if current_defect_rate <= target_defect_rate:
                st.success(f"✅ **불량율 목표 달성**")
                st.write(f"🎯 목표: **{target_defect_rate}%**")
                st.write(f"📊 현재: **{current_defect_rate:.3f}%**")
                st.write(f"📈 달성률: **{((target_defect_rate - current_defect_rate) / target_defect_rate * 100):.1f}% 초과 달성**")
            else:
                st.error(f"❌ **불량율 목표 미달성**")
                st.write(f"🎯 목표: **{target_defect_rate}%**")
                st.write(f"📊 현재: **{current_defect_rate:.3f}%**")
                st.write(f"⚠️ 개선 필요: **{(current_defect_rate - target_defect_rate):.3f}%p**")
        
        with col2:
            # 검사효율성 KPI
            current_efficiency = kpi_data['inspection_efficiency']
            target_efficiency = 95.0  # 목표 검사효율 95%
            
            if current_efficiency >= target_efficiency:
                st.success(f"✅ **검사효율성 목표 달성**")
                st.write(f"🎯 목표: **{target_efficiency}%**")
                st.write(f"📊 현재: **{current_efficiency:.1f}%**")
                st.write(f"📈 달성률: **{(current_efficiency / target_efficiency * 100):.1f}%**")
            else:
                st.warning(f"⚠️ **검사효율성 목표 미달성**")
                st.write(f"🎯 목표: **{target_efficiency}%**")
                st.write(f"📊 현재: **{current_efficiency:.1f}%**")
                st.write(f"📉 부족분: **{(target_efficiency - current_efficiency):.1f}%p**")
                
    except Exception as e:
        st.error(f"KPI 데이터 계산 중 오류: {str(e)}")

def show_enhanced_shift_comparison():
    """개선된 교대조별 성과 비교 표시"""
    st.subheader("🏭 오늘 교대조별 성과 비교")
    
    try:
        # 오늘 교대조별 데이터 조회
        comparison = shift_analytics.compare_shifts_performance()
        
        # 교대조 상태 표시기
        show_shift_status_indicator(compact=True)
        
        # 교대조 비교 카드
        show_shift_comparison_cards(
            comparison['day_shift'], 
            comparison['night_shift']
        )
        
        # 분석 결과 표시
        if 'analysis' in comparison:
            analysis = comparison['analysis']
            
            col1, col2 = st.columns(2)
            
            with col1:
                better_defect = "주간조" if analysis['better_defect_rate'] == 'DAY' else "야간조"
                better_emoji = "☀️" if analysis['better_defect_rate'] == 'DAY' else "🌙"
                st.success(f"🏆 **불량률 우수**: {better_emoji} {better_defect}")
                st.caption(f"차이: {analysis['defect_rate_diff']:.3f}%p")
            
            with col2:
                better_efficiency = "주간조" if analysis['better_efficiency'] == 'DAY' else "야간조"
                better_emoji = "☀️" if analysis['better_efficiency'] == 'DAY' else "🌙"
                st.success(f"🏆 **효율성 우수**: {better_emoji} {better_efficiency}")
                st.caption(f"차이: {analysis['efficiency_diff']:.1f}%p")
                
    except Exception as e:
        st.error(f"교대조 비교 데이터 로딩 오류: {str(e)}")

def show_fallback_kpi():
    """폴백 KPI 표시 (기존 방식)"""
    try:
        # 기존 KPI 계산 방식 사용
        kpi_data = calculate_kpi_data()
        
        if kpi_data.get('data_status') == 'success':
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📈 불량률", 
                    value=f"{kpi_data['defect_rate']:.3f}%",
                    delta=f"목표: 0.02%"
                )
            
            with col2:
                st.metric(
                    label="🎯 검사 효율성", 
                    value=f"{kpi_data['inspection_efficiency']:.1f}%",
                    delta=f"목표: 95%"
                )
            
            with col3:
                st.metric(
                    label="📊 총 검사건수", 
                    value=f"{kpi_data['total_inspections']}건"
                )
            
            with col4:
                st.metric(
                    label="📦 총 검사수량", 
                    value=f"{kpi_data['total_inspected_qty']:,}개"
                )
            
            st.caption("📅 기준: 최근 30일 데이터")
            
    except Exception as e:
        st.error(f"폴백 KPI 로딩 오류: {str(e)}")

def show_dashboard_charts():
    """대시보드 차트 표시 - 교대조별 분석 포함"""
    # 기간 선택기
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "기간 선택",
            ["일별", "주별", "월별"]
        )
    with col2:
        date_range = st.date_input(
            "날짜 범위",
            [pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now()]
        )
    
    # 탭 구성 (교대조 분석 탭 추가)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 검사 현황", 
        "❌ 불량 현황", 
        "🏭 교대조 KPI",
        "🔧 설비별 현황", 
        "📦 모델별 현황"
    ])
    
    with tab1:
        st.subheader("검사 건수 추이")
        # 검사 건수 데이터 (예시)
        chart_data = pd.DataFrame({
            "날짜": pd.date_range(start="2023-01-01", periods=30),
            "검사 건수": [40, 42, 45, 47, 38, 39, 41, 43, 46, 48, 
                      50, 49, 47, 45, 43, 44, 45, 47, 49, 51,
                      50, 48, 46, 45, 44, 46, 48, 49, 50, 52]
        })
        fig = px.line(chart_data, x="날짜", y="검사 건수", title="일별 검사 건수")
        st.plotly_chart(fig, use_container_width=True)
        
        # 불량률 추이
        defect_rate_data = pd.DataFrame({
            "날짜": pd.date_range(start="2023-01-01", periods=30),
            "불량률": np.random.normal(2.5, 0.8, 30)  # 평균 2.5%, 표준편차 0.8%
        })
        fig_defect = px.line(defect_rate_data, x="날짜", y="불량률", title="일별 불량률 추이")
        fig_defect.add_hline(y=0.02, line_dash="dash", line_color="red", annotation_text="목표 불량률 0.02%")
        st.plotly_chart(fig_defect, use_container_width=True)
        
    with tab2:
        st.subheader("불량 현황")
        
        # 불량 유형별 분포
        defect_types = ["치수 불량", "외관 불량", "기능 불량", "표면 불량"]
        defect_counts = [25, 15, 8, 12]
        
        fig_pie = px.pie(
            values=defect_counts, 
            names=defect_types, 
            title="불량 유형별 분포"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # 불량 발생 추이
        st.subheader("월별 불량 발생 추이")
        monthly_data = pd.DataFrame({
            "월": ["1월", "2월", "3월", "4월", "5월", "6월"],
            "불량 건수": [45, 38, 52, 41, 33, 47]
        })
        fig_bar = px.bar(monthly_data, x="월", y="불량 건수", title="월별 불량 발생 건수")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab3:
        show_shift_kpi_analysis()
        
    with tab4:
        st.subheader("설비별 현황")
        st.info("설비별 데이터 기능은 추후 업데이트 예정입니다.")
        
    with tab5:
        st.subheader("모델별 현황")
        st.info("모델별 상세 분석 기능은 추후 업데이트 예정입니다.")

def show_shift_kpi_analysis():
    """교대조별 KPI 상세 분석"""
    st.subheader("🏭 교대조별 KPI 분석")
    
    # 분석 기간 선택
    col1, col2 = st.columns(2)
    with col1:
        analysis_days = st.slider("분석 기간 (일)", min_value=1, max_value=30, value=7)
    with col2:
        end_date = st.date_input("종료일", value=date.today())
    
    try:
        # 주간 교대조 요약 데이터
        weekly_summary = shift_analytics.get_weekly_shift_summary(end_date, analysis_days)
        
        # 기간별 KPI 요약
        st.subheader("📊 기간별 KPI 요약")
        
        day_totals = weekly_summary['week_totals']['day_shift']
        night_totals = weekly_summary['week_totals']['night_shift']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "주간조 평균 불량률",
                f"{day_totals['avg_defect_rate']:.3f}%",
                delta=f"목표: 0.02%"
            )
        
        with col2:
            st.metric(
                "야간조 평균 불량률", 
                f"{night_totals['avg_defect_rate']:.3f}%",
                delta=f"목표: 0.02%"
            )
        
        with col3:
            total_inspections = day_totals['inspections'] + night_totals['inspections']
            day_ratio = (day_totals['inspections'] / total_inspections * 100) if total_inspections > 0 else 0
            st.metric(
                "주간조 검사 비율",
                f"{day_ratio:.1f}%",
                delta=f"{day_totals['inspections']}건"
            )
        
        with col4:
            night_ratio = (night_totals['inspections'] / total_inspections * 100) if total_inspections > 0 else 0
            st.metric(
                "야간조 검사 비율",
                f"{night_ratio:.1f}%", 
                delta=f"{night_totals['inspections']}건"
            )
        
        # 교대조별 성과 비교 차트
        if weekly_summary['daily_summaries']:
            st.subheader("📈 교대조별 성과 트렌드")
            
            # 데이터 준비
            trend_data = []
            for daily in weekly_summary['daily_summaries']:
                date_str = daily['date'].strftime('%m/%d')
                
                if daily['day_shift']['data_status'] == 'success':
                    trend_data.append({
                        '날짜': date_str,
                        '교대조': '주간조',
                        '불량률': daily['day_shift']['defect_rate'],
                        '검사건수': daily['day_shift']['total_inspections'],
                        '효율성': daily['day_shift']['inspection_efficiency']
                    })
                
                if daily['night_shift']['data_status'] == 'success':
                    trend_data.append({
                        '날짜': date_str,
                        '교대조': '야간조',
                        '불량률': daily['night_shift']['defect_rate'],
                        '검사건수': daily['night_shift']['total_inspections'],
                        '효율성': daily['night_shift']['inspection_efficiency']
                    })
            
            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                
                # 차트 배치
                col1, col2 = st.columns(2)
                
                with col1:
                    # 불량률 비교 차트
                    fig_defect = px.line(
                        trend_df, 
                        x='날짜', 
                        y='불량률',
                        color='교대조',
                        title="교대조별 불량률 추이 (%)",
                        markers=True,
                        color_discrete_map={'주간조': '#FFD700', '야간조': '#4169E1'}
                    )
                    fig_defect.add_hline(y=0.02, line_dash="dash", line_color="red", annotation_text="목표: 0.02%")
                    st.plotly_chart(fig_defect, use_container_width=True)
                
                with col2:
                    # 검사건수 비교 차트
                    fig_inspections = px.bar(
                        trend_df, 
                        x='날짜', 
                        y='검사건수',
                        color='교대조',
                        title="교대조별 검사건수 추이",
                        barmode='group',
                        color_discrete_map={'주간조': '#FFD700', '야간조': '#4169E1'}
                    )
                    st.plotly_chart(fig_inspections, use_container_width=True)
                
                # 효율성 비교
                fig_efficiency = px.line(
                    trend_df, 
                    x='날짜', 
                    y='효율성',
                    color='교대조',
                    title="교대조별 검사 효율성 추이 (%)",
                    markers=True,
                    color_discrete_map={'주간조': '#FFD700', '야간조': '#4169E1'}
                )
                fig_efficiency.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="목표: 95%")
                st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # 교대조별 상세 통계
        st.subheader("📋 교대조별 상세 통계")
        
        # 통계 테이블 생성
        stats_data = {
            '지표': [
                '총 검사건수',
                '총 검사수량', 
                '총 불량수량',
                '평균 불량률 (%)',
                '불량률 표준편차',
                '최고 불량률 (%)',
                '최저 불량률 (%)'
            ],
            '주간조': [
                f"{day_totals['inspections']}건",
                f"{day_totals['inspected_qty']:,}개",
                f"{day_totals['defect_qty']}개", 
                f"{day_totals['avg_defect_rate']:.3f}%",
                "계산 중...",  # 실제로는 표준편차 계산 필요
                "계산 중...",  # 실제로는 최고값 계산 필요
                "계산 중..."   # 실제로는 최저값 계산 필요
            ],
            '야간조': [
                f"{night_totals['inspections']}건",
                f"{night_totals['inspected_qty']:,}개",
                f"{night_totals['defect_qty']}개",
                f"{night_totals['avg_defect_rate']:.3f}%",
                "계산 중...",
                "계산 중...",
                "계산 중..."
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
        
        # KPI 목표 달성률
        st.subheader("🎯 KPI 목표 달성률")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**주간조 목표 달성률**")
            day_defect_achievement = (0.02 / day_totals['avg_defect_rate'] * 100) if day_totals['avg_defect_rate'] > 0 else 100
            day_defect_achievement = min(100, day_defect_achievement)
            
            st.progress(day_defect_achievement / 100, text=f"불량률 목표: {day_defect_achievement:.1f}%")
            
            if day_totals['avg_defect_rate'] <= 0.02:
                st.success("✅ 불량률 목표 달성!")
            else:
                st.warning(f"⚠️ 목표 대비 {day_totals['avg_defect_rate'] - 0.02:.3f}%p 초과")
        
        with col2:
            st.write("**야간조 목표 달성률**")
            night_defect_achievement = (0.02 / night_totals['avg_defect_rate'] * 100) if night_totals['avg_defect_rate'] > 0 else 100
            night_defect_achievement = min(100, night_defect_achievement)
            
            st.progress(night_defect_achievement / 100, text=f"불량률 목표: {night_defect_achievement:.1f}%")
            
            if night_totals['avg_defect_rate'] <= 0.02:
                st.success("✅ 불량률 목표 달성!")
            else:
                st.warning(f"⚠️ 목표 대비 {night_totals['avg_defect_rate'] - 0.02:.3f}%p 초과")
    
    except Exception as e:
        st.error(f"교대조 KPI 분석 오류: {str(e)}")
        st.info("교대조별 데이터가 충분하지 않습니다. 검사 데이터를 더 입력해주세요.")

def get_inspector_performance_data():
    """검사자별 성과 데이터 조회 - 성능 최적화된 버전"""
    # 성능 최적화된 버전 사용
    try:
        from utils.performance_optimizer import query_optimizer
        return query_optimizer.get_optimized_inspector_performance()
    except ImportError:
        # 폴백: 기존 방식
        return get_inspector_performance_data_fallback()

def get_inspector_performance_data_fallback():
    """검사자별 성과 데이터 조회 - 실제 데이터베이스에서 (기존 버전)"""
    try:
        supabase = get_supabase_client()
        
        # 1. 검사 데이터 조회 (시간대 변환 적용)
        inspection_result = supabase.table('inspection_data').select('*').execute()
        if inspection_result.data:
            inspections = convert_supabase_data_timezone(inspection_result.data)
        else:
            inspections = []
        
        # 2. 검사자 정보 조회 (시간대 변환 적용)
        inspectors_result = supabase.table('inspectors').select('*').execute()
        if inspectors_result.data:
            inspectors_data = convert_supabase_data_timezone(inspectors_result.data)
            inspectors = {insp['id']: insp for insp in inspectors_data}
        else:
            inspectors = {}
        
        if not inspections or not inspectors:
            return None
        
        # 3. 검사자별 성과 계산
        inspector_stats = {}
        
        for inspection in inspections:
            inspector_id = inspection.get('inspector_id')
            if not inspector_id or inspector_id not in inspectors:
                continue
                
            if inspector_id not in inspector_stats:
                inspector_stats[inspector_id] = {
                    'name': inspectors[inspector_id]['name'],
                    'employee_id': inspectors[inspector_id].get('employee_id', 'N/A'),
                    'total_inspections': 0,
                    'pass_count': 0,
                    'total_inspected_qty': 0,
                    'total_defect_qty': 0
                }
            
            stats = inspector_stats[inspector_id]
            stats['total_inspections'] += 1
            
            if inspection.get('result') == '합격':
                stats['pass_count'] += 1
            
            # 수량 정보
            inspected_qty = inspection.get('total_inspected') or inspection.get('quantity') or 0
            defect_qty = inspection.get('defect_quantity') or 0
            
            stats['total_inspected_qty'] += inspected_qty
            stats['total_defect_qty'] += defect_qty
        
        # 4. 성과 지표 계산 및 정렬
        performance_data = []
        for inspector_id, stats in inspector_stats.items():
            if stats['total_inspections'] > 0:
                pass_rate = (stats['pass_count'] / stats['total_inspections']) * 100
                defect_rate = (stats['total_defect_qty'] / stats['total_inspected_qty'] * 100) if stats['total_inspected_qty'] > 0 else 0
                
                performance_data.append({
                    'name': stats['name'],
                    'employee_id': stats['employee_id'],
                    'total_inspections': stats['total_inspections'],
                    'pass_rate': pass_rate,
                    'defect_rate': defect_rate
                })
        
        # 합격률 기준으로 내림차순 정렬
        performance_data.sort(key=lambda x: x['pass_rate'], reverse=True)
        
        return performance_data if performance_data else None
        
    except Exception as e:
        st.error(f"검사자 성과 데이터 조회 실패: {str(e)}")
        return None

def calculate_kpi_data():
    """KPI 데이터 계산 - 성능 최적화된 버전"""
    # 성능 최적화된 버전 사용
    try:
        from utils.performance_optimizer import query_optimizer
        return query_optimizer.get_optimized_kpi_data()
    except ImportError:
        # 폴백: 기존 방식
        return calculate_kpi_data_fallback()

def calculate_kpi_data_fallback():
    """KPI 데이터 계산 - 실제 데이터베이스에서 (기존 버전)"""
    try:
        supabase = get_supabase_client()
        
        # 검사 데이터 조회 (최근 30일)
        from datetime import datetime, timedelta
        thirty_days_ago = (get_vietnam_now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 더 효율적인 쿼리: 필요한 컬럼만 조회
        inspection_result = supabase.table('inspection_data') \
            .select('result, total_inspected, defect_quantity, pass_quantity, quantity') \
            .gte('inspection_date', thirty_days_ago) \
            .execute()
        
        inspections = inspection_result.data if inspection_result.data else []
        
        # 데이터가 없을 때 기본값 반환 (에러 대신 정보성 메시지)
        if not inspections:
            return {
                'defect_rate': 0.0,
                'inspection_efficiency': 0.0,
                'total_inspections': 0,
                'pass_count': 0,
                'total_inspected_qty': 0,
                'total_defect_qty': 0,
                'data_status': 'no_data'
            }
        
        # KPI 계산 (개선된 로직)
        total_inspections = len(inspections)
        pass_count = 0
        total_inspected_qty = 0
        total_defect_qty = 0
        total_pass_qty = 0
        
        for inspection in inspections:
            # 합격 건수
            if inspection.get('result') == '합격':
                pass_count += 1
            
            # 수량 정보 (우선순위: total_inspected > quantity > 0)
            inspected_qty = inspection.get('total_inspected') or inspection.get('quantity') or 0
            defect_qty = inspection.get('defect_quantity') or 0
            pass_qty = inspection.get('pass_quantity') or 0
            
            # 데이터 정합성 체크
            if defect_qty > inspected_qty:
                defect_qty = inspected_qty  # 불량수량이 총 검사수량보다 클 수 없음
            
            if pass_qty == 0 and inspected_qty > 0:
                pass_qty = inspected_qty - defect_qty  # 합격수량이 없으면 계산
            
            total_inspected_qty += inspected_qty
            total_defect_qty += defect_qty
            total_pass_qty += pass_qty
        
        # KPI 계산 (개선된 공식)
        # 1. 불량률: 불량 수량 / 총 검사 수량 * 100
        defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
        
        # 2. 검사효율성: 합격 건수 / 총 검사 건수 * 100 (건수 기준)
        inspection_efficiency = (pass_count / total_inspections * 100) if total_inspections > 0 else 0.0
        
        # 3. 수량 기준 합격률: 합격 수량 / 총 검사 수량 * 100
        quantity_pass_rate = (total_pass_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
        
        return {
            'defect_rate': round(defect_rate, 3),
            'inspection_efficiency': round(inspection_efficiency, 1),
            'quantity_pass_rate': round(quantity_pass_rate, 1),
            'total_inspections': total_inspections,
            'pass_count': pass_count,
            'total_inspected_qty': total_inspected_qty,
            'total_defect_qty': total_defect_qty,
            'total_pass_qty': total_pass_qty,
            'data_status': 'success'
        }
        
    except Exception as e:
        # 에러 상황에서도 기본 구조 유지
        error_msg = str(e)
        
        # 연결 문제인지 데이터 문제인지 구분
        if "does not exist" in error_msg:
            data_status = 'table_missing'
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            data_status = 'connection_error'
        else:
            data_status = 'unknown_error'
        
        return {
            'defect_rate': 0.0,
            'inspection_efficiency': 0.0,
            'quantity_pass_rate': 0.0,
            'total_inspections': 0,
            'pass_count': 0,
            'total_inspected_qty': 0,
            'total_defect_qty': 0,
            'total_pass_qty': 0,
            'data_status': data_status,
            'error_message': error_msg
        } 
