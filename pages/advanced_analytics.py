"""
고급 분석 페이지
트렌드 분석, 예측 분석, 통계적 공정 관리(SPC) 기능 제공
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from utils.advanced_analytics import trend_analyzer, predictive_analyzer, spc_analyzer

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)


def show_advanced_analytics():
    """고급 분석 페이지 표시"""
    st.title("📈 고급 분석")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 트렌드 분석", "🔮 예측 분석", "📉 SPC 관리도", "📋 종합 분석"])
    
    with tab1:
        show_trend_analysis()
    
    with tab2:
        show_predictive_analysis()
    
    with tab3:
        show_spc_analysis()
    
    with tab4:
        show_comprehensive_analysis()


def show_trend_analysis():
    """트렌드 분석 탭"""
    st.subheader("📊 트렌드 분석")
    
    # 분석 기간 설정 (베트남 시간대 기준)
    col1, col2 = st.columns(2)
    vietnam_today = get_vietnam_date()
    
    with col1:
        start_date = st.date_input(
            "시작 날짜",
            value=vietnam_today - timedelta(days=30),
            max_value=vietnam_today
        )
    
    with col2:
        end_date = st.date_input(
            "종료 날짜",
            value=vietnam_today,
            max_value=vietnam_today
        )
    
    if start_date >= end_date:
        st.error("시작 날짜는 종료 날짜보다 이전이어야 합니다.")
        return
    
    # 분석 실행
    if st.button("📈 트렌드 분석 실행", use_container_width=True):
        with st.spinner("트렌드 데이터 분석 중..."):
            analyze_trends(start_date, end_date)
    
    # 기존 결과 표시
    if 'trend_analysis_results' in st.session_state:
        display_trend_results()


def analyze_trends(start_date: date, end_date: date):
    """트렌드 분석 실행"""
    try:
        # 데이터 조회
        df = trend_analyzer.get_trend_data(start_date, end_date)
        
        if df.empty:
            st.warning("선택한 기간에 데이터가 없습니다.")
            return
        
        # 일별 트렌드 계산
        daily_trends = trend_analyzer.calculate_daily_trends(df)
        
        # 이동 평균 계산
        daily_trends_ma = trend_analyzer.calculate_moving_averages(daily_trends)
        
        # 트렌드 변화점 감지
        trend_changes = trend_analyzer.detect_trend_changes(daily_trends_ma, 'defect_rate')
        
        # 결과 저장
        st.session_state.trend_analysis_results = {
            'raw_data': df,
            'daily_trends': daily_trends_ma,
            'trend_changes': trend_changes,
            'period': f"{start_date} ~ {end_date}"
        }
        
        st.success("✅ 트렌드 분석이 완료되었습니다!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 트렌드 분석 실패: {str(e)}")


def display_trend_results():
    """트렌드 분석 결과 표시"""
    results = st.session_state.trend_analysis_results
    daily_trends = results['daily_trends']
    trend_changes = results['trend_changes']
    
    st.write(f"**분석 기간:** {results['period']}")
    
    # 핵심 지표 요약
    st.write("### 📊 핵심 지표 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_defect_rate = daily_trends['defect_rate'].mean()
        st.metric("평균 불량률", f"{avg_defect_rate:.3f}%")
    
    with col2:
        total_inspections = daily_trends['inspection_count'].sum()
        st.metric("총 검사 건수", f"{total_inspections:,}건")
    
    with col3:
        trend_direction = get_trend_direction(daily_trends['defect_rate'])
        st.metric("트렌드 방향", trend_direction)
    
    with col4:
        volatility = daily_trends['defect_rate'].std()
        st.metric("변동성 (표준편차)", f"{volatility:.3f}%")
    
    # 트렌드 차트
    st.write("### 📈 트렌드 차트")
    
    metric_options = {
        "불량률": "defect_rate",
        "합격률": "pass_rate",
        "검사 건수": "inspection_count"
    }
    
    selected_metric = st.selectbox("표시할 지표 선택", list(metric_options.keys()))
    
    fig = trend_analyzer.create_trend_chart(daily_trends, metric_options[selected_metric])
    st.plotly_chart(fig, use_container_width=True)
    
    # 트렌드 변화점
    if trend_changes:
        st.write("### 🔍 트렌드 변화점 감지")
        
        for i, change in enumerate(trend_changes[-5:]):  # 최근 5개만 표시
            if change['change_type'] == "증가":
                st.error(f"📈 **{change['date']}**: 불량률 급증 감지 ({change['value']:.3f}% → 예상: {change['expected']:.3f}%)")
            else:
                st.success(f"📉 **{change['date']}**: 불량률 급감 감지 ({change['value']:.3f}% → 예상: {change['expected']:.3f}%)")
    else:
        st.info("🔍 감지된 트렌드 변화점이 없습니다. 안정적인 상태입니다.")
    
    # 상세 데이터 테이블
    with st.expander("📋 상세 데이터 보기"):
        st.dataframe(daily_trends, use_container_width=True)


def get_trend_direction(values: pd.Series) -> str:
    """트렌드 방향 판단"""
    if len(values) < 2:
        return "데이터 부족"
    
    # 선형 회귀로 기울기 계산
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    
    if slope > 0.01:
        return "🔴 악화"
    elif slope < -0.01:
        return "🟢 개선"
    else:
        return "🟡 안정"


def show_predictive_analysis():
    """예측 분석 탭"""
    st.subheader("🔮 예측 분석")
    
    # 기존 트렌드 분석 결과가 있는지 확인
    if 'trend_analysis_results' not in st.session_state:
        st.warning("⚠️ 먼저 트렌드 분석을 수행해주세요.")
        if st.button("🔄 트렌드 분석 탭으로 이동"):
            st.session_state.selected_tab = 0
            st.rerun()
        return
    
    # 예측 설정
    col1, col2 = st.columns(2)
    
    with col1:
        prediction_days = st.slider(
            "예측 기간 (일)",
            min_value=1,
            max_value=30,
            value=7,
            help="미래 며칠까지 예측할지 선택하세요"
        )
    
    with col2:
        confidence_level = st.slider(
            "신뢰도 (%)",
            min_value=80,
            max_value=99,
            value=95,
            help="예측 신뢰구간의 신뢰도를 설정하세요"
        )
    
    # 예측 실행
    if st.button("🔮 불량률 예측 실행", use_container_width=True):
        execute_prediction_analysis(prediction_days, confidence_level)
    
    # 예측 결과 표시
    if 'prediction_results' in st.session_state:
        display_prediction_results()


def execute_prediction_analysis(days_ahead: int, confidence_level: int):
    """예측 분석 실행"""
    try:
        daily_trends = st.session_state.trend_analysis_results['daily_trends']
        
        with st.spinner(f"향후 {days_ahead}일 불량률 예측 중..."):
            prediction_results = predictive_analyzer.predict_defect_rate(daily_trends, days_ahead)
        
        if 'error' in prediction_results:
            st.error(f"❌ 예측 실패: {prediction_results['error']}")
            return
        
        st.session_state.prediction_results = prediction_results
        st.session_state.prediction_confidence = confidence_level
        
        st.success("✅ 예측 분석이 완료되었습니다!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 예측 분석 실패: {str(e)}")


def display_prediction_results():
    """예측 결과 표시"""
    results = st.session_state.prediction_results
    daily_trends = st.session_state.trend_analysis_results['daily_trends']
    
    # 예측 요약
    st.write("### 🎯 예측 요약")
    
    if 'predictions' in results:
        predictions = results['predictions']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_prediction = np.mean([p['polynomial_prediction'] for p in predictions])
            st.metric("예상 평균 불량률", f"{avg_prediction:.3f}%")
        
        with col2:
            trend_direction = results.get('trend_analysis', '알 수 없음')
            st.metric("예측 트렌드", trend_direction)
        
        with col3:
            model_performance = results.get('model_performance', {})
            best_model = model_performance.get('recommended_model', 'N/A')
            st.metric("최적 모델", best_model.title())
        
        # 예측 차트
        st.write("### 📊 예측 차트")
        
        fig = predictive_analyzer.create_prediction_chart(daily_trends, results)
        st.plotly_chart(fig, use_container_width=True)
        
        # 예측 상세 결과
        st.write("### 📅 일별 예측 결과")
        
        pred_df = pd.DataFrame([
            {
                '날짜': p['date'].strftime('%Y-%m-%d'),
                '예측 불량률 (%)': f"{p['polynomial_prediction']:.3f}",
                '신뢰구간 하한': f"{p['confidence_interval'][0]:.3f}",
                '신뢰구간 상한': f"{p['confidence_interval'][1]:.3f}"
            }
            for p in predictions
        ])
        
        st.dataframe(pred_df, use_container_width=True)
        
        # 예측 신뢰도 정보
        if 'model_performance' in results:
            perf = results['model_performance']
            
            with st.expander("🔍 모델 성능 정보"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**선형 회귀 모델:**")
                    st.write(f"- R² 점수: {perf.get('linear_r2', 0):.3f}")
                
                with col2:
                    st.write("**다항 회귀 모델:**")
                    st.write(f"- R² 점수: {perf.get('polynomial_r2', 0):.3f}")
                
                st.write(f"**권장 모델:** {perf.get('recommended_model', 'N/A').title()}")
                
                if perf.get('polynomial_r2', 0) > 0.7:
                    st.success("✅ 높은 예측 정확도 (R² > 0.7)")
                elif perf.get('polynomial_r2', 0) > 0.5:
                    st.warning("⚠️ 보통 예측 정확도 (0.5 < R² < 0.7)")
                else:
                    st.error("❌ 낮은 예측 정확도 (R² < 0.5)")
        
        # 예측 기반 권고사항
        st.write("### 💡 권고사항")
        
        generate_prediction_recommendations(predictions, results.get('trend_analysis'))


def generate_prediction_recommendations(predictions: list, trend_analysis: str):
    """예측 기반 권고사항 생성"""
    avg_prediction = np.mean([p['polynomial_prediction'] for p in predictions])
    max_prediction = max([p['polynomial_prediction'] for p in predictions])
    
    recommendations = []
    
    if avg_prediction > 3.0:
        recommendations.append("🔴 **긴급**: 예측 불량률이 3%를 초과합니다. 즉시 품질 개선 조치가 필요합니다.")
    elif avg_prediction > 2.0:
        recommendations.append("🟡 **주의**: 예측 불량률이 2%를 초과합니다. 예방 조치를 검토하세요.")
    else:
        recommendations.append("🟢 **양호**: 예측 불량률이 안정적인 수준입니다.")
    
    if trend_analysis == "증가 추세":
        recommendations.append("📈 **트렌드 경고**: 불량률 증가 추세가 감지되었습니다. 원인 분석이 필요합니다.")
    elif trend_analysis == "감소 추세":
        recommendations.append("📉 **개선**: 불량률 감소 추세입니다. 현재 개선 활동을 지속하세요.")
    
    if max_prediction > avg_prediction * 1.5:
        recommendations.append("⚠️ **변동성 주의**: 예측 기간 중 불량률 변동이 클 것으로 예상됩니다.")
    
    for rec in recommendations:
        if "긴급" in rec or "경고" in rec:
            st.error(rec)
        elif "주의" in rec or "변동성" in rec:
            st.warning(rec)
        else:
            st.success(rec)


def show_spc_analysis():
    """SPC 분석 탭"""
    st.subheader("📉 통계적 공정 관리 (SPC)")
    
    # 기존 트렌드 분석 결과가 있는지 확인
    if 'trend_analysis_results' not in st.session_state:
        st.warning("⚠️ 먼저 트렌드 분석을 수행해주세요.")
        return
    
    # SPC 설정
    col1, col2 = st.columns(2)
    
    with col1:
        chart_type = st.selectbox(
            "관리도 유형",
            options=["x_chart", "r_chart"],
            format_func=lambda x: "X-Chart (개별값 차트)" if x == "x_chart" else "R-Chart (범위 차트)"
        )
    
    with col2:
        analysis_metric = st.selectbox(
            "분석 지표",
            options=["defect_rate", "inspection_count"],
            format_func=lambda x: "불량률 (%)" if x == "defect_rate" else "검사 건수"
        )
    
    # SPC 분석 실행
    if st.button("📉 SPC 분석 실행", use_container_width=True):
        execute_spc_analysis(chart_type, analysis_metric)
    
    # SPC 결과 표시
    if 'spc_results' in st.session_state:
        display_spc_results()


def execute_spc_analysis(chart_type: str, metric: str):
    """SPC 분석 실행"""
    try:
        daily_trends = st.session_state.trend_analysis_results['daily_trends']
        data_series = daily_trends[metric]
        
        with st.spinner("SPC 관리도 분석 중..."):
            # 관리한계 계산
            control_limits = spc_analyzer.calculate_control_limits(data_series, chart_type)
            
            if 'error' in control_limits:
                st.error(f"❌ SPC 분석 실패: {control_limits['error']}")
                return
            
            # 관리 이탈점 감지
            out_of_control = spc_analyzer.detect_out_of_control_points(data_series, control_limits)
            
            # 넬슨 규칙 적용
            nelson_violations = spc_analyzer.apply_nelson_rules(data_series, control_limits)
            
            # 모든 위반사항 통합
            all_violations = out_of_control + nelson_violations
            
            # 결과 저장
            st.session_state.spc_results = {
                'control_limits': control_limits,
                'out_of_control': out_of_control,
                'nelson_violations': nelson_violations,
                'all_violations': all_violations,
                'data_series': data_series,
                'dates': daily_trends['date'],
                'metric': metric,
                'chart_type': chart_type
            }
        
        st.success("✅ SPC 분석이 완료되었습니다!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ SPC 분석 실패: {str(e)}")


def display_spc_results():
    """SPC 결과 표시"""
    results = st.session_state.spc_results
    control_limits = results['control_limits']
    all_violations = results['all_violations']
    data_series = results['data_series']
    dates = results['dates']
    metric = results['metric']
    
    # SPC 요약
    st.write("### 📊 SPC 분석 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("중심선 (CL)", f"{control_limits['center_line']:.3f}")
    
    with col2:
        st.metric("상한관리한계 (UCL)", f"{control_limits['ucl']:.3f}")
    
    with col3:
        st.metric("하한관리한계 (LCL)", f"{control_limits['lcl']:.3f}")
    
    with col4:
        out_of_control_count = len([v for v in all_violations if v.get('severity') == 'high'])
        status = "관리 상태" if out_of_control_count == 0 else "관리 이탈"
        st.metric("공정 상태", status)
    
    # 관리도
    st.write("### 📉 SPC 관리도")
    
    fig = spc_analyzer.create_control_chart(
        data_series, 
        control_limits, 
        dates, 
        all_violations
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 위반사항 상세
    if all_violations:
        st.write("### ⚠️ 감지된 위반사항")
        
        for i, violation in enumerate(all_violations):
            if violation.get('severity') == 'high':
                st.error(f"🚨 **위반 {i+1}**: {violation.get('type', violation.get('rule', '알 수 없는 위반'))}")
            elif violation.get('severity') == 'medium':
                st.warning(f"⚠️ **위반 {i+1}**: {violation.get('rule', '알 수 없는 위반')}")
            else:
                st.info(f"ℹ️ **위반 {i+1}**: {violation.get('rule', '알 수 없는 위반')}")
    else:
        st.success("✅ 감지된 위반사항이 없습니다. 공정이 관리 상태에 있습니다.")
    
    # SPC 보고서
    st.write("### 📋 SPC 분석 보고서")
    
    report = spc_analyzer.generate_spc_report(data_series, control_limits, all_violations)
    st.markdown(report)


def show_comprehensive_analysis():
    """종합 분석 탭"""
    st.subheader("📋 종합 분석 보고서")
    
    # 모든 분석 결과가 있는지 확인
    has_trend = 'trend_analysis_results' in st.session_state
    has_prediction = 'prediction_results' in st.session_state
    has_spc = 'spc_results' in st.session_state
    
    if not any([has_trend, has_prediction, has_spc]):
        st.warning("⚠️ 종합 분석을 위해서는 먼저 다른 탭에서 분석을 수행해주세요.")
        return
    
    # 종합 분석 실행
    if st.button("📋 종합 분석 보고서 생성", use_container_width=True):
        generate_comprehensive_report(has_trend, has_prediction, has_spc)
    
    # 종합 보고서 표시
    if 'comprehensive_report' in st.session_state:
        display_comprehensive_report()


def generate_comprehensive_report(has_trend: bool, has_prediction: bool, has_spc: bool):
    """종합 분석 보고서 생성 (베트남 시간대)"""
    report = {
        'generated_at': get_vietnam_display_time(),
        'has_trend': has_trend,
        'has_prediction': has_prediction,
        'has_spc': has_spc,
        'summary': {},
        'recommendations': []
    }
    
    # 트렌드 분석 요약
    if has_trend:
        trend_results = st.session_state.trend_analysis_results
        daily_trends = trend_results['daily_trends']
        
        report['summary']['trend'] = {
            'period': trend_results['period'],
            'avg_defect_rate': daily_trends['defect_rate'].mean(),
            'trend_direction': get_trend_direction(daily_trends['defect_rate']),
            'volatility': daily_trends['defect_rate'].std(),
            'total_inspections': daily_trends['inspection_count'].sum(),
            'change_points': len(trend_results['trend_changes'])
        }
    
    # 예측 분석 요약
    if has_prediction:
        pred_results = st.session_state.prediction_results
        
        if 'predictions' in pred_results:
            predictions = pred_results['predictions']
            
            report['summary']['prediction'] = {
                'avg_predicted_defect_rate': np.mean([p['polynomial_prediction'] for p in predictions]),
                'max_predicted_defect_rate': max([p['polynomial_prediction'] for p in predictions]),
                'trend_analysis': pred_results.get('trend_analysis', '알 수 없음'),
                'model_performance': pred_results.get('model_performance', {}).get('polynomial_r2', 0)
            }
    
    # SPC 분석 요약
    if has_spc:
        spc_results = st.session_state.spc_results
        
        report['summary']['spc'] = {
            'chart_type': spc_results['control_limits']['chart_type'],
            'center_line': spc_results['control_limits']['center_line'],
            'violations_count': len(spc_results['all_violations']),
            'process_status': "관리 상태" if len(spc_results['all_violations']) == 0 else "관리 이탈"
        }
    
    # 종합 권고사항 생성
    report['recommendations'] = generate_comprehensive_recommendations(report['summary'])
    
    st.session_state.comprehensive_report = report
    st.success("✅ 종합 분석 보고서가 생성되었습니다!")
    st.rerun()


def display_comprehensive_report():
    """종합 보고서 표시"""
    report = st.session_state.comprehensive_report
    
    # 보고서 헤더 (베트남 시간 표시)
    st.write(f"**생성 시간:** {report['generated_at'].strftime('%Y-%m-%d %H:%M:%S')} (UTC+7)")
    
    # 분석 범위
    included_analyses = []
    if report['has_trend']:
        included_analyses.append("트렌드 분석")
    if report['has_prediction']:
        included_analyses.append("예측 분석")
    if report['has_spc']:
        included_analyses.append("SPC 분석")
    
    st.write(f"**포함된 분석:** {', '.join(included_analyses)}")
    
    # 핵심 지표 요약
    st.write("### 📊 핵심 지표 요약")
    
    summary = report['summary']
    
    if 'trend' in summary:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("평균 불량률", f"{summary['trend']['avg_defect_rate']:.3f}%")
        
        with col2:
            st.metric("트렌드 방향", summary['trend']['trend_direction'])
        
        with col3:
            st.metric("총 검사 건수", f"{summary['trend']['total_inspections']:,}건")
    
    # 예측 정보
    if 'prediction' in summary:
        st.write("### 🔮 예측 요약")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("예상 평균 불량률", f"{summary['prediction']['avg_predicted_defect_rate']:.3f}%")
        
        with col2:
            st.metric("예측 정확도 (R²)", f"{summary['prediction']['model_performance']:.3f}")
    
    # SPC 상태
    if 'spc' in summary:
        st.write("### 📉 SPC 상태")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("공정 상태", summary['spc']['process_status'])
        
        with col2:
            st.metric("위반사항", f"{summary['spc']['violations_count']}건")
    
    # 종합 권고사항
    st.write("### 💡 종합 권고사항")
    
    for i, recommendation in enumerate(report['recommendations'], 1):
        priority = recommendation['priority']
        message = recommendation['message']
        
        if priority == 'high':
            st.error(f"**{i}. [긴급]** {message}")
        elif priority == 'medium':
            st.warning(f"**{i}. [중요]** {message}")
        else:
            st.info(f"**{i}. [권장]** {message}")
    
    # 상세 데이터 다운로드
    st.write("---")
    
    if st.button("📊 상세 분석 데이터 다운로드", use_container_width=True):
        download_analysis_data()


def generate_comprehensive_recommendations(summary: dict) -> list:
    """종합 권고사항 생성"""
    recommendations = []
    
    # 트렌드 기반 권고사항
    if 'trend' in summary:
        trend_data = summary['trend']
        
        if trend_data['avg_defect_rate'] > 3.0:
            recommendations.append({
                'priority': 'high',
                'message': f"평균 불량률이 {trend_data['avg_defect_rate']:.3f}%로 높습니다. 즉시 품질 개선 조치가 필요합니다."
            })
        
        if "악화" in trend_data['trend_direction']:
            recommendations.append({
                'priority': 'high',
                'message': "불량률 악화 추세가 감지되었습니다. 원인 분석 및 개선 조치를 시급히 수행하세요."
            })
        
        if trend_data['volatility'] > 1.0:
            recommendations.append({
                'priority': 'medium',
                'message': f"불량률 변동성이 높습니다 (표준편차: {trend_data['volatility']:.3f}%). 공정 안정화가 필요합니다."
            })
    
    # 예측 기반 권고사항
    if 'prediction' in summary:
        pred_data = summary['prediction']
        
        if pred_data['avg_predicted_defect_rate'] > 2.5:
            recommendations.append({
                'priority': 'medium',
                'message': f"향후 예상 불량률이 {pred_data['avg_predicted_defect_rate']:.3f}%입니다. 예방 조치를 검토하세요."
            })
        
        if pred_data['model_performance'] < 0.5:
            recommendations.append({
                'priority': 'low',
                'message': "예측 모델의 정확도가 낮습니다. 더 많은 데이터 수집을 권장합니다."
            })
    
    # SPC 기반 권고사항
    if 'spc' in summary:
        spc_data = summary['spc']
        
        if spc_data['process_status'] == "관리 이탈":
            recommendations.append({
                'priority': 'high',
                'message': f"공정이 관리 이탈 상태입니다 ({spc_data['violations_count']}건 위반). 공정 조정이 필요합니다."
            })
        else:
            recommendations.append({
                'priority': 'low',
                'message': "공정이 관리 상태에 있습니다. 현재 수준을 유지하세요."
            })
    
    # 기본 권고사항
    if not recommendations:
        recommendations.append({
            'priority': 'low',
            'message': "현재 모든 지표가 양호한 상태입니다. 지속적인 모니터링을 유지하세요."
        })
    
    return recommendations


def download_analysis_data():
    """분석 데이터 다운로드"""
    try:
        # 모든 분석 결과를 Excel 파일로 생성
        import io
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # 트렌드 데이터
            if 'trend_analysis_results' in st.session_state:
                trend_data = st.session_state.trend_analysis_results['daily_trends']
                trend_data.to_excel(writer, sheet_name='트렌드분석', index=False)
            
            # 예측 데이터
            if 'prediction_results' in st.session_state and 'predictions' in st.session_state.prediction_results:
                pred_data = st.session_state.prediction_results['predictions']
                pred_df = pd.DataFrame([
                    {
                        '날짜': p['date'],
                        '예측_불량률': p['polynomial_prediction'],
                        '신뢰구간_하한': p['confidence_interval'][0],
                        '신뢰구간_상한': p['confidence_interval'][1]
                    }
                    for p in pred_data
                ])
                pred_df.to_excel(writer, sheet_name='예측분석', index=False)
            
            # SPC 데이터
            if 'spc_results' in st.session_state:
                spc_data = st.session_state.spc_results
                spc_df = pd.DataFrame({
                    '날짜': spc_data['dates'],
                    '측정값': spc_data['data_series'],
                    '중심선': spc_data['control_limits']['center_line'],
                    '상한관리한계': spc_data['control_limits']['ucl'],
                    '하한관리한계': spc_data['control_limits']['lcl']
                })
                spc_df.to_excel(writer, sheet_name='SPC분석', index=False)
        
        excel_data = output.getvalue()
        
        vietnam_time = get_vietnam_display_time()
        st.download_button(
            label="📊 Excel 파일 다운로드",
            data=excel_data,
            file_name=f"고급분석결과_{vietnam_time.strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.success("✅ 분석 데이터 다운로드가 준비되었습니다!")
        
    except Exception as e:
        st.error(f"❌ 데이터 다운로드 실패: {str(e)}")


if __name__ == "__main__":
    show_advanced_analytics() 