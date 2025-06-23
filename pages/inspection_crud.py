import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
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
    st.title("🔍 검사실적 관리")
    
    # 세션 상태에 검사 데이터 초기화
    if "inspection_data" not in st.session_state:
        st.session_state.inspection_data = []
    
    # 탭 생성 - CRUD 형태
    tabs = st.tabs(["📊 데이터 조회", "➕ 데이터 입력", "✏️ 데이터 수정", "🗑️ 데이터 삭제"])
    
    with tabs[0]:
        show_data_search()
    
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
        st.warning(f"검사자 데이터 로드 실패: {str(e)}")
        return []

def get_supabase_models():
    """Supabase에서 생산 모델 목록을 가져옵니다."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('production_models').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        st.warning(f"모델 데이터 로드 실패: {str(e)}")
        return []

def show_data_search():
    """검사 데이터 검색 및 표시"""
    st.header("검사실적 데이터 검색")
    
    # 검색 조건
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("시작일", value=date.today() - timedelta(days=7))
        end_date = st.date_input("종료일", value=date.today())
    
    with col2:
        # 모델 선택
        models = get_supabase_models()
        model_options = ["전체"] + [model['model_name'] for model in models]
        selected_model = st.selectbox("모델 선택", model_options)
        
        # 검사원 선택
        inspectors = get_supabase_inspectors()
        inspector_options = ["전체"] + [inspector['name'] for inspector in inspectors]
        selected_inspector = st.selectbox("검사원 선택", inspector_options)
    
    # LOT 번호 검색
    search_lot = st.text_input("LOT 번호 검색 (부분 검색 가능)")
    
    if st.button("🔍 검색", type="primary"):
        search_inspection_data(start_date, end_date, selected_model, selected_inspector, search_lot)

def search_inspection_data(start_date, end_date, selected_model, selected_inspector, search_lot):
    """검사 데이터 검색 실행"""
    try:
        supabase = get_supabase_client()
        response = supabase.table('inspection_data').select('*').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # 날짜 필터링
            df['inspection_date'] = pd.to_datetime(df['inspection_date'])
            start_datetime = pd.to_datetime(start_date)
            end_datetime = pd.to_datetime(end_date)
            df = df[(df['inspection_date'] >= start_datetime) & (df['inspection_date'] <= end_datetime)]
            
            # 모델 필터링
            if selected_model != "전체":
                df = df[df['model_id'].str.contains(selected_model, case=False, na=False)]
            
            # 검사원 필터링
            if selected_inspector != "전체":
                df = df[df['inspector_id'].str.contains(selected_inspector, case=False, na=False)]
            
            # LOT 번호 필터링
            if search_lot:
                df = df[df['lot_number'].str.contains(search_lot, case=False, na=False)]
            
            if len(df) > 0:
                # 날짜 형식 변환
                df['inspection_date'] = df['inspection_date'].dt.strftime("%Y-%m-%d")
                
                # 표시할 컬럼 선택
                display_columns = ['inspection_date', 'inspector_id', 'lot_number', 'model_id', 'result']
                available_columns = [col for col in display_columns if col in df.columns]
                
                st.dataframe(df[available_columns], use_container_width=True, hide_index=True)
                st.success(f"총 {len(df)}건의 검사 데이터가 검색되었습니다.")
            else:
                st.info("검색 조건에 맞는 데이터가 없습니다.")
        else:
            st.info("저장된 검사 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"데이터 검색 중 오류 발생: {str(e)}")

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
        try:
            inspectors = get_all_inspectors()
            # status 필터링 제거하고 모든 검사자 사용
            inspector_options = ["검사원 선택"] + [f"{insp['name']} ({insp['id']})" for insp in inspectors]
        except Exception as e:
            st.warning(f"검사자 데이터 로드 실패: {str(e)}")
            inspector_options = ["검사원 선택"]
    
    with st.form("inspection_input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            inspection_date = st.date_input("검사일자", value=date.today())
            inspector_id = st.text_input("검사원 ID", placeholder="검사원 ID를 입력하세요")
            lot_number = st.text_input("LOT 번호", placeholder="LOT 번호를 입력하세요")
        
        with col2:
            model_id = st.text_input("모델 ID", placeholder="모델 ID를 입력하세요")
            result = st.selectbox("검사 결과", ["선택하세요", "합격", "불합격", "재검사"])
            notes = st.text_area("비고", placeholder="특이사항이 있으면 입력하세요")
        
        submitted = st.form_submit_button("저장", type="primary")
        
        if submitted:
            if not inspector_id or not lot_number or not model_id or result == "선택하세요":
                st.error("모든 필수 항목을 입력해주세요.")
            else:
                try:
                    inspection_data = {
                        "inspection_date": inspection_date.isoformat(),
                        "inspector_id": inspector_id,
                        "lot_number": lot_number,
                        "model_id": model_id,
                        "result": result,
                        "notes": notes if notes else None,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    supabase = get_supabase_client()
                    response = supabase.table('inspection_data').insert(inspection_data).execute()
                    
                    if response.data:
                        st.success("✅ 검사 데이터가 성공적으로 저장되었습니다!")
                        st.rerun()
                    else:
                        st.error("데이터 저장에 실패했습니다.")
                        
                except Exception as e:
                    st.error(f"데이터 저장 중 오류 발생: {str(e)}")

def show_data_edit_form():
    """검사 데이터 수정 폼"""
    st.header("검사실적 데이터 수정")
    
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('inspection_data').select('*').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            if len(df) > 0:
                # 수정할 레코드 선택
                options = []
                for _, row in df.iterrows():
                    option = f"{row['inspection_date']} - {row['inspector_id']} - {row['result']}"
                    options.append(option)
                
                selected_option = st.selectbox("수정할 데이터 선택", ["선택하세요"] + options)
                
                if selected_option != "선택하세요":
                    selected_index = options.index(selected_option)
                    selected_record = df.iloc[selected_index]
                    
                    with st.form("edit_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_inspector = st.text_input("검사원 ID", value=selected_record['inspector_id'])
                            new_date = st.date_input("검사일자", value=pd.to_datetime(selected_record['inspection_date']).date())
                            new_lot = st.text_input("LOT 번호", value=selected_record['lot_number'])
                        
                        with col2:
                            new_model = st.text_input("모델 ID", value=selected_record['model_id'])
                            new_result = st.selectbox("검사 결과", ["합격", "불합격", "재검사"], 
                                                    index=["합격", "불합격", "재검사"].index(selected_record['result']) if selected_record['result'] in ["합격", "불합격", "재검사"] else 0)
                            new_notes = st.text_area("비고", value=selected_record['notes'] if selected_record['notes'] else "")
                        
                        if st.form_submit_button("수정", type="primary"):
                            try:
                                updated_data = {
                                    "inspection_date": new_date.isoformat(),
                                    "inspector_id": new_inspector,
                                    "lot_number": new_lot,
                                    "model_id": new_model,
                                    "result": new_result,
                                    "notes": new_notes if new_notes else None,
                                    "updated_at": datetime.now().isoformat()
                                }
                                
                                response = supabase.table('inspection_data').update(updated_data).eq('id', selected_record['id']).execute()
                                
                                if response.data:
                                    st.success("✅ 데이터가 성공적으로 수정되었습니다!")
                                    st.rerun()
                                else:
                                    st.error("데이터 수정에 실패했습니다.")
                                    
                            except Exception as e:
                                st.error(f"데이터 수정 중 오류 발생: {str(e)}")
            else:
                st.info("수정할 데이터가 없습니다.")
        else:
            st.info("저장된 검사 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {str(e)}")

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
                    st.warning("⚠️ 다음 데이터를 삭제하시겠습니까?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**검사일자**: {selected_record['inspection_date']}")
                        st.write(f"**검사원**: {selected_record['inspector_id']}")
                        st.write(f"**LOT 번호**: {selected_record['lot_number']}")
                    
                    with col2:
                        st.write(f"**모델**: {selected_record['model_id']}")
                        st.write(f"**결과**: {selected_record['result']}")
                        st.write(f"**비고**: {selected_record['notes'] if selected_record['notes'] else '없음'}")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        if st.button("🗑️ 삭제 확인", type="primary"):
                            try:
                                response = supabase.table('inspection_data').delete().eq('id', selected_record['id']).execute()
                                
                                if response.data:
                                    st.success("✅ 데이터가 성공적으로 삭제되었습니다!")
                                    st.rerun()
                                else:
                                    st.error("데이터 삭제에 실패했습니다.")
                                    
                            except Exception as e:
                                st.error(f"데이터 삭제 중 오류 발생: {str(e)}")
                    
                    with col2:
                        if st.button("❌ 취소"):
                            st.rerun()
            else:
                st.info("삭제할 데이터가 없습니다.")
        else:
            st.info("저장된 검사 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {str(e)}")

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