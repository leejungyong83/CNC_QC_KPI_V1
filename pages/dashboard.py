import streamlit as st
import pandas as pd
import plotly.express as px

def show_dashboard():
    """KPI 대시보드 화면 표시"""
    st.header("KPI 대시보드")
    
    # KPI 카드 레이아웃
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="총 검사 건수", value="175", delta="15")
    with col2:
        st.metric(label="불량률", value="3.5%", delta="-0.5%")
    with col3:
        st.metric(label="평균 검사 시간", value="12분", delta="-2분")
    with col4:
        st.metric(label="최초 합격률", value="92%", delta="2%")
    
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
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["검사 현황", "불량 현황", "설비별 현황", "모델별 현황"])
    
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
        
    with tab2:
        st.subheader("불량률 추이")
        # 불량률 데이터 (예시)
        chart_data = pd.DataFrame({
            "날짜": pd.date_range(start="2023-01-01", periods=30),
            "불량률": [4.0, 3.9, 4.2, 3.8, 3.7, 3.6, 3.3, 3.5, 3.6, 3.4, 
                     3.2, 3.5, 3.6, 3.7, 3.8, 3.6, 3.5, 3.4, 3.3, 3.4,
                     3.5, 3.6, 3.5, 3.4, 3.3, 3.2, 3.3, 3.4, 3.5, 3.4]
        })
        fig = px.line(chart_data, x="날짜", y="불량률", title="일별 불량률")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("주요 불량 유형")
        # 불량 유형 데이터 (예시)
        defect_data = pd.DataFrame({
            "불량 유형": ["치수 불량", "표면 결함", "가공 불량", "재료 결함", "기타"],
            "발생 건수": [15, 12, 8, 5, 3]
        })
        fig = px.bar(defect_data, x="불량 유형", y="발생 건수", title="불량 유형별 발생 건수")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab3:
        st.subheader("설비별 검사 현황")
        # 설비별 데이터 (예시)
        equipment_data = pd.DataFrame({
            "설비": ["설비1", "설비2", "설비3", "설비4", "설비5"],
            "검사 건수": [45, 38, 42, 36, 30],
            "불량 건수": [2, 3, 1, 1, 2],
            "불량률": [4.4, 7.9, 2.4, 2.8, 6.7]
        })
        st.dataframe(equipment_data, use_container_width=True)
        
        fig = px.bar(equipment_data, x="설비", y="불량률", title="설비별 불량률")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("모델별 검사 현황")
        # 모델별 데이터 (예시)
        model_data = pd.DataFrame({
            "모델": ["모델A", "모델B", "모델C", "모델D", "모델E"],
            "검사 건수": [50, 42, 38, 25, 20],
            "불량 건수": [3, 2, 3, 1, 1],
            "불량률": [6.0, 4.8, 7.9, 4.0, 5.0]
        })
        st.dataframe(model_data, use_container_width=True)
        
        fig = px.bar(model_data, x="모델", y="불량률", title="모델별 불량률")
        st.plotly_chart(fig, use_container_width=True) 