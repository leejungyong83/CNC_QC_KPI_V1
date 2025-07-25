"""
교대조별 실적분석 페이지
- 주간조/야간조별 상세 분석
- 교대조 간 성과 비교
- 시간대별 품질 트렌드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from utils.shift_analytics import shift_analytics, get_shift_performance
from utils.shift_manager import get_current_shift, shift_manager
from utils.vietnam_timezone import get_vietnam_now
from utils.supabase_client import get_supabase_client

def show_shift_reports():
    """교대조별 실적분석 메인 페이지"""
    st.title("🏭 교대조별 실적분석")
    
    # 현재 교대조 정보
    current_shift = get_current_shift()
    st.info(f"**현재 교대조**: {current_shift['full_shift_name']}")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 오늘 교대조 분석", 
        "📈 주간 교대조 트렌드", 
        "⚖️ 교대조 성과 비교",
        "📋 상세 데이터 조회"
    ])
    
    with tab1:
        show_today_shift_analysis()
    
    with tab2:
        show_weekly_shift_trends()
    
    with tab3:
        show_shift_performance_comparison()
    
    with tab4:
        show_detailed_shift_data()

def show_today_shift_analysis():
    """오늘 교대조별 분석"""
    st.subheader("📊 오늘 교대조별 성과")
    
    # 날짜 선택
    selected_date = st.date_input(
        "📅 분석 대상일",
        value=date.today(),
        help="교대조 분석을 원하는 날짜를 선택하세요"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### ☀️ 주간조 (08:00~19:59)")
        day_data = shift_analytics.get_shift_defect_rate(selected_date, 'DAY')
        
        if day_data['data_status'] == 'success':
            # 주간조 KPI 카드
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                st.metric(
                    "검사건수", 
                    f"{day_data['total_inspections']}건",
                    delta=f"수량: {day_data['total_inspected_qty']}개"
                )
            with subcol2:
                st.metric(
                    "불량률", 
                    f"{day_data['defect_rate']:.3f}%",
                    delta=f"불량: {day_data['total_defect_qty']}개"
                )
            
            st.metric(
                "검사 효율성", 
                f"{day_data['inspection_efficiency']:.1f}%",
                delta="목표: 95%"
            )
            
            # 검사자별 성과
            if day_data['inspector_performance']:
                st.write("**👥 검사자별 성과:**")
                inspector_df = pd.DataFrame(day_data['inspector_performance'])
                st.dataframe(inspector_df, use_container_width=True)
        else:
            st.info("주간조 데이터가 없습니다.")
    
    with col2:
        st.write("### 🌙 야간조 (20:00~07:59)")
        night_data = shift_analytics.get_shift_defect_rate(selected_date, 'NIGHT')
        
        if night_data['data_status'] == 'success':
            # 야간조 KPI 카드
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                st.metric(
                    "검사건수", 
                    f"{night_data['total_inspections']}건",
                    delta=f"수량: {night_data['total_inspected_qty']}개"
                )
            with subcol2:
                st.metric(
                    "불량률", 
                    f"{night_data['defect_rate']:.3f}%",
                    delta=f"불량: {night_data['total_defect_qty']}개"
                )
            
            st.metric(
                "검사 효율성", 
                f"{night_data['inspection_efficiency']:.1f}%",
                delta="목표: 95%"
            )
            
            # 검사자별 성과
            if night_data['inspector_performance']:
                st.write("**👥 검사자별 성과:**")
                inspector_df = pd.DataFrame(night_data['inspector_performance'])
                st.dataframe(inspector_df, use_container_width=True)
        else:
            st.info("야간조 데이터가 없습니다.")
    
    # 교대조 비교 차트
    if day_data['data_status'] == 'success' and night_data['data_status'] == 'success':
        st.markdown("---")
        st.subheader("📊 교대조 비교 차트")
        
        # 비교 데이터 준비
        comparison_data = pd.DataFrame({
            '교대조': ['주간조', '야간조'],
            '검사건수': [day_data['total_inspections'], night_data['total_inspections']],
            '불량률': [day_data['defect_rate'], night_data['defect_rate']],
            '효율성': [day_data['inspection_efficiency'], night_data['inspection_efficiency']]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 검사건수 비교
            fig_inspections = px.bar(
                comparison_data, 
                x='교대조', 
                y='검사건수',
                title="교대조별 검사건수 비교",
                color='교대조',
                color_discrete_map={'주간조': '#FFD700', '야간조': '#4169E1'}
            )
            st.plotly_chart(fig_inspections, use_container_width=True)
        
        with col2:
            # 불량률 비교
            fig_defect = px.bar(
                comparison_data, 
                x='교대조', 
                y='불량률',
                title="교대조별 불량률 비교 (%)",
                color='교대조',
                color_discrete_map={'주간조': '#FFD700', '야간조': '#4169E1'}
            )
            fig_defect.add_hline(y=0.02, line_dash="dash", line_color="red", annotation_text="목표: 0.02%")
            st.plotly_chart(fig_defect, use_container_width=True)

def show_weekly_shift_trends():
    """주간 교대조 트렌드"""
    st.subheader("📈 주간 교대조 트렌드 분석")
    
    # 분석 기간 선택
    col1, col2 = st.columns(2)
    with col1:
        end_date = st.date_input("종료일", value=date.today())
    with col2:
        days = st.slider("분석 기간 (일)", min_value=3, max_value=30, value=7)
    
    # 주간 요약 데이터 조회
    weekly_summary = shift_analytics.get_weekly_shift_summary(end_date, days)
    
    # 주간 총합 표시
    st.subheader("📊 기간별 총합")
    col1, col2, col3, col4 = st.columns(4)
    
    day_totals = weekly_summary['week_totals']['day_shift']
    night_totals = weekly_summary['week_totals']['night_shift']
    
    with col1:
        st.metric(
            "주간조 검사건수",
            f"{day_totals['inspections']}건",
            delta=f"불량률: {day_totals['avg_defect_rate']:.3f}%"
        )
    
    with col2:
        st.metric(
            "야간조 검사건수", 
            f"{night_totals['inspections']}건",
            delta=f"불량률: {night_totals['avg_defect_rate']:.3f}%"
        )
    
    with col3:
        total_inspections = day_totals['inspections'] + night_totals['inspections']
        st.metric("전체 검사건수", f"{total_inspections}건")
    
    with col4:
        total_defect_qty = day_totals['defect_qty'] + night_totals['defect_qty']
        total_inspected_qty = day_totals['inspected_qty'] + night_totals['inspected_qty']
        overall_defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0
        st.metric("전체 불량률", f"{overall_defect_rate:.3f}%")
    
    # 일별 트렌드 차트
    if weekly_summary['daily_summaries']:
        st.subheader("📈 일별 교대조 트렌드")
        
        # 트렌드 데이터 준비
        daily_data = []
        for daily in weekly_summary['daily_summaries']:
            date_str = daily['date'].strftime('%m/%d')
            
            # 주간조 데이터
            if daily['day_shift']['data_status'] == 'success':
                daily_data.append({
                    '날짜': date_str,
                    '교대조': '주간조',
                    '검사건수': daily['day_shift']['total_inspections'],
                    '불량률': daily['day_shift']['defect_rate'],
                    '효율성': daily['day_shift']['inspection_efficiency']
                })
            
            # 야간조 데이터
            if daily['night_shift']['data_status'] == 'success':
                daily_data.append({
                    '날짜': date_str,
                    '교대조': '야간조',
                    '검사건수': daily['night_shift']['total_inspections'],
                    '불량률': daily['night_shift']['defect_rate'],
                    '효율성': daily['night_shift']['inspection_efficiency']
                })
        
        if daily_data:
            trend_df = pd.DataFrame(daily_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 검사건수 트렌드
                fig_trend = px.line(
                    trend_df, 
                    x='날짜', 
                    y='검사건수',
                    color='교대조',
                    title="일별 검사건수 트렌드",
                    markers=True
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            
            with col2:
                # 불량률 트렌드
                fig_defect_trend = px.line(
                    trend_df, 
                    x='날짜', 
                    y='불량률',
                    color='교대조',
                    title="일별 불량률 트렌드 (%)",
                    markers=True
                )
                fig_defect_trend.add_hline(y=0.02, line_dash="dash", line_color="red")
                st.plotly_chart(fig_defect_trend, use_container_width=True)

def show_shift_performance_comparison():
    """교대조 성과 비교"""
    st.subheader("⚖️ 교대조 성과 상세 비교")
    
    # 비교 기간 선택
    comparison_date = st.date_input("비교 대상일", value=date.today())
    
    # 교대조별 상세 비교
    comparison = shift_analytics.compare_shifts_performance(comparison_date)
    
    if 'analysis' in comparison:
        analysis = comparison['analysis']
        
        # 성과 요약
        st.subheader("🏆 성과 요약")
        col1, col2 = st.columns(2)
        
        with col1:
            better_defect = "주간조" if analysis['better_defect_rate'] == 'DAY' else "야간조"
            st.success(f"**불량률 우수**: {better_defect}")
            st.write(f"차이: {analysis['defect_rate_diff']:.3f}%p")
        
        with col2:
            better_efficiency = "주간조" if analysis['better_efficiency'] == 'DAY' else "야간조"
            st.success(f"**효율성 우수**: {better_efficiency}")
            st.write(f"차이: {analysis['efficiency_diff']:.1f}%p")
        
        # 상세 비교 테이블
        st.subheader("📊 상세 비교 데이터")
        
        day_data = comparison['day_shift']
        night_data = comparison['night_shift']
        
        comparison_table = pd.DataFrame({
            '지표': ['검사건수', '검사수량', '불량수량', '불량률(%)', '검사효율성(%)'],
            '주간조': [
                f"{day_data.get('total_inspections', 0)}건",
                f"{day_data.get('total_inspected_qty', 0)}개",
                f"{day_data.get('total_defect_qty', 0)}개",
                f"{day_data.get('defect_rate', 0):.3f}%",
                f"{day_data.get('inspection_efficiency', 0):.1f}%"
            ],
            '야간조': [
                f"{night_data.get('total_inspections', 0)}건",
                f"{night_data.get('total_inspected_qty', 0)}개",
                f"{night_data.get('total_defect_qty', 0)}개",
                f"{night_data.get('defect_rate', 0):.3f}%",
                f"{night_data.get('inspection_efficiency', 0):.1f}%"
            ]
        })
        
        st.dataframe(comparison_table, use_container_width=True)
        
    else:
        st.warning("선택한 날짜의 교대조 데이터가 부족합니다.")

def show_detailed_shift_data():
    """교대조별 상세 데이터 조회"""
    st.subheader("📋 교대조별 상세 데이터")
    
    # 필터 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_date = st.date_input("조회 날짜", value=date.today())
    
    with col2:
        filter_shift = st.selectbox(
            "교대조 선택",
            ["전체", "주간조", "야간조"]
        )
    
    with col3:
        show_details = st.checkbox("상세 정보 표시", value=True)
    
    try:
        supabase = get_supabase_client()
        
        # 날짜 범위 계산
        if filter_shift == "주간조":
            start_time, end_time = shift_manager.get_shift_time_range(filter_date, 'DAY')
        elif filter_shift == "야간조":
            start_time, end_time = shift_manager.get_shift_time_range(filter_date, 'NIGHT')
        else:
            start_time, end_time = shift_manager.get_daily_time_range(filter_date)
        
        # 데이터 조회
        result = supabase.table('inspection_data') \
            .select('*, inspectors(name), production_models(model_name)') \
            .gte('created_at', start_time.isoformat()) \
            .lte('created_at', end_time.isoformat()) \
            .order('created_at', desc=True) \
            .execute()
        
        if result.data:
            # 데이터 프레임 생성
            data_list = []
            for row in result.data:
                inspector_name = row.get('inspectors', {}).get('name', '알 수 없음') if row.get('inspectors') else '알 수 없음'
                model_name = row.get('production_models', {}).get('model_name', '알 수 없음') if row.get('production_models') else '알 수 없음'
                
                data_list.append({
                    '검사일시': row.get('created_at', '')[:19].replace('T', ' '),
                    '교대조': row.get('shift', '미분류'),
                    '검사자': inspector_name,
                    '모델': model_name,
                    '공정': row.get('process', ''),
                    '검사수량': row.get('total_inspected', 0),
                    '불량수량': row.get('defect_quantity', 0),
                    '불량률(%)': round((row.get('defect_quantity', 0) / row.get('total_inspected', 1) * 100), 3),
                    '결과': row.get('result', ''),
                    '비고': row.get('notes', '') or ''
                })
            
            df = pd.DataFrame(data_list)
            
            # 요약 통계
            st.subheader("📊 조회 결과 요약")
            col1, col2, col3, col4 = st.columns(4)
            
            total_inspections = len(df)
            total_qty = df['검사수량'].sum()
            total_defects = df['불량수량'].sum()
            avg_defect_rate = (total_defects / total_qty * 100) if total_qty > 0 else 0
            
            with col1:
                st.metric("총 검사건수", f"{total_inspections}건")
            with col2:
                st.metric("총 검사수량", f"{total_qty:,}개")
            with col3:
                st.metric("총 불량수량", f"{total_defects}개")
            with col4:
                st.metric("평균 불량률", f"{avg_defect_rate:.3f}%")
            
            # 데이터 테이블
            st.subheader("📋 상세 데이터")
            
            if show_details:
                st.dataframe(df, use_container_width=True)
            else:
                # 요약 뷰
                summary_df = df.groupby('교대조').agg({
                    '검사수량': 'sum',
                    '불량수량': 'sum',
                    '불량률(%)': 'mean'
                }).round(3)
                st.dataframe(summary_df, use_container_width=True)
            
            # 데이터 다운로드
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 CSV 다운로드",
                csv,
                f"shift_data_{filter_date}_{filter_shift}.csv",
                "text/csv"
            )
            
        else:
            st.info("선택한 조건에 해당하는 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"데이터 조회 중 오류: {str(e)}")

if __name__ == "__main__":
    show_shift_reports() 