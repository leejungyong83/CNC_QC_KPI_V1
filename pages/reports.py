import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import numpy as np
from utils.defect_utils import get_defect_type_names

def show_reports():
    """보고서 페이지를 표시합니다."""
    st.header("보고서")
    
    # 세션 상태 초기화
    if "report_type" not in st.session_state:
        st.session_state.report_type = None
    
    # 공통으로 사용할 날짜 선택 및 데이터
    with st.sidebar:
        st.subheader("리포트 설정")
        today = datetime.now().date()
        end_date = st.date_input("종료일", value=today)
        model = st.selectbox(
            "모델 선택", 
            ["모든 모델", "모델A", "모델B", "모델C", "모델D", "모델E"]
        )
        chart_type = st.selectbox(
            "차트 타입",
            ["라인 차트", "바 차트", "파이 차트", "복합 차트"]
        )
    
    # 리포트 타입 선택 버튼 표시
    if st.session_state.report_type is None:
        show_report_menu()
    else:
        # 뒤로 가기 버튼
        if st.button("← 리포트 메뉴로 돌아가기"):
            st.session_state.report_type = None
            st.rerun()
            
        # 선택된 리포트 표시
        if st.session_state.report_type == "dashboard":
            show_dashboard(end_date, model, chart_type)
        elif st.session_state.report_type == "daily":
            show_daily_report(end_date, model, chart_type)
        elif st.session_state.report_type == "weekly":
            show_weekly_report(end_date, model, chart_type)
        elif st.session_state.report_type == "monthly":
            show_monthly_report(end_date, model, chart_type)
        elif st.session_state.report_type == "yearly":
            show_yearly_report(end_date, model, chart_type)

