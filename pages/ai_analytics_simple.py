"""
🤖 AI 분석 페이지 (간소화 버전)
2025-07-30 추가
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from utils.ml_predictor import get_predictor
from utils.anomaly_detector import get_detector
from utils.trend_analyzer import get_analyzer
from utils.language_manager import t

def show_ai_analytics():
    """AI 분석 메인 페이지"""
    st.title(f"🤖 {t('AI 품질 분석')}")
    
    # 데이터 로드
    try:
        data = load_sample_data()
        
        if data.empty:
            st.warning(f"⚠️ {t('분석할 데이터가 없습니다')}.")
            return
        
        # 기본 통계
        show_basic_stats(data)
        
        st.divider()
        
        # 탭 생성
        tab1, tab2, tab3 = st.tabs([
            f"🔮 {t('예측 분석')}", 
            f"🔍 {t('이상치 탐지')}", 
            f"📈 {t('트렌드 분석')}"
        ])
        
        with tab1:
            show_prediction_analysis(data)
        
        with tab2:
            show_anomaly_analysis(data)
        
        with tab3:
            show_trend_analysis_simple(data)
            
    except Exception as e:
        st.error(f"❌ {t('분석 오류')}: {str(e)}")

def load_sample_data():
    """샘플 데이터 로드 또는 생성"""
    try:
        # 더미 데이터 생성
        np.random.seed(42)
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        
        data = []
        for i, date in enumerate(dates):
            base_rate = 0.02 + 0.001 * np.sin(i * 0.3) + np.random.normal(0, 0.005)
            base_rate = max(0, min(0.1, base_rate))
            
            total = np.random.randint(80, 120)
            defects = int(total * base_rate)
            
            # 가끔 이상치
            if np.random.random() < 0.1:
                defects = int(total * 0.08)
            
            data.append({
                'inspection_date': date,
                'total_inspected': total,
                'defect_quantity': defects,
                'inspector_id': f'inspector_{np.random.randint(1, 4)}',
                'model_id': f'model_{np.random.randint(1, 3)}'
            })
        
        return pd.DataFrame(data)
        
    except Exception:
        return pd.DataFrame()

def show_basic_stats(data):
    """기본 통계 표시"""
    data['defect_rate'] = data['defect_quantity'] / data['total_inspected']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(f"{t('총 검사 수량')}", f"{data['total_inspected'].sum():,}")
    
    with col2:
        st.metric(f"{t('총 불량 수량')}", f"{data['defect_quantity'].sum():,}")
    
    with col3:
        avg_rate = data['defect_rate'].mean()
        st.metric(f"{t('평균 불량률')}", f"{avg_rate:.2%}")
    
    with col4:
        data_points = len(data)
        st.metric(f"{t('데이터 포인트')}", f"{data_points}")

def show_prediction_analysis(data):
    """예측 분석"""
    st.subheader(f"🔮 {t('불량률 예측')}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        pred_days = st.slider(f"{t('예측 기간')} ({t('일')})", 1, 14, 7)
    
    with col2:
        if st.button(f"▶️ {t('예측 실행')}", type="primary"):
            with st.spinner(f"{t('AI 모델 학습 중')}..."):
                predictor = get_predictor()
                
                # 모델 학습
                train_result = predictor.train_model(data)
                
                if train_result['status'] == 'success':
                    st.success(f"✅ {t('모델 학습 완료')}!")
                    
                    # 성능 표시
                    perf = train_result['performance']
                    st.info(f"📊 {t('모델 정확도')}: {perf['accuracy']:.1f}% | R² 점수: {perf['r2_score']:.3f}")
                    
                    # 예측 수행
                    pred_result = predictor.predict(pred_days)
                    
                    if pred_result['status'] == 'success':
                        # 차트 생성
                        fig = create_simple_prediction_chart(data, pred_result['predictions'])
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 예측 테이블
                        pred_df = pd.DataFrame(pred_result['predictions'])
                        pred_df['predicted_defect_rate'] = pred_df['predicted_defect_rate'].apply(lambda x: f"{x:.2%}")
                        st.dataframe(pred_df, use_container_width=True)
                    
                else:
                    st.error(f"❌ {train_result['message']}")

def show_anomaly_analysis(data):
    """이상치 분석"""
    st.subheader(f"🔍 {t('이상치 탐지')}")
    
    if st.button(f"🕵️ {t('이상치 분석 실행')}", type="primary"):
        with st.spinner(f"{t('이상치 탐지 중')}..."):
            detector = get_detector()
            result = detector.detect_anomalies(data)
            
            if result['status'] == 'success':
                stats = result['statistics']
                
                # 통계 표시
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(f"{t('이상치 개수')}", stats['total_anomalies'])
                
                with col2:
                    st.metric(f"{t('이상치 비율')}", f"{stats['anomaly_percentage']:.1f}%")
                
                with col3:
                    severity_colors = {"없음": "🟢", "낮음": "🟡", "보통": "🟠", "높음": "🔴", "심각": "🚨"}
                    color = severity_colors.get(stats['severity'], "⚪")
                    st.metric(f"{t('심각도')}", f"{color} {stats['severity']}")
                
                # 인사이트
                for insight in result['insights']:
                    st.info(insight)
                
                # 차트
                if result['anomalies']:
                    fig = create_simple_anomaly_chart(data, result['anomalies'])
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.error(f"❌ {result['message']}")

def show_trend_analysis_simple(data):
    """간단한 트렌드 분석"""
    st.subheader(f"📈 {t('트렌드 분석')}")
    
    if st.button(f"📊 {t('트렌드 분석 실행')}", type="primary"):
        with st.spinner(f"{t('트렌드 계산 중')}..."):
            analyzer = get_analyzer()
            result = analyzer.analyze_trends(data)
            
            if result['status'] == 'success':
                classification = result['trend_analysis']['classification']
                
                # 트렌드 요약
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    trend_icons = {"개선": "📈", "악화": "📉", "안정": "➡️"}
                    icon = trend_icons.get(classification['defect_rate_trend'], "➡️")
                    st.metric(f"{t('불량률 트렌드')}", f"{icon} {classification['defect_rate_trend']}")
                
                with col2:
                    st.metric(f"{t('트렌드 강도')}", classification['trend_strength'])
                
                with col3:
                    confidence_colors = {"높음": "🟢", "보통": "🟡", "낮음": "🔴"}
                    color = confidence_colors.get(classification['confidence'], "⚪")
                    st.metric(f"{t('신뢰도')}", f"{color} {classification['confidence']}")
                
                # 인사이트
                for insight in result['insights']:
                    st.info(insight)
                
                # 트렌드 차트
                fig = create_simple_trend_chart(data)
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.error(f"❌ {result['message']}")

def create_simple_prediction_chart(data, predictions):
    """간단한 예측 차트"""
    data = data.copy()
    data['defect_rate'] = data['defect_quantity'] / data['total_inspected']
    
    fig = go.Figure()
    
    # 실제 데이터
    fig.add_trace(go.Scatter(
        x=data['inspection_date'],
        y=data['defect_rate'],
        mode='lines+markers',
        name=t('실제 불량률'),
        line=dict(color='blue')
    ))
    
    # 예측 데이터
    pred_dates = [pd.to_datetime(p['date']) for p in predictions]
    pred_rates = [p['predicted_defect_rate'] for p in predictions]
    
    fig.add_trace(go.Scatter(
        x=pred_dates,
        y=pred_rates,
        mode='lines+markers',
        name=t('예측 불량률'),
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title=t('불량률 예측'),
        xaxis_title=t('날짜'),
        yaxis_title=t('불량률')
    )
    
    return fig

def create_simple_anomaly_chart(data, anomalies):
    """간단한 이상치 차트"""
    data = data.copy()
    data['defect_rate'] = data['defect_quantity'] / data['total_inspected']
    
    fig = go.Figure()
    
    # 정상 데이터
    fig.add_trace(go.Scatter(
        x=data['inspection_date'],
        y=data['defect_rate'],
        mode='markers',
        name=t('정상 데이터'),
        marker=dict(color='blue', size=6)
    ))
    
    # 이상치
    anomaly_dates = [pd.to_datetime(a['date']) for a in anomalies]
    anomaly_rates = [a['defect_rate'] for a in anomalies]
    
    fig.add_trace(go.Scatter(
        x=anomaly_dates,
        y=anomaly_rates,
        mode='markers',
        name=t('이상치'),
        marker=dict(color='red', size=12, symbol='x')
    ))
    
    fig.update_layout(
        title=t('이상치 탐지'),
        xaxis_title=t('날짜'),
        yaxis_title=t('불량률')
    )
    
    return fig

def create_simple_trend_chart(data):
    """간단한 트렌드 차트"""
    data = data.copy()
    data['defect_rate'] = data['defect_quantity'] / data['total_inspected']
    
    # 일별 집계
    daily = data.groupby('inspection_date')['defect_rate'].mean().reset_index()
    
    fig = px.line(
        daily, 
        x='inspection_date', 
        y='defect_rate',
        title=t('불량률 트렌드'),
        labels={'inspection_date': t('날짜'), 'defect_rate': t('불량률')}
    )
    
    return fig