import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pages.item_management import get_all_models
from pages.inspector_management import get_all_inspectors
from utils.defect_utils import get_defect_type_names

def show_defect_management():
    """불량 관리 화면 표시"""
    st.header("불량 관리")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["불량 목록", "불량 분석", "조치 관리"])
    
    # 불량 목록 탭
    with tab1:
        show_defect_list()
    
    # 불량 분석 탭
    with tab2:
        show_defect_analysis()
    
    # 조치 관리 탭
    with tab3:
        show_action_management()

def show_defect_list():
    """불량 목록 표시"""
    st.subheader("불량 목록")
    
    # 필터 옵션
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # 생산모델관리에서 등록된 모델 리스트 불러오기
        models_df = get_all_models()
        if not models_df.empty:
            # 중복 제거된 모델명 리스트 만들기
            unique_models = models_df['name'].unique()
            model_options = ["모든 모델"] + list(unique_models)
            model = st.selectbox("모델", model_options)
        else:
            model = st.selectbox("모델", ["모든 모델", "모델A", "모델B", "모델C", "모델D", "모델E"])
    with col2:
        equipment = st.selectbox("설비", ["모든 설비", "설비1", "설비2", "설비3", "설비4", "설비5"])
    with col3:
        # 데이터베이스에서 불량 유형 가져오기
        defect_types = get_defect_type_names()
        defect_type = st.selectbox("불량 유형", ["모든 유형"] + defect_types)
    with col4:
        status = st.selectbox("처리 상태", ["모든 상태", "미처리", "처리 중", "완료"])
    
    # 날짜 범위
    start_date, end_date = st.date_input(
        "날짜 범위",
        [datetime.now().date() - timedelta(days=30), datetime.now().date()],
        max_value=datetime.now().date()
    )
    
    # 데이터 로드
    defects_df = get_defects()
    
    # 필터링
    if model != "모든 모델":
        defects_df = defects_df[defects_df['model'] == model]
    if equipment != "모든 설비":
        defects_df = defects_df[defects_df['equipment'] == equipment]
    if defect_type != "모든 유형":
        defects_df = defects_df[defects_df['defect_type'] == defect_type]
    if status != "모든 상태":
        defects_df = defects_df[defects_df['status'] == status]
    
    # 날짜 필터링
    defects_df = defects_df[
        (pd.to_datetime(defects_df['date']).dt.date >= start_date) &
        (pd.to_datetime(defects_df['date']).dt.date <= end_date)
    ]
    
    # 결과 표시
    st.write(f"총 {len(defects_df)}건의 불량이 발견되었습니다.")
    
    # 테이블로 표시
    st.dataframe(
        defects_df,
        column_config={
            "id": st.column_config.NumberColumn("순번", width="small"),
            "analysis_date": st.column_config.DateColumn("분석일자", format="YYYY-MM-DD"),
            "date": st.column_config.DateColumn("발생일자", format="YYYY-MM-DD"),
            "shift": st.column_config.TextColumn("발생조", width="small"),
            "model": st.column_config.TextColumn("모델", width="medium"),
            "equipment": st.column_config.TextColumn("설비번호", width="medium"),
            "defect_type": st.column_config.TextColumn("불량유형", width="medium"),
            "analysis_result": st.column_config.TextColumn("분석결과", width="medium"),
            "cause": st.column_config.TextColumn("발생원인", width="medium"),
            "action": st.column_config.TextColumn("설비조치현황", width="medium"),
            "status": st.column_config.TextColumn("설비처리상태", width="medium"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # 불량 상세 정보 (선택 시)
    st.subheader("불량 상세 정보")
    defect_id = st.number_input("순번을 입력하세요", min_value=1, max_value=int(defects_df['id'].max()) if not defects_df.empty else 1, value=1)
    
    if st.button("상세 정보 보기"):
        defect = defects_df[defects_df['id'] == defect_id]
        
        if not defect.empty:
            defect = defect.iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**기본 정보**")
                st.write(f"순번: {defect['id']}")
                st.write(f"분석일자: {defect['analysis_date']}")
                st.write(f"발생일자: {defect['date']}")
                st.write(f"발생조: {defect['shift']}")
                st.write(f"모델: {defect['model']}")
                st.write(f"설비번호: {defect['equipment']}")
            
            with col2:
                st.write("**불량 세부 내용**")
                st.write(f"불량유형: {defect['defect_type']}")
                st.write(f"분석결과: {defect['analysis_result']}")
                st.write(f"발생원인: {defect['cause']}")
                st.write(f"설비조치현황: {defect['action']}")
                st.write(f"설비처리상태: {defect['status']}")
            
            # 첨부 이미지 (예시)
            st.write("**첨부 이미지**")
            st.image("https://via.placeholder.com/400x300", caption="불량 이미지")
        else:
            st.error(f"ID {defect_id}에 해당하는 불량 정보를 찾을 수 없습니다.")

def show_defect_analysis():
    """불량 분석 화면 표시"""
    st.subheader("불량 분석")
    
    # 기간 선택
    period = st.selectbox("분석 기간", ["최근 7일", "최근 30일", "최근 90일", "최근 365일"])
    
    # 데이터 로드
    defects_df = get_defects()
    
    # 기간 필터링
    days_map = {"최근 7일": 7, "최근 30일": 30, "최근 90일": 90, "최근 365일": 365}
    days = days_map[period]
    start_date = datetime.now().date() - timedelta(days=days)
    
    defects_df = defects_df[pd.to_datetime(defects_df['date']).dt.date >= start_date]
    
    # 분석 차트들
    col1, col2 = st.columns(2)
    
    with col1:
        # 불량 유형별 분석
        st.subheader("불량 유형별 분석")
        defect_type_counts = defects_df['defect_type'].value_counts().reset_index()
        defect_type_counts.columns = ['defect_type', 'count']
        
        fig = px.pie(defect_type_counts, names='defect_type', values='count', title="불량 유형별 비율")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 설비별 불량 건수
        st.subheader("설비별 불량 건수")
        equipment_counts = defects_df['equipment'].value_counts().reset_index()
        equipment_counts.columns = ['equipment', 'count']
        
        fig = px.bar(equipment_counts, x='equipment', y='count', title="설비별 불량 건수")
        st.plotly_chart(fig, use_container_width=True)
    
    # 모델별 불량 분석
    st.subheader("모델별 불량 분석")
    model_defects = pd.crosstab(defects_df['model'], defects_df['defect_type'])
    
    fig = go.Figure()
    for defect_type in model_defects.columns:
        fig.add_trace(go.Bar(
            x=model_defects.index,
            y=model_defects[defect_type],
            name=defect_type
        ))
    
    fig.update_layout(title="모델별 불량 유형 분석", barmode='stack')
    st.plotly_chart(fig, use_container_width=True)
    
    # 불량 추이 분석
    st.subheader("불량 추이 분석")
    defects_df['date'] = pd.to_datetime(defects_df['date'])
    daily_counts = defects_df.groupby(defects_df['date'].dt.date).size().reset_index()
    daily_counts.columns = ['date', 'count']
    
    fig = px.line(daily_counts, x='date', y='count', title="일별 불량 발생 추이")
    st.plotly_chart(fig, use_container_width=True)

def show_action_management():
    """조치 관리 화면 표시"""
    st.subheader("조치 관리")
    
    # 조치 필요한 불량 목록
    defects_df = get_defects()
    pending_defects = defects_df[defects_df['status'] != "완료"].reset_index(drop=True)
    
    # 필터 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        # 생산모델관리에서 등록된 모델 리스트 불러오기
        models_df = get_all_models()
        if not models_df.empty:
            # 중복 제거된 모델명 리스트 만들기
            unique_models = models_df['name'].unique()
            model_options = ["모든 모델"] + list(unique_models)
            model = st.selectbox("모델 필터", model_options, key="action_model_filter")
            
            # 모델 필터링
            if model != "모든 모델":
                pending_defects = pending_defects[pending_defects['model'] == model]
        else:
            model = st.selectbox("모델 필터", ["모든 모델", "모델A", "모델B", "모델C", "모델D", "모델E"], key="action_model_filter")
    
    with col2:
        # 설비 필터링
        equipment = st.selectbox("설비 필터", ["모든 설비", "설비1", "설비2", "설비3", "설비4", "설비5"], key="action_equipment_filter")
        if equipment != "모든 설비":
            pending_defects = pending_defects[pending_defects['equipment'] == equipment]
    
    if pending_defects.empty:
        st.success("모든 불량이 처리되었습니다.")
    else:
        st.write(f"{len(pending_defects)}건의 미처리 불량이 있습니다.")
        
        # 테이블로 표시
        st.dataframe(
            pending_defects,
            column_config={
                "id": st.column_config.NumberColumn("순번", width="small"),
                "analysis_date": st.column_config.DateColumn("분석일자", format="YYYY-MM-DD"),
                "date": st.column_config.DateColumn("발생일자", format="YYYY-MM-DD"),
                "shift": st.column_config.TextColumn("발생조", width="small"),
                "model": st.column_config.TextColumn("모델", width="medium"),
                "equipment": st.column_config.TextColumn("설비번호", width="medium"),
                "defect_type": st.column_config.TextColumn("불량유형", width="medium"),
                "analysis_result": st.column_config.TextColumn("분석결과", width="medium"),
                "cause": st.column_config.TextColumn("발생원인", width="medium"),
                "action": st.column_config.TextColumn("설비조치현황", width="medium"),
                "status": st.column_config.TextColumn("설비처리상태", width="medium"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 조치 입력 폼
        with st.form("action_form"):
            st.subheader("조치 입력")
            
            defect_id = st.number_input("순번", min_value=1)
            action_desc = st.text_area("설비조치현황")
            action_date = st.date_input("조치일", datetime.now().date())
            
            # 검사자 관리 페이지에서 검사자 목록 가져오기
            inspectors = get_all_inspectors()
            if inspectors:
                # 검사자 목록에서 이름과 아이디 조합으로 드롭다운 옵션 생성
                inspector_options = [f"{insp['name']} ({insp['id']})" for insp in inspectors]
                default_index = 0
                # 현재 로그인한 사용자와 일치하는 검사자가 있으면 그 사람을 기본값으로 설정
                if st.session_state.user_name:
                    for i, option in enumerate(inspector_options):
                        if st.session_state.user_name in option:
                            default_index = i
                            break
                
                action_by = st.selectbox("작업자", inspector_options, index=default_index)
            else:
                # 검사자 목록이 없을 경우 텍스트 입력 사용
                action_by = st.text_input("작업자", value=st.session_state.user_name)
            
            status = st.selectbox("설비처리상태", ["처리 중", "완료"])
            
            submit = st.form_submit_button("조치 저장")
            
            if submit:
                # 해당 ID의 불량이 존재하는지 확인
                if defect_id in pending_defects['id'].values:
                    # 여기서는 데이터 저장 로직이 없으므로 성공 메시지만 표시
                    st.success(f"순번 {defect_id}에 대한 조치가 저장되었습니다.")
                    # 실제 구현에서는 Supabase에 데이터 저장
                else:
                    st.error(f"순번 {defect_id}에 해당하는 미처리 불량을 찾을 수 없습니다.")

def get_defects():
    """불량 데이터 반환 (예시 데이터)"""
    # 오늘 날짜 기준으로 랜덤 불량 데이터 생성
    today = datetime.now().date()
    
    # 생산모델관리에서 등록된 모델 리스트 불러오기
    models_df = get_all_models()
    
    # 모델 목록 준비
    if not models_df.empty:
        # 등록된 모델이 있으면 그것을 사용
        models = models_df['name'].unique()
    else:
        # 등록된 모델이 없으면 기본 모델 사용
        models = [f"모델{chr(65 + i)}" for i in range(5)]  # 모델A, 모델B, ...
    
    # 불량 유형 목록 가져오기
    defect_types = get_defect_type_names()
    
    data = []
    for i in range(1, 31):
        date = today - timedelta(days=i % 30)
        analysis_date = date + timedelta(days=1)  # 분석일자는 발생일 다음날로 가정
        shift = ["주간", "야간"][i % 2]  # 발생조: 주간/야간
        model = models[i % len(models)]  # 등록된 모델 중에서 선택
        equipment = f"설비{i % 5 + 1}"
        defect_type = defect_types[i % len(defect_types)]
        analysis_result = ["부품 교체 필요", "설비 조정 필요", "공구 교체 필요", "검사 필요", "기타"][i % 5]
        cause = ["공구 마모", "진동", "재료 결함", "작업자 실수", "설비 오류"][i % 5]
        action = ["공구 교체", "설비 조정", "재료 교체", "작업자 교육", "설비 수리"][i % 5]
        status = ["미처리", "처리 중", "완료"][min(i % 3, 2)]
        
        data.append({
            "id": i,
            "analysis_date": analysis_date.strftime('%Y-%m-%d'),
            "date": date.strftime('%Y-%m-%d'),
            "shift": shift,
            "model": model,
            "equipment": equipment,
            "defect_type": defect_type,
            "analysis_result": analysis_result,
            "cause": cause,
            "action": action if status != "미처리" else "",
            "status": status
        })
    
    return pd.DataFrame(data) 