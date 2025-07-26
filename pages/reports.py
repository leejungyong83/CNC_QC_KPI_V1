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

def show_reports():
    """보고서 페이지를 표시합니다."""
    st.header("📊 보고서")
    
    # 세션 상태 초기화
    if "report_type" not in st.session_state:
        st.session_state.report_type = None
    
    # 공통으로 사용할 날짜 선택 및 데이터
    with st.sidebar:
        st.subheader("📋 리포트 설정")
        today = get_vietnam_now().date()  # 베트남 시간 기준 오늘 날짜
        
        # 날짜 범위 선택
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", value=today - timedelta(days=30))
        with col2:
        end_date = st.date_input("종료일", value=today)
        
        # 모델 선택
        try:
            supabase = get_supabase_client()
            models_result = supabase.table('production_models').select('model_name').execute()
            available_models = ["전체 모델"] + [model['model_name'] for model in models_result.data] if models_result.data else ["전체 모델"]
        except:
            available_models = ["전체 모델"]
        
        selected_model = st.selectbox("모델 선택", available_models)
        
        # 검사자 선택
        try:
            inspectors_result = supabase.table('inspectors').select('name').execute()
            available_inspectors = ["전체 검사자"] + [insp['name'] for insp in inspectors_result.data] if inspectors_result.data else ["전체 검사자"]
        except:
            available_inspectors = ["전체 검사자"]
        
        selected_inspector = st.selectbox("검사자 선택", available_inspectors)
        
        # 공정 선택
        processes = ["전체 공정", "IQC", "CNC1_PQC", "CNC2_PQC", "OQC", "CNC OQC"]
        selected_process = st.selectbox("공정 선택", processes)
    
    # 리포트 타입 선택 버튼 표시
    if st.session_state.report_type is None:
        show_report_menu()
    else:
        # 뒤로 가기 버튼
        if st.button("← 리포트 메뉴로 돌아가기"):
            st.session_state.report_type = None
            st.rerun()
            
        # 선택된 리포트 표시
        filter_params = {
            'start_date': start_date,
            'end_date': end_date,
            'model': selected_model,
            'inspector': selected_inspector,
            'process': selected_process
        }
        
        if st.session_state.report_type == "dashboard":
            show_dashboard(filter_params)
        elif st.session_state.report_type == "daily":
            show_daily_report(filter_params)
        elif st.session_state.report_type == "weekly":
            show_weekly_report(filter_params)
        elif st.session_state.report_type == "monthly":
            show_monthly_report(filter_params)
        elif st.session_state.report_type == "defect_analysis":
            show_defect_analysis(filter_params)

def show_report_menu():
    """리포트 메뉴 화면을 표시합니다."""
    st.subheader("📊 리포트 메뉴")
    
    # 리포트 설명
    st.markdown("""
    **실제 검사실적 데이터를 기반으로 한 종합 분석 리포트**
    - 모든 데이터는 Supabase에서 실시간으로 조회됩니다
    - 사이드바에서 필터 조건을 설정할 수 있습니다
    """)
    
    # 리포트 카드 행 생성
    col1, col2, col3 = st.columns(3)
    
    # 총합 대시보드
    with col1:
        if st.button("📈 종합 대시보드", use_container_width=True, key="dashboard_btn", help="전체 검사실적 요약"):
            st.session_state.report_type = "dashboard"
            st.rerun()
    
    # 일별 분석
    with col2:
        if st.button("📅 일별 분석", use_container_width=True, key="daily_btn", help="일별 검사실적 추이"):
            st.session_state.report_type = "daily"
            st.rerun()
            
    # 주별 분석
    with col3:
        if st.button("📆 주별 분석", use_container_width=True, key="weekly_btn", help="주별 검사실적 추이"):
            st.session_state.report_type = "weekly"
            st.rerun()
            
    col1, col2, col3 = st.columns(3)
    
    # 월별 분석
    with col1:
        if st.button("📊 월별 분석", use_container_width=True, key="monthly_btn", help="월별 검사실적 추이"):
            st.session_state.report_type = "monthly"
            st.rerun()
            
    # 불량 분석
    with col2:
        if st.button("🔍 불량 분석", use_container_width=True, key="defect_btn", help="불량유형별 상세 분석"):
            st.session_state.report_type = "defect_analysis"
            st.rerun()

