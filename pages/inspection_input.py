import streamlit as st
import pandas as pd
from datetime import datetime
import io
from PIL import Image
import uuid
from pages.inspector_management import get_all_inspectors
from pages.item_management import get_all_models
from utils.supabase_client import get_supabase_client

def show_inspection_input():
    """검사 데이터 입력 화면 표시"""
    st.title("검사실적 관리")
    
    # 세션 상태에 검사 데이터 초기화
    if "inspection_data" not in st.session_state:
        st.session_state.inspection_data = []
    
    # 탭 생성
    tabs = st.tabs(["실적 데이터 조회", "실적 데이터 입력", "데이터 검증"])
    
    with tabs[0]:
        show_inspection_data()
    
    with tabs[1]:
        show_data_input_form()
    
    with tabs[2]:
        show_data_validation()

def show_inspection_data():
    """검사 데이터 조회 화면 표시"""
    st.header("검사실적 데이터 조회")
    
    # 검색 필터
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("시작일", datetime.now().date(), key="search_start_date")
    with col2:
        end_date = st.date_input("종료일", datetime.now().date(), key="search_end_date")
    
    # 모델 데이터 가져오기
    try:
        # 모델 정보 가져오기 (없으면 기본값 사용)
        models_df = get_all_models()
        model_options = ["전체"] + [model["name"] for model in models_df.to_dict('records')]
    except:
        model_options = ["전체", "모델A", "모델B", "모델C", "모델D", "모델E"]
        
    with col3:
        selected_model = st.selectbox("모델 선택", model_options, key="search_model")
    
    # 검사자 필터 추가
    col1, col2 = st.columns(2)
    with col1:
        inspector_options = ["전체"]
        
        # 실제 검사자 데이터 가져오기
        try:
            inspectors = get_all_inspectors()
            inspector_options += [f"{insp['name']}" for insp in inspectors]
        except:
            inspector_options += ["관리자", "검사자1", "검사자2"]
            
        selected_inspector = st.selectbox("검사원 선택", inspector_options, key="search_inspector")
    
    with col2:
        search_lot = st.text_input("LOT 번호", key="search_lot")
    
    if st.button("검색", key="search_button"):
        # 세션 상태에 저장된 검사 데이터 가져오기
        if "inspection_data" in st.session_state and st.session_state.inspection_data:
            # 데이터프레임으로 변환
            df = pd.DataFrame(st.session_state.inspection_data)
            
            # 필터 적용
            if len(df) > 0:
                # 날짜 필터링
                df["검사일자"] = pd.to_datetime(df["검사일자"])
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                df = df[(df["검사일자"] >= start_date) & (df["검사일자"] <= end_date)]
                
                # 모델 필터링
                if selected_model != "전체":
                    df = df[df["모델명"] == selected_model]
                
                # 검사자 필터링
                if selected_inspector != "전체":
                    df = df[df["검사원"] == selected_inspector]
                
                # LOT 번호 필터링
                if search_lot:
                    df = df[df["LOT 번호"].str.contains(search_lot, case=False)]
                
                # 결과 표시
                if len(df) > 0:
                    # 날짜 형식을 문자열로 변환
                    df["검사일자"] = df["검사일자"].dt.strftime("%Y-%m-%d")
                    
                    # 불필요한 컬럼 제거
                    display_columns = [
                        "검사일자", "검사원", "LOT 번호", "공정", "모델명", 
                        "계획 수량", "총 검사 수량", "불량 수량"
                    ]
                    
                    # 불량률 컬럼 추가
                    df["불량률"] = df.apply(
                        lambda row: f"{(row['불량 수량'] / row['총 검사 수량'] * 100):.1f}%" 
                        if row['총 검사 수량'] > 0 else "0.0%", 
                        axis=1
                    )
                    
                    display_columns.append("불량률")
                    
                    # 화면에 표시
                    st.dataframe(
                        df[display_columns], 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # 검색 결과 요약
                    st.success(f"총 {len(df)}건의 검사 데이터가 검색되었습니다.")
                else:
                    st.info("검색 조건에 맞는 데이터가 없습니다.")
            else:
                st.info("저장된 검사 데이터가 없습니다.")
        else:
            st.info("저장된 검사 데이터가 없습니다. 실적 데이터 입력 탭에서 데이터를 추가해주세요.")

def show_data_input_form():
    """검사 데이터 입력 폼 표시"""
    st.header("검사실적 데이터 입력")
    
    # 검사자 데이터 가져오기
    inspectors = get_all_inspectors()
    
    # 활성 상태인 검사자만 필터링
    active_inspectors = [insp for insp in inspectors if insp["status"] == "활성"]
    
    # 검사자 옵션 생성
    inspector_options = ["검사원 선택"] + [f"{insp['name']} ({insp['id']})" for insp in active_inspectors]
    
    # 공정 목록 - 이미지에 표시된 공정으로 수정
    processes = ["공정을 선택하세요", "IQC", "CNC1_PQC", "CNC2_PQC", "OQC", "CNC OQC"]
    
    # 모델 데이터 가져오기
    try:
        # 모델 정보 가져오기 (없으면 기본값 사용)
        models_df = get_all_models()
        model_options = ["모델을 선택하세요"] + [model["name"] for model in models_df.to_dict('records')]
    except:
        model_options = ["모델을 선택하세요", "모델A", "모델B", "모델C", "모델D", "모델E"]
    
    # 왼쪽 열
    col1, col2 = st.columns(2)
    
    with col1:
        # 검사원 이름 (검사자 관리에서 가져온 목록 사용)
        selected_inspector = st.selectbox("검사원", inspector_options)
        
        # 검사원 ID 자동 설정
        inspector_id = ""
        if selected_inspector != "검사원 선택":
            # 선택된 검사원 정보에서 ID 추출
            inspector_name = selected_inspector.split(" (")[0]
            inspector_id = selected_inspector.split(" (")[1].rstrip(")")
            
            # 선택된 검사자의 공정 정보 가져오기 (더 이상 사용하지 않음)
            default_process = processes[0]
        else:
            inspector_id = ""
            default_process = processes[0]
        
        st.text_input("검사원 ID", value=inspector_id, disabled=True)
        
        # 공정 (이미지에 표시된 공정 목록으로 변경)
        process = st.selectbox("공정", processes)
        
        # 모델명
        model = st.selectbox("모델명", model_options)
    
    with col2:
        # 검사일자
        inspection_date = st.date_input("검사일자", datetime.now().date())
        
        # LOT 번호
        lot_number = st.text_input("LOT 번호", placeholder="LOT 번호를 입력하세요")
        
        # 작업 시간(분)
        work_time = st.number_input("작업 시간(분)", min_value=0, value=60, step=5)
    
    # 수량 입력 섹션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 계획 수량
        planned_qty = st.number_input("계획 수량", min_value=0, value=100, step=1)
    
    with col2:
        # 총 검사 수량
        total_inspected = st.number_input("총 검사 수량", min_value=0, value=0, step=1)
    
    with col3:
        # 불량 수량
        defect_qty = st.number_input("불량 수량", min_value=0, value=0, step=1)
    
    # 검사 지표 계산 및 표시
    with st.container():
        st.header("검사 지표")
        
        # 불량률, 목표대비 검사율, 시간당 검사량을 나란히 표시
        metric_cols = st.columns(3)
        
        # 1. 불량률
        defect_rate = 0
        if total_inspected > 0:
            defect_rate = (defect_qty / total_inspected) * 100
        
        with metric_cols[0]:
            st.metric(
                label="불량률", 
                value=f"{defect_rate:.1f}%"
            )
        
        # 2. 목표대비 검사율
        inspection_rate = 0
        if planned_qty > 0:
            inspection_rate = (total_inspected / planned_qty) * 100
            
        inspection_status = "목표 달성" if inspection_rate >= 100 else "목표 미달"
        inspection_delta_color = "normal" if inspection_rate >= 100 else "off"
        
        with metric_cols[1]:
            st.metric(
                label="목표대비 검사율", 
                value=f"{inspection_rate:.1f}%",
                delta=inspection_status,
                delta_color=inspection_delta_color
            )
        
        # 3. 시간당 검사량
        hourly_rate = 0
        if work_time > 0:
            hourly_rate = (total_inspected / work_time) * 60  # 시간당 검사량으로 변환
            
        with metric_cols[2]:
            st.metric(
                label="시간당 검사량", 
                value=f"{hourly_rate:.1f}개/시간",
                delta="목표 달성 완료" if hourly_rate > 0 else None,
                delta_color="normal" if hourly_rate > 0 else "off"
            )
    
    # 비고
    note = st.text_area("비고", placeholder="특이사항이 있으면 입력하세요")
    
    # 불량 세부 정보 입력 섹션
    defect_details = {}
    defect_quantities = {}
    total_defect_qty = 0
    selected_defects = []
    defect_desc = ""
    
    if defect_qty > 0:
        st.markdown("---")
        st.subheader("불량 정보")
        
        # 불량 유형 선택 (복수 선택 가능)
        defect_types = ["치수 불량", "표면 결함", "가공 불량", "재료 결함", "기타"]
        selected_defects = st.multiselect("불량 유형 선택", defect_types, key="defect_types")
        
        # 선택된 불량 유형에 대해 각각 수량 입력 필드 생성
        if selected_defects:
            st.write("각 불량 유형별 수량을 입력하세요:")
            cols = st.columns(min(3, len(selected_defects)))
            
            for i, defect_type in enumerate(selected_defects):
                with cols[i % 3]:
                    qty = st.number_input(
                        f"{defect_type} 수량",
                        min_value=0,
                        value=1 if i == 0 else 0,
                        key=f"defect_qty_{i}"
                    )
                    defect_quantities[defect_type] = qty
                    total_defect_qty += qty
            
            # 불량 수량과 유형별 수량 합계 검증
            if total_defect_qty != defect_qty:
                st.warning(f"입력한 불량 수량({defect_qty})과 유형별 불량 수량의 합({total_defect_qty})이 일치하지 않습니다.")
            else:
                st.success("불량 수량이 일치합니다.")
                
                # 불량 세부 정보 저장
                defect_details = {
                    "유형별 수량": defect_quantities,
                    "불량 설명": defect_desc
                }
        
        # 불량 상세 설명
        defect_desc = st.text_area("불량 상세 설명")
        
        # 사진 첨부
        uploaded_file = st.file_uploader("불량 사진 첨부", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="첨부된 불량 사진", width=300)
    
    st.markdown("---")
    
    # 디버그 모드 추가 (개발 중 확인용)
    debug_mode = st.checkbox("디버그 모드", value=False, key="debug_mode")
    if debug_mode:
        st.info("디버그 모드가 활성화되었습니다. 저장 시 세부 정보가 표시됩니다.")
    
    # 저장 버튼
    if st.button("데이터 저장", type="primary"):
        if selected_inspector == "검사원 선택" or process == "공정을 선택하세요" or model == "모델을 선택하세요" or not lot_number:
            st.error("검사원, 공정, 모델, LOT 번호는 필수 입력 항목입니다.")
        elif defect_qty > 0 and (not selected_defects or total_defect_qty != defect_qty):
            st.error("불량 유형 선택과 유형별 수량을 정확히 입력해주세요.")
        else:
            # 저장할 데이터 생성
            inspector_name = selected_inspector.split(" (")[0] if selected_inspector != "검사원 선택" else ""
            
            data = {
                "검사원": inspector_name,
                "검사일자": inspection_date,
                "검사원 ID": inspector_id,
                "LOT 번호": lot_number,
                "공정": process,
                "작업 시간(분)": work_time,
                "모델명": model,
                "계획 수량": planned_qty,
                "총 검사 수량": total_inspected,
                "불량 수량": defect_qty,
                "검사 지표": {
                    "불량률": f"{defect_rate:.1f}%",
                    "목표대비 검사율": f"{inspection_rate:.1f}%", 
                    "시간당 검사량": f"{hourly_rate:.1f}개/시간"
                },
                "저장일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 불량 세부 정보가 있을 경우 추가
            if defect_qty > 0 and selected_defects:
                data["불량 유형"] = {d: defect_quantities.get(d, 0) for d in selected_defects}
                data["불량 상세 설명"] = defect_desc
            
            # 세션 상태에 데이터 저장
            if "inspection_data" not in st.session_state:
                st.session_state.inspection_data = []
                
            st.session_state.inspection_data.append(data)
            
            # Supabase에 데이터 저장
            try:
                # Supabase 클라이언트 연결
                supabase = get_supabase_client()
                
                if debug_mode:
                    st.write("Supabase 클라이언트 연결 성공")
                
                # 검사자 UUID 확인 - 실제 UUID 형식이 아닌 경우 임시 UUID 생성
                inspector_uuid = inspector_id
                try:
                    # UUID 형식 검증
                    uuid.UUID(inspector_id)
                except (ValueError, AttributeError):
                    # 유효한 UUID가 아니면 임시 UUID 생성
                    inspector_uuid = str(uuid.uuid4())
                    if debug_mode:
                        st.warning(f"검사자 ID '{inspector_id}'가 유효한 UUID가 아니므로 임시 UUID로 대체: {inspector_uuid}")
                
                # 검사자 레코드 확인 - 없으면 생성
                inspector_check = supabase.table('inspectors').select('*').eq('id', inspector_uuid).execute()
                
                if debug_mode:
                    st.write(f"검사자 조회 결과: {len(inspector_check.data)}개 레코드 발견")
                
                if not inspector_check.data:
                    # 검사자 레코드 생성
                    inspector_data = {
                        "id": inspector_uuid,
                        "name": inspector_name,
                        "employee_id": inspector_id,
                        "department": "품질관리부"  # 기본값
                    }
                    inspector_result = supabase.table('inspectors').insert(inspector_data).execute()
                    if debug_mode:
                        st.write(f"새 검사자 생성: {inspector_result.data}")
                
                # 모델 ID 가져오기
                models_response = supabase.table('production_models').select('*').eq('model_name', model).execute()
                
                if debug_mode:
                    st.write(f"모델 조회 결과: {len(models_response.data)}개 레코드 발견")
                    if models_response.data:
                        st.write(f"조회된 모델 데이터: {models_response.data}")
                
                model_id = None
                if not models_response.data:
                    # 모델이 없으면 새로 생성
                    model_data = {
                        "model_no": f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "model_name": model,
                        "process": process
                    }
                    model_result = supabase.table('production_models').insert(model_data).execute()
                    model_id = model_result.data[0]['id']
                    if debug_mode:
                        st.write(f"새 모델 생성: {model_result.data}")
                else:
                    model_id = models_response.data[0]['id']
                
                if debug_mode:
                    st.write(f"사용할 모델 ID: {model_id}")
                
                # 검사 데이터 저장
                inspection_data = {
                    "inspection_date": inspection_date.strftime("%Y-%m-%d"),
                    "inspector_id": inspector_uuid,
                    "model_id": model_id,
                    "result": "불합격" if defect_qty > 0 else "합격",
                    "quantity": total_inspected,
                    "notes": note if note else None
                }
                
                if debug_mode:
                    st.write(f"저장할 검사 데이터: {inspection_data}")
                
                inspection_result = supabase.table('inspection_data').insert(inspection_data).execute()
                inspection_id = inspection_result.data[0]['id']
                
                if debug_mode:
                    st.write(f"저장된 검사 데이터: {inspection_result.data}")
                
                # 불량 데이터가 있는 경우 저장
                if defect_qty > 0 and selected_defects:
                    for defect_type, count in defect_quantities.items():
                        if count > 0:
                            defect_data = {
                                "inspection_id": inspection_id,
                                "defect_type": defect_type,
                                "defect_count": count,
                                "description": defect_desc if defect_desc else None
                            }
                            defect_result = supabase.table('defects').insert(defect_data).execute()
                            if debug_mode:
                                st.write(f"저장된 불량 데이터: {defect_result.data}")
                
                st.success(f"검사 데이터가 성공적으로 Supabase에 저장되었습니다. (검사 ID: {inspection_id})")
            except Exception as e:
                st.error(f"Supabase 저장 중 오류가 발생했습니다: {str(e)}")
                st.exception(e)
            
            st.success(f"검사 데이터가 성공적으로 저장되었습니다. (현재 총 {len(st.session_state.inspection_data)}건의 데이터가 저장됨)")
            
            # 저장된 데이터 표시
            with st.expander("저장된 데이터 확인"):
                st.json(data)
            
            # 입력 필드 초기화를 위한 페이지 새로고침
            st.rerun()

def show_data_validation():
    """데이터 검증 화면 표시"""
    st.header("데이터 검증")
    
    st.info("이 기능은 입력된 데이터의 유효성을 검증하는 기능입니다.")
    
    # 날짜 범위 선택
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("검증 시작일", datetime.now().date())
    with col2:
        end_date = st.date_input("검증 종료일", datetime.now().date())
    
    if st.button("데이터 검증 실행"):
        # 실제 검사 데이터 기반 검증
        if "inspection_data" in st.session_state and st.session_state.inspection_data:
            total_count = len(st.session_state.inspection_data)
            valid_count = sum(1 for data in st.session_state.inspection_data if 
                             data["총 검사 수량"] >= data["불량 수량"])
            invalid_count = total_count - valid_count
            validation_rate = (valid_count / total_count * 100) if total_count > 0 else 0
            
            if invalid_count > 0:
                st.warning(f"검증 완료! {invalid_count}개의 이상 데이터가 발견되었습니다.")
            else:
                st.success("데이터 검증 완료! 이상이 없습니다.")
            
            # 검증 결과 요약
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(label="총 검사 건수", value=str(total_count))
            with col2:
                st.metric(label="검증된 건수", value=str(valid_count))
            with col3:
                st.metric(label="이상치 건수", value=str(invalid_count))
            with col4:
                st.metric(label="검증률", value=f"{validation_rate:.1f}%")
        else:
            # 예시 검증 결과 (데이터가 없을 경우)
            st.info("저장된 검사 데이터가 없습니다. 실적 데이터 입력 탭에서 데이터를 추가해주세요.")
            
            # 검증 결과 요약 (샘플)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(label="총 검사 건수", value="0")
            with col2:
                st.metric(label="검증된 건수", value="0")
            with col3:
                st.metric(label="이상치 건수", value="0")
            with col4:
                st.metric(label="검증률", value="0%")

def get_inspection_items(model):
    """모델별 검사 항목 반환 (예시 데이터)"""
    if model == "모델A":
        return [
            {"id": 1, "name": "길이", "standard": "100", "tolerance": "0.5", "unit": "mm"},
            {"id": 2, "name": "너비", "standard": "50", "tolerance": "0.3", "unit": "mm"},
            {"id": 3, "name": "높이", "standard": "25", "tolerance": "0.2", "unit": "mm"},
            {"id": 4, "name": "무게", "standard": "250", "tolerance": "5", "unit": "g"},
            {"id": 5, "name": "표면 거칠기", "standard": "1.6", "tolerance": "0.4", "unit": "Ra"}
        ]
    elif model == "모델B":
        return [
            {"id": 6, "name": "길이", "standard": "120", "tolerance": "0.5", "unit": "mm"},
            {"id": 7, "name": "너비", "standard": "60", "tolerance": "0.3", "unit": "mm"},
            {"id": 8, "name": "높이", "standard": "30", "tolerance": "0.2", "unit": "mm"},
            {"id": 9, "name": "무게", "standard": "300", "tolerance": "5", "unit": "g"},
            {"id": 10, "name": "표면 거칠기", "standard": "1.8", "tolerance": "0.4", "unit": "Ra"}
        ]
    else:
        return [
            {"id": 11, "name": "길이", "standard": "150", "tolerance": "0.8", "unit": "mm"},
            {"id": 12, "name": "너비", "standard": "75", "tolerance": "0.5", "unit": "mm"},
            {"id": 13, "name": "높이", "standard": "40", "tolerance": "0.3", "unit": "mm"},
            {"id": 14, "name": "무게", "standard": "350", "tolerance": "8", "unit": "g"},
            {"id": 15, "name": "표면 거칠기", "standard": "2.0", "tolerance": "0.5", "unit": "Ra"}
        ] 