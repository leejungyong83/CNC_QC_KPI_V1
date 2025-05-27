import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from PIL import Image
import uuid
from pages.inspector_management import get_all_inspectors
from pages.item_management import get_all_models
from utils.supabase_client import get_supabase_client
from utils.defect_utils import get_defect_type_names
import random

def show_inspection_crud():
    """검사 데이터 CRUD 화면 표시"""
    st.title("검사실적 관리")
    
    # 세션 상태에 검사 데이터 초기화
    if "inspection_data" not in st.session_state:
        st.session_state.inspection_data = []
    
    # 탭 생성 - CRUD 형태
    tabs = st.tabs(["목록 조회", "데이터 입력", "데이터 수정", "데이터 삭제"])
    
    with tabs[0]:
        show_inspection_list()
    
    with tabs[1]:
        show_data_input_form()
    
    with tabs[2]:
        show_data_edit_form()
    
    with tabs[3]:
        show_data_delete_form()

def get_supabase_inspectors():
    """Supabase에서 실제 검사자 데이터를 가져오는 함수"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('inspectors').select('id, name, employee_id, department').execute()
        
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.warning(f"Supabase 검사자 데이터 조회 실패: {str(e)}")
        return []

def get_supabase_models():
    """Supabase에서 실제 모델 데이터를 가져오는 함수"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('production_models').select('id, model_name, model_no').execute()
        
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.warning(f"Supabase 모델 데이터 조회 실패: {str(e)}")
        return []