def get_inspection_data(filter_params):
    """필터 조건에 따라 검사실적 데이터를 조회합니다."""
    try:
        supabase = get_supabase_client()
        
        # 기본 쿼리
        query = supabase.table('inspection_data').select('*')
        
        # 날짜 필터
        if filter_params['start_date']:
            query = query.gte('inspection_date', filter_params['start_date'].isoformat())
        if filter_params['end_date']:
            query = query.lte('inspection_date', filter_params['end_date'].isoformat())
        
        # 데이터 조회
        result = query.order('inspection_date', desc=False).execute()
        
        if not result.data:
            return pd.DataFrame()
        
        # 검사자 및 모델 정보 조회
        inspectors_result = supabase.table('inspectors').select('*').execute()
        inspectors = {insp['id']: insp for insp in inspectors_result.data} if inspectors_result.data else {}
        
        models_result = supabase.table('production_models').select('*').execute()
        models = {model['id']: model for model in models_result.data} if models_result.data else {}
        
        # 시간대 변환
        converted_data = convert_supabase_data_timezone(result.data)
        
        # 데이터프레임 생성
        df_data = []
        for row in converted_data:
            inspector = inspectors.get(row.get('inspector_id'), {})
            model = models.get(row.get('model_id'), {})
            
            inspector_name = inspector.get('name', '알 수 없음')
            model_name = model.get('model_name', '알 수 없음')
            
            df_data.append({
                'inspection_date': row['inspection_date'],
                'inspector_name': inspector_name,
                'model_name': model_name,
                'process': row.get('process', ''),
                'total_inspected': row.get('total_inspected', 0),
                'defect_quantity': row.get('defect_quantity', 0),
                'result': row['result'],
                'notes': row.get('notes', ''),
                'created_at': row.get('created_at', '')
            })
        
        df = pd.DataFrame(df_data)
        
        # 추가 필터 적용
        if filter_params['model'] != "전체 모델":
            df = df[df['model_name'] == filter_params['model']]
        
        if filter_params['inspector'] != "전체 검사자":
            df = df[df['inspector_name'] == filter_params['inspector']]
        
        if filter_params['process'] != "전체 공정":
            df = df[df['process'] == filter_params['process']]
        
        # 날짜 컬럼을 datetime으로 변환
        df['inspection_date'] = pd.to_datetime(df['inspection_date'])
        
        # 불량률 계산
        df['defect_rate'] = (df['defect_quantity'] / df['total_inspected'] * 100).fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"데이터 조회 중 오류가 발생했습니다: {str(e)}")
        return pd.DataFrame()