def show_report_menu():
    """리포트 메뉴 화면을 표시합니다."""
    st.subheader("📊 리포트 메뉴")
    
    # 카드 스타일 정의
    card_style = """
    <style>
    .report-card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        background-color: #f0f2f6;
        text-align: center;
        cursor: pointer;
    }
    .report-card:hover {
        background-color: #e6e9ef;
    }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)
    
    # 리포트 카드 행 생성
    col1, col2 = st.columns(2)
    
    # 총합 대시보드
    with col1:
        if st.button("📈 총합 대시보드", use_container_width=True, key="dashboard_btn"):
            st.session_state.report_type = "dashboard"
            st.rerun()
    
    # 일간 리포트
    with col2:
        if st.button("📆 일간 리포트", use_container_width=True, key="daily_btn"):
            st.session_state.report_type = "daily"
            st.rerun()
            
    # 주간 리포트
    with col1:
        if st.button("📆 주간 리포트", use_container_width=True, key="weekly_btn"):
            st.session_state.report_type = "weekly"
            st.rerun()
            
    # 월간 리포트
    with col2:
        if st.button("📊 월간 리포트", use_container_width=True, key="monthly_btn"):
            st.session_state.report_type = "monthly"
            st.rerun()
            
    # 연간 리포트
    with col1:
        if st.button("📊 연간 리포트", use_container_width=True, key="yearly_btn"):
            st.session_state.report_type = "yearly"
            st.rerun()

def show_dashboard(end_date, model, chart_type):
    """총합 대시보드를 표시합니다."""
    st.subheader("총합 대시보드")
    
    # 오늘 날짜 표시
    st.write(f"기준일: {end_date.strftime('%Y-%m-%d')}")
    
    if model != "모든 모델":
        st.write(f"선택된 모델: {model}")
    
    # 데이터 생성
    # 일간 데이터
    daily_data = generate_hourly_data(end_date, model)
    # 주간 데이터
    start_date = end_date - timedelta(days=6)
    weekly_data = generate_daily_data(start_date, end_date, model)
    # 월간 데이터
    monthly_data = generate_monthly_data(end_date.year, model)
    
    # 주요 KPI 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        daily_production = sum(daily_data["production_count"])
        st.metric(label="오늘 생산량", value=f"{daily_production:,}")
    
    with col2:
        daily_defect_rate = sum(daily_data["defect_count"]) / daily_production * 100 if daily_production > 0 else 0
        st.metric(label="오늘 불량률", value=f"{daily_defect_rate:.2f}%")
    
    with col3:
        weekly_production = sum(weekly_data["production_count"])
        st.metric(label="주간 생산량", value=f"{weekly_production:,}")
    
    with col4:
        weekly_defect_rate = sum(weekly_data["defect_count"]) / weekly_production * 100 if weekly_production > 0 else 0
        st.metric(label="주간 불량률", value=f"{weekly_defect_rate:.2f}%")
    
    # 차트 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("시간별 생산량 추이")
        fig = px.line(
            daily_data,
            x="hour",
            y="production_count",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("일별 불량률 추이")
        fig = px.line(
            weekly_data,
            x="date",
            y="defect_rate",
            markers=True,
            color_discrete_sequence=["#FF4B4B"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 월별 추이
    st.subheader("월별 생산량 및 불량률 추이")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_data["month"],
        y=monthly_data["production_count"],
        name="생산량"
    ))
    fig.add_trace(go.Scatter(
        x=monthly_data["month"],
        y=monthly_data["defect_rate"],
        name="불량률 (%)",
        yaxis="y2",
        line=dict(color="red")
    ))
    fig.update_layout(
        yaxis2=dict(
            title="불량률 (%)",
            overlaying="y",
            side="right"
        ),
        yaxis=dict(title="생산량"),
        xaxis=dict(title="월"),
        legend=dict(x=0.01, y=0.99),
        title="월별 생산량 및 불량률 추이"
    )
    st.plotly_chart(fig, use_container_width=True)

def show_daily_report(end_date, model, chart_type):
    """일간 리포트를 표시합니다."""
    st.subheader("일간 생산 품질 리포트")
    st.write(f"기준일: {end_date.strftime('%Y-%m-%d')}")
    
    if model != "모든 모델":
        st.write(f"선택된 모델: {model}")
    
    # 시간별 데이터 생성
    hourly_data = generate_hourly_data(end_date, model)
    
    # 데이터 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("시간대별 생산량 및 불량률")
        
        if chart_type in ["바 차트", "복합 차트"]:
            fig = px.bar(
                hourly_data, 
                x="hour", 
                y=["production_count", "defect_count"],
                barmode="group",
                title="시간별 생산량 및 불량수"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.line(
                hourly_data, 
                x="hour", 
                y="defect_rate",
                title="시간별 불량률 (%)",
                color_discrete_sequence=["#FF4B4B"]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("검사 항목별 불량 현황")
        
        # 데이터베이스에서 불량 유형 가져오기
        defect_types = get_defect_type_names()
        
        # 검사 항목별 불량 데이터 생성
        defect_by_item = {}
        for defect_type in defect_types:
            defect_by_item[defect_type] = random.randint(1, 15)
        
        defect_df = pd.DataFrame({
            "항목": list(defect_by_item.keys()),
            "불량수": list(defect_by_item.values())
        })
        
        if chart_type in ["파이 차트", "복합 차트"]:
            fig = px.pie(
                defect_df, 
                names="항목", 
                values="불량수", 
                title="불량 유형 분포"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.bar(
                defect_df,
                x="항목",
                y="불량수",
                title="불량 유형별 건수",
                color="항목"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 일간 요약 테이블
    st.subheader("일간 생산 품질 요약")
    summary = {
        "총 생산량": sum(hourly_data["production_count"]),
        "합격": sum(hourly_data["production_count"]) - sum(hourly_data["defect_count"]),
        "불량": sum(hourly_data["defect_count"]),
        "평균 불량률": f"{(sum(hourly_data['defect_count']) / sum(hourly_data['production_count']) * 100):.2f}%",
        "주요 불량 유형": max(defect_by_item, key=defect_by_item.get)
    }
    
    st.table(pd.DataFrame([summary]))
    
    # 시간별 상세 데이터
    st.subheader("시간별 상세 데이터")
    st.dataframe(hourly_data)

def show_weekly_report(end_date, model, chart_type):
    """주간 리포트를 표시합니다."""
    st.subheader("주간 생산 품질 리포트")
    
    # 주간 범위 계산
    start_date = end_date - timedelta(days=6)
    st.write(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    
    if model != "모든 모델":
        st.write(f"선택된 모델: {model}")
    
    # 일별 데이터 생성
    daily_data = generate_daily_data(start_date, end_date, model)
    
    # 데이터 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("일별 생산량 추이")
        if chart_type in ["라인 차트", "복합 차트"]:
            fig = px.line(
                daily_data, 
                x="date", 
                y="production_count",
                markers=True,
                title="일별 생산량"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.bar(
                daily_data, 
                x="date", 
                y="production_count",
                title="일별 생산량"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("일별 불량률 추이")
        fig = px.line(
            daily_data, 
            x="date", 
            y="defect_rate",
            markers=True,
            title="일별 불량률 (%)",
            color_discrete_sequence=["#FF4B4B"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 주간 요약
    st.subheader("주간 품질 요약")
    
    summary = {
        "총 생산량": sum(daily_data["production_count"]),
        "합격": sum(daily_data["production_count"]) - sum(daily_data["defect_count"]),
        "불량": sum(daily_data["defect_count"]),
        "평균 불량률": f"{(sum(daily_data['defect_count']) / sum(daily_data['production_count']) * 100):.2f}%",
        "최고 생산일": daily_data.loc[daily_data["production_count"].idxmax(), "date"],
        "최저 불량률": f"{daily_data['defect_rate'].min():.2f}%"
    }
    
    st.table(pd.DataFrame([summary]))
    
    # 일별 상세 데이터
    st.subheader("일별 상세 데이터")
    st.dataframe(daily_data)

def show_monthly_report(end_date, model, chart_type):
    """월간 리포트를 표시합니다."""
    st.subheader("월간 생산 품질 리포트")
    
    # 월간 표시 날짜 계산
    year = end_date.year
    month = end_date.month
    month_name = f"{year}-{month:02d}"
    st.write(f"기준월: {month_name}")
    
    if model != "모든 모델":
        st.write(f"선택된 모델: {model}")

    # 주차별 데이터 생성
    weekly_data = generate_weekly_data(year, month, model)
    
    # 모델별 데이터 생성
    models = ["모델A", "모델B", "모델C", "모델D", "모델E"]
    model_data = generate_model_data(models, month)
    
    # 데이터 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("주차별 생산량 및 불량률")
        
        if chart_type in ["바 차트", "복합 차트"]:
            fig = px.bar(
                weekly_data, 
                x="week", 
                y=["production_count", "defect_count"],
                barmode="group",
                title="주차별 생산량 및 불량수"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=weekly_data["week"], 
                y=weekly_data["production_count"],
                mode="lines+markers",
                name="생산량"
            ))
            fig.add_trace(go.Scatter(
                x=weekly_data["week"], 
                y=weekly_data["defect_count"],
                mode="lines+markers",
                name="불량수",
                line=dict(color="red")
            ))
            fig.update_layout(title="주차별 생산량 및 불량수")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("모델별 생산량 비교")
        
        if chart_type in ["파이 차트"]:
            fig = px.pie(
                model_data, 
                names="model", 
                values="production_count", 
                title=f"{month_name} 모델별 생산 비율"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.bar(
                model_data, 
                x="model", 
                y=["production_count", "defect_count"],
                barmode="group",
                title=f"{month_name} 모델별 생산량 및 불량수"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 월간 요약
    st.subheader("월간 품질 요약")
    
    monthly_summary = {
        "총 생산량": sum(weekly_data["production_count"]),
        "합격": sum(weekly_data["production_count"]) - sum(weekly_data["defect_count"]),
        "불량": sum(weekly_data["defect_count"]),
        "평균 불량률": f"{(sum(weekly_data['defect_count']) / sum(weekly_data['production_count']) * 100):.2f}%",
        "주요 생산모델": model_data.loc[model_data["production_count"].idxmax(), "model"]
    }
    
    st.table(pd.DataFrame([monthly_summary]))
    
    # 월간 추이 차트
    st.subheader("일별 품질 추이")
    daily_data = generate_daily_data_for_month(year, month, model)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_data["date"], 
        y=daily_data["defect_rate"],
        mode="lines+markers",
        name="불량률 (%)",
        line=dict(color="red")
    ))
    fig.update_layout(title="일별 불량률 추이 (%)")
    st.plotly_chart(fig, use_container_width=True)

def show_yearly_report(end_date, model, chart_type):
    """연간 리포트를 표시합니다."""
    st.subheader("연간 생산 품질 리포트")
    
    # 연간 표시 날짜 계산
    year = end_date.year
    st.write(f"기준연도: {year}")
    
    if model != "모든 모델":
        st.write(f"선택된 모델: {model}")

    # 월별 데이터 생성
    monthly_data = generate_monthly_data(year, model)
    
    # 데이터 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("월별 생산량 추이")
        
        if chart_type in ["바 차트", "복합 차트"]:
            fig = px.bar(
                monthly_data, 
                x="month", 
                y="production_count",
                title=f"{year} 월별 생산량"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.line(
                monthly_data, 
                x="month", 
                y="production_count",
                markers=True,
                title=f"{year} 월별 생산량"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("월별 불량률 추이")
        
        fig = px.line(
            monthly_data, 
            x="month", 
            y="defect_rate",
            markers=True,
            title=f"{year} 월별 불량률 (%)",
            color_discrete_sequence=["#FF4B4B"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 분기별 데이터
    st.subheader("분기별 품질 분석")
    
    # 분기별 데이터 계산
    quarterly_data = monthly_data.copy()
    quarterly_data["quarter"] = (quarterly_data["month_num"] - 1) // 3 + 1
    quarterly_summary = quarterly_data.groupby("quarter").agg({
        "production_count": "sum",
        "defect_count": "sum"
    }).reset_index()
    
    quarterly_summary["defect_rate"] = (quarterly_summary["defect_count"] / quarterly_summary["production_count"] * 100).round(2)
    quarterly_summary["quarter"] = quarterly_summary["quarter"].apply(lambda x: f"Q{x}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            quarterly_summary,
            x="quarter",
            y="production_count",
            title="분기별 생산량",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            quarterly_summary,
            x="quarter",
            y="defect_rate",
            title="분기별 불량률 (%)",
            color_discrete_sequence=["#FF4B4B"],
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 연간 요약
    st.subheader("연간 품질 요약")
    
    yearly_summary = {
        "총 생산량": sum(monthly_data["production_count"]),
        "합격": sum(monthly_data["production_count"]) - sum(monthly_data["defect_count"]),
        "불량": sum(monthly_data["defect_count"]),
        "평균 불량률": f"{(sum(monthly_data['defect_count']) / sum(monthly_data['production_count']) * 100):.2f}%",
        "최고 생산월": monthly_data.loc[monthly_data["production_count"].idxmax(), "month"],
        "최저 불량률월": monthly_data.loc[monthly_data["defect_rate"].idxmin(), "month"]
    }
    
    st.table(pd.DataFrame([yearly_summary]))
    
    # 월별 상세 데이터
    st.subheader("월별 상세 데이터")
    st.dataframe(monthly_data[["month", "production_count", "defect_count", "defect_rate"]])

# 데이터 생성 함수들
def generate_hourly_data(date, model=None):
    """시간별 데이터 생성 (일간 리포트용)"""
    np.random.seed(hash(str(date) + str(model)) % 2**32)
    
    hours = list(range(8, 18))  # 8시부터 17시까지 (근무 시간)
    data = []
    
    for hour in hours:
        # 생산량은 시간대별로 다르게 (점심시간 전후로 다름)
        base_production = 80 if 11 <= hour <= 14 else 100
        production_count = int(np.random.normal(base_production, 15))
        
        # 불량수 계산 (약 3~7% 정도의 불량률)
        defect_rate = np.random.uniform(3, 7)
        defect_count = int(production_count * defect_rate / 100)
        
        data.append({
            "hour": f"{hour:02d}:00",
            "production_count": production_count,
            "defect_count": defect_count,
            "defect_rate": round(defect_rate, 2)
        })
    
    return pd.DataFrame(data)

def generate_daily_data(start_date, end_date, model=None):
    """일별 데이터 생성 (주간 리포트용)"""
    np.random.seed(hash(str(start_date) + str(end_date) + str(model)) % 2**32)
    
    days = (end_date - start_date).days + 1
    data = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # 주말(토,일)은 생산량이 적음
        is_weekend = current_date.weekday() >= 5
        base_production = 400 if is_weekend else 800
        
        production_count = int(np.random.normal(base_production, base_production * 0.1))
        
        # 불량률 계산 (약 3~5%)
        defect_rate = np.random.uniform(3, 5)
        defect_count = int(production_count * defect_rate / 100)
        
        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "day": current_date.strftime("%a"),
            "production_count": production_count,
            "defect_count": defect_count,
            "defect_rate": round(defect_rate, 2)
        })
    
    return pd.DataFrame(data)

def generate_daily_data_for_month(year, month, model=None):
    """월간 일별 데이터 생성"""
    import calendar
    
    # 해당 월의 일수 계산
    _, days_in_month = calendar.monthrange(year, month)
    
    # 시작일과 종료일 설정
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, days_in_month).date()
    
    return generate_daily_data(start_date, end_date, model)

def generate_weekly_data(year, month, model=None):
    """주차별 데이터 생성 (월간 리포트용)"""
    np.random.seed(hash(str(year) + str(month) + str(model)) % 2**32)
    
    # 일반적으로 한 달은 4-5주
    num_weeks = 5
    data = []
    
    for week in range(1, num_weeks + 1):
        # 주차별 생산량 (첫주와 마지막주는 약간 적게)
        if week in [1, num_weeks]:
            base_production = 3000
        else:
            base_production = 4000
        
        production_count = int(np.random.normal(base_production, base_production * 0.1))
        
        # 불량률 계산
        defect_rate = np.random.uniform(2.5, 5.5)
        defect_count = int(production_count * defect_rate / 100)
        
        data.append({
            "week": f"Week {week}", # 한글 대신 영문 표기 사용
            "production_count": production_count,
            "defect_count": defect_count,
            "defect_rate": round(defect_rate, 2)
        })
    
    return pd.DataFrame(data)

def generate_model_data(models, month):
    """모델별 데이터 생성 (월간 리포트용)"""
    np.random.seed(hash(str(month) + str(models)) % 2**32)
    
    data = []
    
    for model in models:
        # 모델별로 다른 생산량 설정
        base_production = np.random.randint(8000, 15000)
        production_count = base_production
        
        # 모델별로 다른 불량률
        defect_rate = np.random.uniform(2, 6)
        defect_count = int(production_count * defect_rate / 100)
        
        data.append({
            "model": model,
            "production_count": production_count,
            "defect_count": defect_count,
            "defect_rate": round(defect_rate, 2)
        })
    
    return pd.DataFrame(data)

def generate_monthly_data(year, model=None):
    """월별 데이터 생성 (연간 리포트용)"""
    np.random.seed(hash(str(year) + str(model)) % 2**32)
    
    data = []
    month_names = ["1월", "2월", "3월", "4월", "5월", "6월", 
                  "7월", "8월", "9월", "10월", "11월", "12월"]
    
    for i, month_name in enumerate(month_names, 1):
        # 계절적 요인 적용 (여름, 겨울은 약간 생산량 감소)
        if i in [1, 2, 7, 8]:
            base_production = 12000
        else:
            base_production = 15000
        
        # 월별 변동성 추가
        variation = np.random.uniform(0.8, 1.2)
        production_count = int(base_production * variation)
        
        # 불량률 계산
        defect_rate = np.random.uniform(2, 6)
        defect_count = int(production_count * defect_rate / 100)
        
        data.append({
            "month": month_name,
            "month_num": i,
            "production_count": production_count,
            "defect_count": defect_count,
            "defect_rate": round(defect_rate, 2)
        })
    
    return pd.DataFrame(data) 