def show_inspection_list():
    """검사 데이터 목록 조회 화면 표시"""
    st.header("검사실적 데이터 조회")
    
    # Supabase 클라이언트 가져오기
    supabase = get_supabase_client()
    
    # 검색 필터
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("시작일", datetime.now().date(), key="search_start_date")
    with col2:
        end_date = st.date_input("종료일", datetime.now().date(), key="search_end_date")
    
    # 모델 데이터 가져오기
    try:
        models_df = get_all_models()
        model_options = ["전체"] + [model["name"] for model in models_df.to_dict('records')]
    except:
        model_options = ["전체", "PA1", "PA2", "PA3", "B6", "B6M"]
        
    with col3:
        selected_model = st.selectbox("모델 선택", model_options, key="search_model")
    
    # 검사자 필터 추가
    col1, col2 = st.columns(2)
    with col1:
        inspector_options = ["전체"]
        
        try:
            inspectors = get_all_inspectors()
            inspector_options += [f"{insp['name']}" for insp in inspectors]
        except:
            inspector_options += ["김검사", "이검사", "박검사"]
            
        selected_inspector = st.selectbox("검사원 선택", inspector_options, key="search_inspector")
    
    with col2:
        search_lot = st.text_input("LOT 번호", key="search_lot")
    
    if st.button("검색", key="search_button"):
        try:
            # Supabase에서 데이터 조회 시도 - 실제 테이블 구조에 맞게 수정
            response = supabase.table('inspection_data').select('*').execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # 날짜 필터 적용
                if start_date and end_date:
                    df['inspection_date'] = pd.to_datetime(df['inspection_date'])
                    start_datetime = pd.to_datetime(start_date)
                    end_datetime = pd.to_datetime(end_date)
                    df = df[(df['inspection_date'] >= start_datetime) & (df['inspection_date'] <= end_datetime)]
                
                # 추가 필터링
                if selected_model != "전체":
                    df = df[df["model_id"].str.contains(selected_model, case=False, na=False)]
                
                if selected_inspector != "전체":
                    df = df[df["inspector_id"].str.contains(selected_inspector, case=False, na=False)]
                
                # 결과 표시
                if len(df) > 0:
                    # 컬럼명 한글로 변경 - 실제 테이블 구조에 맞게
                    display_df = df.rename(columns={
                        'inspection_date': '검사일자',
                        'inspector_id': '검사원',
                        'model_id': '모델명',
                        'result': '검사결과',
                        'quantity': '검사수량',
                        'notes': '비고'
                    })
                    
                    # 화면에 표시할 컬럼 선택
                    display_columns = [
                        "검사일자", "검사원", "모델명", "검사결과", "검사수량", "비고"
                    ]
                    
                    st.dataframe(
                        display_df[display_columns], 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    st.success(f"총 {len(df)}건의 검사 데이터가 검색되었습니다.")
                else:
                    st.info("검색 조건에 맞는 데이터가 없습니다.")
            else:
                st.info("저장된 검사 데이터가 없습니다.")
                
        except Exception as e:
            st.warning(f"Supabase 연결 실패: {str(e)}. 오프라인 모드로 실행됩니다.")
            # 오프라인 모드에서는 세션 데이터 사용
            if "inspection_data" not in st.session_state or not st.session_state.inspection_data:
                st.session_state.inspection_data = generate_sample_inspection_data()
                st.info("샘플 데이터를 생성했습니다.")
            
            df = pd.DataFrame(st.session_state.inspection_data)
            if len(df) > 0:
                # 필터 적용
                df["검사일자"] = pd.to_datetime(df["검사일자"])
                start_datetime = pd.to_datetime(start_date)
                end_datetime = pd.to_datetime(end_date)
                df = df[(df["검사일자"] >= start_datetime) & (df["검사일자"] <= end_datetime)]
                
                if selected_model != "전체":
                    df = df[df["모델명"] == selected_model]
                
                if selected_inspector != "전체":
                    df = df[df["검사원"] == selected_inspector]
                
                if search_lot:
                    df = df[df["LOT 번호"].str.contains(search_lot, case=False)]
                
                # 결과 표시
                if len(df) > 0:
                    df["검사일자"] = df["검사일자"].dt.strftime("%Y-%m-%d")
                    
                    display_columns = [
                        "검사일자", "검사원", "LOT 번호", "공정", "모델명", 
                        "계획 수량", "총 검사 수량", "불량 수량"
                    ]
                    
                    df["불량률"] = df.apply(
                        lambda row: f"{(row['불량 수량'] / row['총 검사 수량'] * 100):.1f}%" 
                        if row['총 검사 수량'] > 0 else "0.0%", 
                        axis=1
                    )
                    
                    display_columns.append("불량률")
                    
                    st.dataframe(
                        df[display_columns], 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    st.success(f"총 {len(df)}건의 검사 데이터가 검색되었습니다.")
                else:
                    st.info("검색 조건에 맞는 데이터가 없습니다.")

def show_data_input_form():
    """검사 데이터 입력 폼 표시 - 기존 디자인 유지 + 불량 유형별 수량 입력 추가"""
    st.header("검사실적 데이터 입력")
    
    # Supabase에서 실제 검사자 데이터 가져오기
    supabase_inspectors = get_supabase_inspectors()
    supabase_models = get_supabase_models()
    
    # 검사자 옵션 생성
    if supabase_inspectors:
        # Supabase 데이터 사용 - 모든 검사자 포함
        inspector_options = ["검사원 선택"] + [f"{insp['name']} ({insp['employee_id']})" for insp in supabase_inspectors]
        st.info(f"✅ Supabase에서 {len(supabase_inspectors)}명의 검사자 데이터를 가져왔습니다.")
    else:
        # 오프라인 모드 - 세션 데이터 사용
        try:
            inspectors = get_all_inspectors()
            # status 필터링 제거하고 모든 검사자 사용
            inspector_options = ["검사원 선택"] + [f"{insp['name']} ({insp['id']})" for insp in inspectors]
            st.warning("⚠️ 오프라인 모드: 세션 데이터를 사용합니다.")
        except:
            inspector_options = ["검사원 선택", "김검사 (inspector1)", "이검사 (inspector2)", "박검사 (inspector3)"]
            st.warning("⚠️ 기본 데이터를 사용합니다.")
    
    # 모델 옵션 생성
    if supabase_models:
        # Supabase 데이터 사용
        model_options = ["모델을 선택하세요"] + [model["model_name"] for model in supabase_models]
        st.info(f"✅ Supabase에서 {len(supabase_models)}개의 모델 데이터를 가져왔습니다.")
    else:
        # 오프라인 모드
        try:
            models_df = get_all_models()
            model_options = ["모델을 선택하세요"] + [model["name"] for model in models_df.to_dict('records')]
            st.warning("⚠️ 오프라인 모드: 세션 모델 데이터를 사용합니다.")
        except:
            model_options = ["모델을 선택하세요", "PA1", "PA2", "PA3", "B6", "B6M"]
            st.warning("⚠️ 기본 모델 데이터를 사용합니다.")
    
    # 공정 목록
    processes = ["공정을 선택하세요", "IQC", "CNC1_PQC", "CNC2_PQC", "OQC", "CNC OQC"]
    
    # 왼쪽 열
    col1, col2 = st.columns(2)
    
    with col1:
        # 검사원
        selected_inspector = st.selectbox("검사원", inspector_options)
        
        # 검사원 ID 및 UUID 설정
        inspector_id = ""
        inspector_uuid = ""
        inspector_name = ""
        
        if selected_inspector != "검사원 선택":
            inspector_name = selected_inspector.split(" (")[0]
            inspector_code = selected_inspector.split(" (")[1].rstrip(")")
            
            if supabase_inspectors:
                # Supabase 데이터에서 실제 UUID 찾기
                matching_inspector = next(
                    (insp for insp in supabase_inspectors 
                     if insp['name'] == inspector_name and insp['employee_id'] == inspector_code), 
                    None
                )
                if matching_inspector:
                    inspector_uuid = matching_inspector['id']  # 실제 UUID
                    inspector_id = matching_inspector['employee_id']
                    st.success(f"✅ 검사자 UUID: {inspector_uuid[:8]}...")
                else:
                    st.error("❌ 선택된 검사자의 UUID를 찾을 수 없습니다.")
            else:
                # 오프라인 모드에서는 UUID 생성
                inspector_id = inspector_code
                inspector_uuid = str(uuid.uuid4())
                st.info(f"🔄 오프라인 모드: 임시 UUID 생성 ({inspector_uuid[:8]}...)")
        
        # 검사일자
        inspection_date = st.date_input("검사일자", datetime.now().date())
        
        # 공정
        selected_process = st.selectbox("공정", processes)
        
        # 모델명
        selected_model = st.selectbox("모델명", model_options)
        
        # 모델 UUID 설정
        model_uuid = ""
        if selected_model != "모델을 선택하세요":
            if supabase_models:
                # Supabase 데이터에서 실제 UUID 찾기
                matching_model = next(
                    (model for model in supabase_models if model['model_name'] == selected_model), 
                    None
                )
                if matching_model:
                    model_uuid = matching_model['id']  # 실제 UUID
                    st.success(f"✅ 모델 UUID: {model_uuid[:8]}...")
                else:
                    st.error("❌ 선택된 모델의 UUID를 찾을 수 없습니다.")
            else:
                # 오프라인 모드에서는 UUID 생성
                model_uuid = str(uuid.uuid4())
                st.info(f"🔄 오프라인 모드: 임시 모델 UUID 생성 ({model_uuid[:8]}...)")
    
    with col2:
        # LOT 번호
        lot_number = st.text_input("LOT 번호", placeholder="LOT 번호를 입력하세요")
        
        # 작업 시간
        work_time = st.number_input("작업 시간(분)", min_value=0, value=60)
        
        # 계획 수량
        planned_qty = st.number_input("계획 수량", min_value=0, value=100)
        
        # 총 검사 수량
        total_inspected = st.number_input("총 검사 수량", min_value=0, value=0)
    
    # 불량 수량 입력
    col1, col2, col3 = st.columns(3)
    with col1:
        defect_qty = st.number_input("불량 수량", min_value=0, value=0)
    with col2:
        pass_qty = st.number_input("양품 수량", min_value=0, value=0)
    with col3:
        total_qty = st.number_input("총량 수량", min_value=0, value=0)
    
    # 불량 유형별 수량 입력 섹션 추가
    if defect_qty > 0:
        st.subheader("불량 유형별 수량 입력")
        
        # 불량 유형 목록 가져오기
        try:
            defect_types = get_defect_type_names()
        except:
            defect_types = ["치수 불량", "표면 결함", "가공 불량", "재료 결함", "기타"]
        
        # 불량 유형 복수 선택
        selected_defect_types = st.multiselect(
            "불량 유형 선택 (복수 선택 가능)",
            defect_types,
            help="발생한 불량 유형을 모두 선택하세요"
        )
        
        # 세션 상태에 불량 유형별 수량 저장
        if "defect_type_quantities" not in st.session_state:
            st.session_state.defect_type_quantities = {}
        
        # 선택된 불량 유형별 수량 입력
        defect_type_quantities = {}
        total_defect_input = 0
        
        if selected_defect_types:
            st.write("**각 불량 유형별 수량을 입력하세요:**")
            
            cols = st.columns(min(len(selected_defect_types), 3))
            for i, defect_type in enumerate(selected_defect_types):
                with cols[i % 3]:
                    qty = st.number_input(
                        f"{defect_type}",
                        min_value=0,
                        max_value=defect_qty,
                        value=st.session_state.defect_type_quantities.get(defect_type, 0),
                        key=f"defect_{defect_type}"
                    )
                    defect_type_quantities[defect_type] = qty
                    total_defect_input += qty
            
            # 불량 수량 검증
            if total_defect_input > defect_qty:
                st.error(f"불량 유형별 수량의 합({total_defect_input})이 총 불량 수량({defect_qty})을 초과합니다!")
            elif total_defect_input < defect_qty:
                st.warning(f"불량 유형별 수량의 합({total_defect_input})이 총 불량 수량({defect_qty})보다 적습니다. 남은 수량: {defect_qty - total_defect_input}")
            else:
                st.success("불량 유형별 수량이 정확히 입력되었습니다.")
            
            # 세션 상태 업데이트
            st.session_state.defect_type_quantities = defect_type_quantities
    
    # 검사 지표 섹션
    st.subheader("검사 지표")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        defect_rate = f"{(defect_qty / total_inspected * 100):.1f}%" if total_inspected > 0 else "0.0%"
        st.metric("불량률", defect_rate)
    with col2:
        pass_rate = f"{(pass_qty / total_inspected * 100):.1f}%" if total_inspected > 0 else "0.0%"
        st.metric("양품률", pass_rate)
    with col3:
        productivity = f"{(total_inspected / work_time * 60):.1f}개/시간" if work_time > 0 else "0.0개/시간"
        st.metric("시간당 검사량", productivity)
    
    # 비고
    st.subheader("불량 정보")
    notes = st.text_area("특이사항이 있으면 입력하세요", height=100)
    
    # 불량 사진 업로드
    st.subheader("불량 사진 첨부")
    uploaded_file = st.file_uploader(
        "불량 사진을 업로드하세요",
        type=['jpg', 'jpeg', 'png'],
        help="Limit 200MB per file • JPG, JPEG, PNG"
    )
    
    # 디버그 모드
    debug_mode = st.checkbox("디버그 모드")
    
    # 데이터 저장 버튼
    if st.button("데이터 저장", type="primary"):
        # 입력 검증
        if selected_inspector == "검사원 선택":
            st.error("검사원을 선택해주세요.")
            return
        
        if selected_process == "공정을 선택하세요":
            st.error("공정을 선택해주세요.")
            return
        
        if selected_model == "모델을 선택하세요":
            st.error("모델을 선택해주세요.")
            return
        
        if not lot_number:
            st.error("LOT 번호를 입력해주세요.")
            return
        
        # UUID 검증
        if not inspector_uuid:
            st.error("검사자 UUID가 설정되지 않았습니다.")
            return
            
        if not model_uuid:
            st.error("모델 UUID가 설정되지 않았습니다.")
            return
        
        # 불량 유형별 수량 검증
        if defect_qty > 0 and selected_defect_types:
            total_defect_input = sum(defect_type_quantities.values())
            if total_defect_input != defect_qty:
                st.error("불량 유형별 수량의 합이 총 불량 수량과 일치하지 않습니다.")
                return
        
        # 데이터 저장
        try:
            supabase = get_supabase_client()
            
            # 검사 결과 결정
            inspection_result = "불합격" if defect_qty > 0 else "합격"
            
            # Supabase에 저장할 데이터 준비 - 실제 테이블 구조에 맞게
            inspection_data = {
                "inspection_date": inspection_date.isoformat(),
                "inspector_id": inspector_uuid,  # 실제 UUID 사용
                "model_id": model_uuid,  # 실제 UUID 사용
                "result": inspection_result,
                "quantity": total_inspected,
                "notes": notes
            }
            
            # 불량 유형별 수량 정보를 notes에 추가
            if defect_qty > 0 and selected_defect_types:
                defect_details = []
                for defect_type, qty in defect_type_quantities.items():
                    if qty > 0:
                        defect_details.append(f"{defect_type}: {qty}개")
                
                if defect_details:
                    defect_info = f"불량 유형별 수량: {', '.join(defect_details)}"
                    inspection_data["notes"] = f"{notes}\n{defect_info}" if notes else defect_info
            
            # 디버그 정보 표시
            if debug_mode:
                st.write("**저장할 데이터:**")
                st.json(inspection_data)
            
            # Supabase에 저장 시도
            response = supabase.table('inspection_data').insert(inspection_data).execute()
            
            if response.data:
                st.success("✅ 검사 데이터가 성공적으로 저장되었습니다!")
                # 불량 유형별 수량 초기화
                st.session_state.defect_type_quantities = {}
                st.rerun()
            else:
                raise Exception("데이터 저장 실패")
                
        except Exception as e:
            st.error(f"❌ Supabase 저장 실패: {str(e)}")
            
            # 세션 상태에 저장 (오프라인 모드)
            session_data = {
                "검사원": inspector_name,
                "검사일자": inspection_date,
                "검사원 ID": inspector_id,
                "LOT 번호": lot_number,
                "공정": selected_process,
                "작업 시간(분)": work_time,
                "모델명": selected_model,
                "계획 수량": planned_qty,
                "총 검사 수량": total_inspected,
                "불량 수량": defect_qty,
                "불량 유형별 수량": defect_type_quantities if defect_qty > 0 else {},
                "저장일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if "inspection_data" not in st.session_state:
                st.session_state.inspection_data = []
            
            st.session_state.inspection_data.append(session_data)
            st.warning("⚠️ 검사 데이터가 세션에 임시 저장되었습니다!")
            
            # 불량 유형별 수량 초기화
            st.session_state.defect_type_quantities = {}

def show_data_edit_form():
    """검사 데이터 수정 폼"""
    st.header("검사실적 데이터 수정")
    
    # 수정할 데이터 선택
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('inspection_data').select('*').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # 수정할 레코드 선택
            if len(df) > 0:
                # 선택 옵션 생성
                options = []
                for _, row in df.iterrows():
                    option = f"{row['inspection_date']} - {row['inspector_id']} - {row['result']}"
                    options.append(option)
                
                selected_option = st.selectbox("수정할 데이터 선택", ["선택하세요"] + options)
                
                if selected_option != "선택하세요":
                    # 선택된 레코드 찾기
                    selected_index = options.index(selected_option)
                    selected_record = df.iloc[selected_index]
                    
                    # 수정 폼 표시
                    with st.form("edit_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_inspector = st.text_input("검사원", value=selected_record['inspector_id'])
                            new_date = st.date_input("검사일자", value=pd.to_datetime(selected_record['inspection_date']).date())
                            new_model = st.text_input("모델명", value=selected_record['model_id'])
                        
                        with col2:
                            new_result = st.selectbox("검사결과", ["합격", "불합격"], 
                                                    index=0 if selected_record['result'] == "합격" else 1)
                            new_quantity = st.number_input("검사수량", value=int(selected_record['quantity']))
                            new_notes = st.text_area("비고", value=selected_record.get('notes', ''))
                        
                        submitted = st.form_submit_button("수정 저장")
                        
                        if submitted:
                            try:
                                update_data = {
                                    "inspector_id": new_inspector,
                                    "inspection_date": new_date.isoformat(),
                                    "model_id": new_model,
                                    "result": new_result,
                                    "quantity": new_quantity,
                                    "notes": new_notes
                                }
                                
                                response = supabase.table('inspection_data').update(update_data).eq('id', selected_record['id']).execute()
                                
                                if response.data:
                                    st.success("데이터가 성공적으로 수정되었습니다!")
                                    st.rerun()
                                else:
                                    st.error("데이터 수정에 실패했습니다.")
                                    
                            except Exception as e:
                                st.error(f"수정 중 오류가 발생했습니다: {str(e)}")
            else:
                st.info("수정할 데이터가 없습니다.")
        else:
            st.info("저장된 검사 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"데이터 조회 중 오류가 발생했습니다: {str(e)}")

def show_data_delete_form():
    """검사 데이터 삭제 폼"""
    st.header("검사실적 데이터 삭제")
    
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('inspection_data').select('*').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            if len(df) > 0:
                # 삭제할 레코드 선택
                options = []
                for _, row in df.iterrows():
                    option = f"{row['inspection_date']} - {row['inspector_id']} - {row['result']}"
                    options.append(option)
                
                selected_option = st.selectbox("삭제할 데이터 선택", ["선택하세요"] + options)
                
                if selected_option != "선택하세요":
                    selected_index = options.index(selected_option)
                    selected_record = df.iloc[selected_index]
                    
                    # 선택된 레코드 정보 표시
                    st.subheader("삭제할 데이터 정보")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**검사일자:** {selected_record['inspection_date']}")
                        st.write(f"**검사원:** {selected_record['inspector_id']}")
                        st.write(f"**모델명:** {selected_record['model_id']}")
                    
                    with col2:
                        st.write(f"**검사결과:** {selected_record['result']}")
                        st.write(f"**검사수량:** {selected_record['quantity']}")
                        st.write(f"**비고:** {selected_record.get('notes', '없음')}")
                    
                    # 삭제 확인
                    st.warning("⚠️ 이 작업은 되돌릴 수 없습니다!")
                    
                    if st.button("데이터 삭제", type="secondary"):
                        try:
                            response = supabase.table('inspection_data').delete().eq('id', selected_record['id']).execute()
                            
                            if response.data:
                                st.success("데이터가 성공적으로 삭제되었습니다!")
                                st.rerun()
                            else:
                                st.error("데이터 삭제에 실패했습니다.")
                                
                        except Exception as e:
                            st.error(f"삭제 중 오류가 발생했습니다: {str(e)}")
            else:
                st.info("삭제할 데이터가 없습니다.")
        else:
            st.info("저장된 검사 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"데이터 조회 중 오류가 발생했습니다: {str(e)}")

def generate_sample_inspection_data():
    """샘플 검사 데이터 생성"""
    today = datetime.now().date()
    
    inspectors = ["김검사", "이검사", "박검사"]
    models = ["PA1", "PA2", "PA3", "B6", "B6M"]
    processes = ["IQC", "CNC1_PQC", "CNC2_PQC", "OQC", "CNC OQC"]
    
    data = []
    for i in range(20):
        inspection_date = today - timedelta(days=i % 10)
        inspector = random.choice(inspectors)
        model = random.choice(models)
        process = random.choice(processes)
        planned_qty = random.randint(80, 120)
        total_inspected = random.randint(70, planned_qty)
        defect_qty = random.randint(0, int(total_inspected * 0.1))
        
        data.append({
            "검사원": inspector,
            "검사일자": inspection_date,
            "검사원 ID": f"INSP-{str(inspectors.index(inspector) + 1).zfill(3)}",
            "LOT 번호": f"LOT-{str(i).zfill(4)}",
            "공정": process,
            "작업 시간(분)": random.randint(30, 90),
            "모델명": model,
            "계획 수량": planned_qty,
            "총 검사 수량": total_inspected,
            "불량 수량": defect_qty,
            "저장일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return data 