def show_dashboard(filter_params):
    """종합 대시보드를 표시합니다."""
    st.subheader("📈 종합 대시보드")
    
    # 데이터 조회
    df = get_inspection_data(filter_params)
    
    if df.empty:
        st.warning("⚠️ 선택한 조건에 해당하는 데이터가 없습니다.")
        return
    
    # 필터 정보 표시
    st.info(f"📅 분석 기간: {filter_params['start_date']} ~ {filter_params['end_date']} | 총 {len(df)}건의 검사실적")
    
    # 주요 KPI 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_inspected = df['total_inspected'].sum()
        st.metric("총 검사수량", f"{total_inspected:,}개")
    
    with col2:
        total_defects = df['defect_quantity'].sum()
        st.metric("총 불량수량", f"{total_defects:,}개")
    
    with col3:
        overall_defect_rate = (total_defects / total_inspected * 100) if total_inspected > 0 else 0
        st.metric("전체 불량률", f"{overall_defect_rate:.2f}%")
    
    with col4:
        pass_count = len(df[df['result'] == '합격'])
        pass_rate = (pass_count / len(df) * 100) if len(df) > 0 else 0
        st.metric("합격률", f"{pass_rate:.1f}%")
    
    # 차트 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 일별 검사수량 추이")
        daily_summary = df.groupby(df['inspection_date'].dt.date).agg({
            'total_inspected': 'sum',
            'defect_quantity': 'sum'
        }).reset_index()
        
        if not daily_summary.empty:
            fig = px.bar(
                daily_summary,
                x='inspection_date',
                y='total_inspected',
                title="일별 검사수량",
                labels={'total_inspected': '검사수량', 'inspection_date': '날짜'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("표시할 데이터가 없습니다.")
    
    with col2:
        st.subheader("📈 일별 불량률 추이")
        if not daily_summary.empty:
            daily_summary['defect_rate'] = (daily_summary['defect_quantity'] / daily_summary['total_inspected'] * 100).fillna(0)
            
            fig = px.line(
                daily_summary,
                x='inspection_date',
                y='defect_rate',
                title="일별 불량률",
                labels={'defect_rate': '불량률 (%)', 'inspection_date': '날짜'},
                markers=True
            )
            fig.update_traces(line_color='red')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("표시할 데이터가 없습니다.")
    
    # 모델별 분석
    if len(df['model_name'].unique()) > 1:
        st.subheader("🔧 모델별 검사실적")
        model_summary = df.groupby('model_name').agg({
            'total_inspected': 'sum',
            'defect_quantity': 'sum'
        }).reset_index()
        model_summary['defect_rate'] = (model_summary['defect_quantity'] / model_summary['total_inspected'] * 100).fillna(0)
        
    col1, col2 = st.columns(2)
    
    with col1:
            fig = px.bar(
                model_summary,
                x='model_name',
                y='total_inspected',
                title="모델별 검사수량",
                labels={'total_inspected': '검사수량', 'model_name': '모델'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
            fig = px.bar(
                model_summary,
                x='model_name',
                y='defect_rate',
                title="모델별 불량률",
                labels={'defect_rate': '불량률 (%)', 'model_name': '모델'},
                color='defect_rate',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 검사자별 분석
    if len(df['inspector_name'].unique()) > 1:
        st.subheader("👤 검사자별 검사실적")
        inspector_summary = df.groupby('inspector_name').agg({
            'total_inspected': 'sum',
            'defect_quantity': 'sum'
        }).reset_index()
        inspector_summary['defect_rate'] = (inspector_summary['defect_quantity'] / inspector_summary['total_inspected'] * 100).fillna(0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                inspector_summary,
                values='total_inspected',
                names='inspector_name',
                title="검사자별 검사수량 비율"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                inspector_summary,
                x='inspector_name',
                y='defect_rate',
                title="검사자별 불량률",
                labels={'defect_rate': '불량률 (%)', 'inspector_name': '검사자'},
                color='defect_rate',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
def show_daily_report(filter_params):
    """일별 분석 리포트를 표시합니다."""
    st.subheader("📅 일별 검사실적 분석")
    
    df = get_inspection_data(filter_params)
    
    if df.empty:
        st.warning("⚠️ 선택한 조건에 해당하는 데이터가 없습니다.")
        return
    
    # 일별 집계
    daily_summary = df.groupby(df['inspection_date'].dt.date).agg({
        'total_inspected': 'sum',
        'defect_quantity': 'sum',
        'result': 'count'  # 검사 횟수
    }).reset_index()
    daily_summary.columns = ['date', 'total_inspected', 'defect_quantity', 'inspection_count']
    daily_summary['defect_rate'] = (daily_summary['defect_quantity'] / daily_summary['total_inspected'] * 100).fillna(0)
    
    # 상세 테이블
    st.subheader("📋 일별 상세 데이터")
    st.dataframe(daily_summary, use_container_width=True)
    
    # 차트
    col1, col2 = st.columns(2)
    
    with col1:
            fig = px.line(
            daily_summary,
            x='date',
            y='total_inspected',
            title="일별 검사수량 추이",
            markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            daily_summary,
            x='date',
            y='defect_rate',
            title="일별 불량률 추이",
            markers=True,
            color_discrete_sequence=['red']
        )
        st.plotly_chart(fig, use_container_width=True)
    
def show_weekly_report(filter_params):
    """주별 분석 리포트를 표시합니다."""
    st.subheader("📆 주별 검사실적 분석")
    
    df = get_inspection_data(filter_params)
    
    if df.empty:
        st.warning("⚠️ 선택한 조건에 해당하는 데이터가 없습니다.")
        return
    
    # 주별 집계 (월요일 시작)
    df['week'] = df['inspection_date'].dt.to_period('W-MON')
    weekly_summary = df.groupby('week').agg({
        'total_inspected': 'sum',
        'defect_quantity': 'sum',
        'result': 'count'
    }).reset_index()
    weekly_summary.columns = ['week', 'total_inspected', 'defect_quantity', 'inspection_count']
    weekly_summary['defect_rate'] = (weekly_summary['defect_quantity'] / weekly_summary['total_inspected'] * 100).fillna(0)
    weekly_summary['week_str'] = weekly_summary['week'].astype(str)
    
    # 상세 테이블
    st.subheader("📋 주별 상세 데이터")
    st.dataframe(weekly_summary[['week_str', 'total_inspected', 'defect_quantity', 'defect_rate', 'inspection_count']], use_container_width=True)
    
    # 차트
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            weekly_summary,
            x='week_str',
            y='total_inspected',
            title="주별 검사수량"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            weekly_summary,
            x='week_str',
            y='defect_rate',
            title="주별 불량률 추이",
            markers=True,
            color_discrete_sequence=['red']
        )
        st.plotly_chart(fig, use_container_width=True)
    
def show_monthly_report(filter_params):
    """월별 분석 리포트를 표시합니다."""
    st.subheader("📊 월별 검사실적 분석")
    
    df = get_inspection_data(filter_params)
    
    if df.empty:
        st.warning("⚠️ 선택한 조건에 해당하는 데이터가 없습니다.")
        return
    
    # 월별 집계
    df['month'] = df['inspection_date'].dt.to_period('M')
    monthly_summary = df.groupby('month').agg({
        'total_inspected': 'sum',
        'defect_quantity': 'sum',
        'result': 'count'
    }).reset_index()
    monthly_summary.columns = ['month', 'total_inspected', 'defect_quantity', 'inspection_count']
    monthly_summary['defect_rate'] = (monthly_summary['defect_quantity'] / monthly_summary['total_inspected'] * 100).fillna(0)
    monthly_summary['month_str'] = monthly_summary['month'].astype(str)
    
    # 상세 테이블
    st.subheader("📋 월별 상세 데이터")
    st.dataframe(monthly_summary[['month_str', 'total_inspected', 'defect_quantity', 'defect_rate', 'inspection_count']], use_container_width=True)
    
    # 복합 차트
    st.subheader("📈 월별 생산량 및 불량률 추이")
    fig = go.Figure()
    
    # 생산량 바 차트
    fig.add_trace(go.Bar(
        x=monthly_summary['month_str'],
        y=monthly_summary['total_inspected'],
        name='검사수량',
        yaxis='y'
    ))
    
    # 불량률 라인 차트
    fig.add_trace(go.Scatter(
        x=monthly_summary['month_str'],
        y=monthly_summary['defect_rate'],
        name='불량률 (%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        yaxis=dict(title='검사수량'),
        yaxis2=dict(title='불량률 (%)', overlaying='y', side='right'),
        xaxis=dict(title='월'),
        legend=dict(x=0.01, y=0.99)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_defect_analysis(filter_params):
    """불량 분석 리포트를 표시합니다."""
    st.subheader("🔍 불량 분석")
    
    try:
        supabase = get_supabase_client()
        
        # 불량 데이터 조회
        defects_query = supabase.table('defects').select('*')
        defects_result = defects_query.execute()
        
        if not defects_result.data:
            st.warning("⚠️ 불량 데이터가 없습니다.")
            return
        
        # 검사실적 데이터와 조인
        inspection_df = get_inspection_data(filter_params)
        
        if inspection_df.empty:
            st.warning("⚠️ 선택한 조건에 해당하는 검사실적이 없습니다.")
            return
        
        # 불량 데이터 처리 (시간대 변환 적용)
        from utils.data_converter import convert_supabase_data_timezone
        defects_data_converted = convert_supabase_data_timezone(defects_result.data)
        defects_df = pd.DataFrame(defects_data_converted)
        
        # 불량유형별 집계
        defect_summary = defects_df.groupby('defect_type').agg({
            'defect_count': 'sum',
            'inspection_id': 'count'
        }).reset_index()
        defect_summary.columns = ['defect_type', 'total_defects', 'occurrence_count']
        defect_summary = defect_summary.sort_values('total_defects', ascending=False)
        
        # 상세 테이블
        st.subheader("📋 불량유형별 상세 데이터")
        st.dataframe(defect_summary, use_container_width=True)
        
        # 차트
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                defect_summary,
                values='total_defects',
                names='defect_type',
                title="불량유형별 비율"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                defect_summary,
                x='defect_type',
                y='total_defects',
                title="불량유형별 수량",
                color='total_defects',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 파레토 차트
        st.subheader("📊 불량유형 파레토 분석")
        defect_summary_sorted = defect_summary.sort_values('total_defects', ascending=False)
        defect_summary_sorted['cumulative_percent'] = (defect_summary_sorted['total_defects'].cumsum() / defect_summary_sorted['total_defects'].sum() * 100)
        
        fig = go.Figure()
        
        # 바 차트
        fig.add_trace(go.Bar(
            x=defect_summary_sorted['defect_type'],
            y=defect_summary_sorted['total_defects'],
            name='불량수량',
            yaxis='y'
        ))
        
        # 누적 퍼센트 라인
        fig.add_trace(go.Scatter(
            x=defect_summary_sorted['defect_type'],
            y=defect_summary_sorted['cumulative_percent'],
            name='누적 비율 (%)',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            yaxis=dict(title='불량수량'),
            yaxis2=dict(title='누적 비율 (%)', overlaying='y', side='right', range=[0, 100]),
            xaxis=dict(title='불량유형'),
            legend=dict(x=0.01, y=0.99),
            title="불량유형 파레토 차트"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"불량 분석 중 오류가 발생했습니다: {str(e)}") 
