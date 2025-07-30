"""
📊 기본 분석 페이지 (ML 라이브러리 불필요)
2025-07-30 추가

numpy, pandas만으로 구현한 기본 분석 기능
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.language_manager import t

def show_analytics_basic():
    """기본 분석 페이지"""
    st.title(f"📊 {t('품질 분석 대시보드')}")
    
    # 데이터 로드
    data = load_sample_analytics_data()
    
    if data.empty:
        st.warning(f"⚠️ {t('분석할 데이터가 없습니다')}.")
        return
    
    # 기본 통계
    show_analytics_summary(data)
    
    st.divider()
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📈 {t('트렌드 분석')}", 
        f"🔍 {t('패턴 발견')}", 
        f"⚠️ {t('품질 알림')}", 
        f"🎯 {t('개선 제안')}"
    ])
    
    with tab1:
        show_trend_analysis(data)
    
    with tab2:
        show_pattern_analysis(data)
    
    with tab3:
        show_quality_alerts(data)
    
    with tab4:
        show_improvement_suggestions(data)

def load_sample_analytics_data():
    """샘플 분석 데이터 생성"""
    try:
        # 시드 설정으로 일관된 데이터 생성
        np.random.seed(42)
        
        # 60일간의 데이터
        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
        
        data = []
        base_defect_rate = 0.02
        
        for i, date in enumerate(dates):
            # 시간에 따른 변화 패턴
            seasonal_effect = 0.005 * np.sin(i * 0.1)  # 계절적 변화
            trend_effect = 0.0001 * i  # 점진적 개선
            noise = np.random.normal(0, 0.003)  # 랜덤 노이즈
            
            defect_rate = base_defect_rate + seasonal_effect + trend_effect + noise
            defect_rate = max(0, min(0.1, defect_rate))  # 0-10% 범위 제한
            
            # 요일 효과 (월요일이 약간 높음)
            if date.weekday() == 0:  # 월요일
                defect_rate *= 1.2
            elif date.weekday() == 4:  # 금요일
                defect_rate *= 0.9
            
            total_inspected = np.random.randint(80, 150)
            defect_quantity = int(total_inspected * defect_rate)
            
            # 가끔 이상치 추가
            if np.random.random() < 0.05:  # 5% 확률
                defect_quantity = int(total_inspected * 0.08)
            
            data.append({
                'date': date,
                'total_inspected': total_inspected,
                'defect_quantity': defect_quantity,
                'defect_rate': defect_quantity / total_inspected,
                'inspector': f"검사자{np.random.randint(1, 6)}",
                'model': f"모델{chr(65 + np.random.randint(0, 3))}",  # A, B, C
                'shift': np.random.choice(['주간', '야간']),
                'weekday': date.weekday(),
                'week': date.isocalendar()[1]
            })
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"데이터 생성 오류: {str(e)}")
        return pd.DataFrame()

def show_analytics_summary(data):
    """분석 요약 정보"""
    # 기본 통계 계산
    total_inspected = data['total_inspected'].sum()
    total_defects = data['defect_quantity'].sum()
    avg_defect_rate = data['defect_rate'].mean()
    
    # 최근 7일 vs 이전 7일 비교
    recent_7_days = data.tail(7)['defect_rate'].mean()
    previous_7_days = data.iloc[-14:-7]['defect_rate'].mean() if len(data) >= 14 else avg_defect_rate
    
    trend_change = (recent_7_days - previous_7_days) / previous_7_days * 100 if previous_7_days > 0 else 0
    
    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            f"{t('총 검사 수량')}", 
            f"{total_inspected:,}",
            help="분석 기간 동안의 총 검사 수량"
        )
    
    with col2:
        st.metric(
            f"{t('총 불량 수량')}", 
            f"{total_defects:,}",
            help="분석 기간 동안의 총 불량 수량"
        )
    
    with col3:
        st.metric(
            f"{t('평균 불량률')}", 
            f"{avg_defect_rate:.2%}",
            help="전체 기간 평균 불량률"
        )
    
    with col4:
        trend_delta = f"{trend_change:+.1f}%" if abs(trend_change) > 0.1 else "변화 없음"
        trend_color = "normal" if abs(trend_change) < 5 else ("inverse" if trend_change < 0 else "off")
        
        st.metric(
            f"{t('주간 트렌드')}", 
            "개선" if trend_change < -1 else "악화" if trend_change > 1 else "안정",
            delta=trend_delta,
            delta_color=trend_color,
            help="최근 7일 vs 이전 7일 불량률 변화"
        )

def show_trend_analysis(data):
    """트렌드 분석"""
    st.subheader(f"📈 {t('불량률 트렌드 분석')}")
    
    # 일별 트렌드 차트
    fig_daily = px.line(
        data, 
        x='date', 
        y='defect_rate',
        title=t('일별 불량률 변화'),
        labels={'date': t('날짜'), 'defect_rate': t('불량률')}
    )
    
    # 이동평균 추가
    data['ma_7'] = data['defect_rate'].rolling(window=7, center=True).mean()
    data['ma_14'] = data['defect_rate'].rolling(window=14, center=True).mean()
    
    fig_daily.add_trace(
        go.Scatter(
            x=data['date'], 
            y=data['ma_7'],
            mode='lines',
            name=t('7일 이동평균'),
            line=dict(color='red', width=2)
        )
    )
    
    fig_daily.add_trace(
        go.Scatter(
            x=data['date'], 
            y=data['ma_14'],
            mode='lines',
            name=t('14일 이동평균'),
            line=dict(color='green', width=2)
        )
    )
    
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # 트렌드 분석 결과
    st.subheader(f"🔍 {t('트렌드 분석 결과')}")
    
    # 선형 회귀로 트렌드 계산
    x = np.arange(len(data))
    y = data['defect_rate'].values
    
    # 간단한 선형 회귀 (numpy만 사용)
    trend_slope = np.polyfit(x, y, 1)[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        if trend_slope < -0.0001:
            st.success(f"✅ {t('품질이 개선되고 있습니다')} (일일 {abs(trend_slope):.4f} 감소)")
        elif trend_slope > 0.0001:
            st.warning(f"⚠️ {t('품질이 악화되고 있습니다')} (일일 {trend_slope:.4f} 증가)")
        else:
            st.info(f"📊 {t('품질이 안정적입니다')}")
    
    with col2:
        # 변동성 분석
        volatility = data['defect_rate'].std()
        if volatility > 0.01:
            st.warning(f"🔀 {t('불량률 변동이 큽니다')} (표준편차: {volatility:.3f})")
        else:
            st.success(f"🎯 {t('불량률이 안정적입니다')} (표준편차: {volatility:.3f})")

def show_pattern_analysis(data):
    """패턴 분석"""
    st.subheader(f"🔍 {t('품질 패턴 분석')}")
    
    # 요일별 패턴
    weekday_pattern = data.groupby('weekday')['defect_rate'].agg(['mean', 'count']).round(4)
    weekday_names = ['월', '화', '수', '목', '금', '토', '일']
    
    weekday_data = []
    for i in range(7):
        if i in weekday_pattern.index:
            weekday_data.append({
                'weekday': weekday_names[i],
                'avg_defect_rate': weekday_pattern.loc[i, 'mean'],
                'data_count': weekday_pattern.loc[i, 'count']
            })
    
    if weekday_data:
        weekday_df = pd.DataFrame(weekday_data)
        
        fig_weekday = px.bar(
            weekday_df,
            x='weekday',
            y='avg_defect_rate',
            title=t('요일별 평균 불량률'),
            labels={'weekday': t('요일'), 'avg_defect_rate': t('평균 불량률')}
        )
        st.plotly_chart(fig_weekday, use_container_width=True)
        
        # 요일별 인사이트
        best_day = weekday_df.loc[weekday_df['avg_defect_rate'].idxmin(), 'weekday']
        worst_day = weekday_df.loc[weekday_df['avg_defect_rate'].idxmax(), 'weekday']
        
        st.info(f"📅 {t('품질이 가장 좋은 요일')}: {best_day}요일")
        st.info(f"📅 {t('품질이 가장 나쁜 요일')}: {worst_day}요일")
    
    # 모델별 패턴
    st.subheader(f"🏭 {t('모델별 품질 패턴')}")
    
    model_pattern = data.groupby('model')['defect_rate'].agg(['mean', 'std', 'count']).round(4)
    
    fig_model = px.box(
        data,
        x='model',
        y='defect_rate',
        title=t('모델별 불량률 분포'),
        labels={'model': t('모델'), 'defect_rate': t('불량률')}
    )
    st.plotly_chart(fig_model, use_container_width=True)
    
    # 모델별 순위
    model_ranking = model_pattern.sort_values('mean')
    st.info(f"🥇 {t('품질 1위 모델')}: {model_ranking.index[0]} (평균 {model_ranking.iloc[0]['mean']:.2%})")
    st.info(f"🥉 {t('개선 필요 모델')}: {model_ranking.index[-1]} (평균 {model_ranking.iloc[-1]['mean']:.2%})")

def show_quality_alerts(data):
    """품질 알림"""
    st.subheader(f"⚠️ {t('품질 알림 시스템')}")
    
    # 이상치 탐지 (통계적 방법)
    mean_rate = data['defect_rate'].mean()
    std_rate = data['defect_rate'].std()
    threshold = mean_rate + 2 * std_rate  # 2 표준편차
    
    anomalies = data[data['defect_rate'] > threshold]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"{t('이상치 개수')}", len(anomalies))
    
    with col2:
        if len(anomalies) > 0:
            anomaly_rate = len(anomalies) / len(data) * 100
            st.metric(f"{t('이상치 비율')}", f"{anomaly_rate:.1f}%")
        else:
            st.metric(f"{t('이상치 비율')}", "0%")
    
    with col3:
        if len(data) > 0:
            last_defect_rate = data.iloc[-1]['defect_rate']
            if last_defect_rate > threshold:
                st.metric(f"{t('최근 상태')}", "🔴 주의", delta="이상치 발견")
            elif last_defect_rate > mean_rate + std_rate:
                st.metric(f"{t('최근 상태')}", "🟡 경고", delta="평균 초과")
            else:
                st.metric(f"{t('최근 상태')}", "🟢 정상", delta="정상 범위")
    
    # 이상치 목록
    if len(anomalies) > 0:
        st.subheader(f"🚨 {t('이상치 발견 목록')}")
        
        display_anomalies = anomalies[['date', 'defect_rate', 'total_inspected', 'defect_quantity', 'inspector', 'model']].copy()
        display_anomalies['date'] = display_anomalies['date'].dt.strftime('%Y-%m-%d')
        display_anomalies['defect_rate'] = display_anomalies['defect_rate'].apply(lambda x: f"{x:.2%}")
        
        st.dataframe(display_anomalies, use_container_width=True)
    else:
        st.success(f"✅ {t('이상치가 발견되지 않았습니다')}. {t('품질이 안정적입니다')}.")
    
    # 품질 임계값 설정
    st.subheader(f"⚙️ {t('품질 임계값 설정')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        warning_threshold = st.slider(
            f"{t('경고 임계값')} (%)", 
            min_value=1, max_value=10, value=3, step=1
        ) / 100
    
    with col2:
        critical_threshold = st.slider(
            f"{t('위험 임계값')} (%)", 
            min_value=3, max_value=15, value=5, step=1
        ) / 100
    
    # 임계값 기반 알림
    recent_data = data.tail(7)  # 최근 7일
    warning_days = len(recent_data[recent_data['defect_rate'] > warning_threshold])
    critical_days = len(recent_data[recent_data['defect_rate'] > critical_threshold])
    
    if critical_days > 0:
        st.error(f"🚨 {t('위험')}: {t('최근 7일 중')} {critical_days}{t('일이 위험 임계값을 초과했습니다')}!")
    elif warning_days > 2:
        st.warning(f"⚠️ {t('경고')}: {t('최근 7일 중')} {warning_days}{t('일이 경고 임계값을 초과했습니다')}.")
    else:
        st.success(f"✅ {t('품질 상태가 양호합니다')}.")

def show_improvement_suggestions(data):
    """개선 제안"""
    st.subheader(f"🎯 {t('품질 개선 제안')}")
    
    # 데이터 기반 인사이트 분석
    insights = []
    
    # 1. 트렌드 기반 제안
    x = np.arange(len(data))
    trend_slope = np.polyfit(x, data['defect_rate'].values, 1)[0]
    
    if trend_slope > 0.0001:
        insights.append({
            'priority': 'high',
            'title': '불량률 상승 트렌드 대응',
            'description': '최근 불량률이 지속적으로 상승하고 있습니다. 생산 프로세스 점검이 필요합니다.',
            'action': '생산 라인 정밀 점검, 장비 캘리브레이션, 원자재 품질 확인'
        })
    
    # 2. 변동성 기반 제안
    volatility = data['defect_rate'].std()
    if volatility > 0.01:
        insights.append({
            'priority': 'medium',
            'title': '품질 안정성 개선',
            'description': f'불량률 변동이 큽니다 (표준편차: {volatility:.3f}). 프로세스 표준화가 필요합니다.',
            'action': '작업 표준서 개선, 검사원 교육 강화, 환경 조건 관리'
        })
    
    # 3. 요일별 패턴 기반 제안
    weekday_pattern = data.groupby('weekday')['defect_rate'].mean()
    if len(weekday_pattern) > 1:
        worst_weekday = weekday_pattern.idxmax()
        best_weekday = weekday_pattern.idxmin()
        weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        
        if weekday_pattern[worst_weekday] > weekday_pattern[best_weekday] * 1.2:
            insights.append({
                'priority': 'medium',
                'title': f'{weekday_names[worst_weekday]} 품질 개선',
                'description': f'{weekday_names[worst_weekday]}의 불량률이 다른 요일보다 높습니다.',
                'action': f'{weekday_names[worst_weekday]} 특별 관리 계획 수립, 해당 요일 작업 조건 분석'
            })
    
    # 4. 모델별 패턴 기반 제안
    model_pattern = data.groupby('model')['defect_rate'].mean()
    if len(model_pattern) > 1:
        worst_model = model_pattern.idxmax()
        best_model = model_pattern.idxmin()
        
        if model_pattern[worst_model] > model_pattern[best_model] * 1.3:
            insights.append({
                'priority': 'high',
                'title': f'{worst_model} 모델 품질 개선',
                'description': f'{worst_model} 모델의 불량률이 {best_model} 모델보다 현저히 높습니다.',
                'action': f'{worst_model} 모델 생산 공정 재검토, {best_model} 모델 우수 사례 벤치마킹'
            })
    
    # 5. 최근 성과 기반 제안
    recent_avg = data.tail(7)['defect_rate'].mean()
    overall_avg = data['defect_rate'].mean()
    
    if recent_avg < overall_avg * 0.8:
        insights.append({
            'priority': 'low',
            'title': '우수 성과 유지 방안',
            'description': '최근 품질 성과가 우수합니다. 현재 상태를 유지하는 것이 중요합니다.',
            'action': '현재 프로세스 문서화, 우수 사례 공유, 지속적 모니터링'
        })
    
    # 기본 제안 (데이터가 부족한 경우)
    if not insights:
        insights.append({
            'priority': 'medium',
            'title': '지속적 품질 모니터링',
            'description': '품질 데이터의 지속적인 수집과 분석을 통해 개선 기회를 발굴하세요.',
            'action': '일일 품질 리뷰 회의, 월간 트렌드 분석, 예방적 품질 관리'
        })
    
    # 우선순위별 제안 표시
    priority_order = {'high': 1, 'medium': 2, 'low': 3}
    insights.sort(key=lambda x: priority_order[x['priority']])
    
    for i, insight in enumerate(insights, 1):
        priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        priority_text = {'high': '높음', 'medium': '보통', 'low': '낮음'}
        
        with st.expander(f"{priority_icon[insight['priority']]} {insight['title']} (우선순위: {priority_text[insight['priority']]})", expanded=i==1):
            st.write(f"**📋 {t('문제 설명')}:** {insight['description']}")
            st.write(f"**🔧 {t('권장 조치')}:** {insight['action']}")
    
    # 종합 품질 점수
    st.subheader(f"🏆 {t('종합 품질 점수')}")
    
    # 점수 계산 (100점 만점)
    base_score = 70
    
    # 트렌드 점수 (-10 ~ +15)
    if trend_slope < -0.0001:
        trend_score = 15  # 개선 중
    elif trend_slope > 0.0001:
        trend_score = -10  # 악화 중
    else:
        trend_score = 5  # 안정
    
    # 안정성 점수 (-15 ~ +10)
    if volatility < 0.005:
        stability_score = 10
    elif volatility < 0.01:
        stability_score = 5
    else:
        stability_score = -15
    
    # 최근 성과 점수 (-10 ~ +15)
    recent_avg = data.tail(7)['defect_rate'].mean()
    overall_avg = data['defect_rate'].mean()
    
    if recent_avg < overall_avg * 0.8:
        recent_score = 15
    elif recent_avg < overall_avg:
        recent_score = 5
    elif recent_avg < overall_avg * 1.2:
        recent_score = -5
    else:
        recent_score = -10
    
    total_score = max(0, min(100, base_score + trend_score + stability_score + recent_score))
    
    # 점수 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_color = "🟢" if total_score >= 80 else "🟡" if total_score >= 60 else "🔴"
        st.metric(f"{t('종합 점수')}", f"{score_color} {total_score}/100")
    
    with col2:
        trend_status = "개선" if trend_slope < -0.0001 else "악화" if trend_slope > 0.0001 else "안정"
        st.metric(f"{t('트렌드')}", trend_status)
    
    with col3:
        stability_status = "우수" if volatility < 0.005 else "양호" if volatility < 0.01 else "개선필요"
        st.metric(f"{t('안정성')}", stability_status)
    
    with col4:
        recent_status = "우수" if recent_avg < overall_avg * 0.8 else "양호" if recent_avg < overall_avg else "주의"
        st.metric(f"{t('최근 성과')}", recent_status)
    
    # 등급 및 평가
    if total_score >= 90:
        st.success("🏆 **S등급** - 최우수 품질 수준입니다!")
    elif total_score >= 80:
        st.success("🥇 **A등급** - 우수한 품질 수준입니다.")
    elif total_score >= 70:
        st.info("🥈 **B등급** - 양호한 품질 수준입니다.")
    elif total_score >= 60:
        st.warning("🥉 **C등급** - 개선이 필요합니다.")
    else:
        st.error("❌ **D등급** - 즉시 개선 조치가 필요합니다!")