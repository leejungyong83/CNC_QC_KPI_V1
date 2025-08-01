﻿import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import io
from PIL import Image
import uuid
import pytz
from utils.inspector_utils import get_all_inspectors
from pages.item_management import get_all_models
from utils.supabase_client import get_supabase_client
from utils.defect_utils import get_defect_type_names
from utils.vietnam_timezone import get_database_time, get_database_time_iso, get_vietnam_display_time, get_vietnam_now
from utils.data_converter import convert_supabase_data_timezone, convert_dataframe_timezone
from utils.shift_manager import get_current_shift, get_shift_for_time, shift_manager
from utils.photo_manager import get_photo_manager, render_photo_upload_tab
# 번역 시스템 import
from utils.language_manager import t
import random

def show_inspection_input():
    """검사실적 관리 - 사용자 요청 필드에 맞춘 새로운 버전"""
    st.title(f"🔍 {t('검사실적 관리')}")
    
    # 탭 생성 - 사진 첨부 탭 추가
    tabs = st.tabs([
        f"📝 {t('실적 데이터 입력')}", 
        f"📷 {t('사진 첨부')}", 
        f"📊 {t('실적 데이터 조회')}", 
        f"✏️ {t('데이터 수정')}", 
        f"🗑️ {t('데이터 삭제')}"
    ])
    
    with tabs[0]:
        show_inspection_input_form()
    
    with tabs[1]:
        show_photo_attachment_tab()
    
    with tabs[2]:
        show_inspection_data_view()
    
    with tabs[3]:
        show_inspection_edit_form()
    
    with tabs[4]:
        show_inspection_delete_form()

def show_inspection_input_form():
    """검사실적 입력 폼 - 교대조 자동 판별 기능 추가"""
    st.header(f"📝 {t('검사실적 데이터 입력')}")
    
    # 🕐 현재 시간 및 교대조 정보 표시
    current_time = get_vietnam_now()
    current_shift = get_current_shift()
    
    # 시간 및 교대조 정보 표시 박스
    st.info(f"""
    **🕐 {t('현재 시간')}**: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ({t('베트남 시간')})
    
    **🏭 {t('현재 교대조')}**: {current_shift['full_shift_name']}
    - 📅 {t('작업일')}: {current_shift['work_date']}
    - 🏢 {t('교대조')}: {current_shift['shift_name']}
    """)
    
    # Supabase 연결
    try:
        supabase = get_supabase_client()
        
        # 검사자 목록 가져오기
        inspectors_result = supabase.table('inspectors').select('*').execute()
        inspectors = inspectors_result.data if inspectors_result.data else []
        
        # 생산모델 목록 가져오기
        models_result = supabase.table('production_models').select('*').execute()
        models = models_result.data if models_result.data else []
        
        # 불량유형 목록 가져오기
        defect_types = get_defect_type_names()
        
    except Exception as e:
        st.error(f"{t('데이터베이스 연결 오류')}: {str(e)}")
        return

    # 불량유형 선택 (폼 밖에서 처리)
    st.subheader(f"❌ {t('불량 정보 설정')}")
    
    # 불량 여부 확인
    has_defects = st.checkbox(f"{t('불량이 있습니까?')}", help=f"{t('불량이 발견된 경우 체크하세요')}")
    
    defect_data = {}
    total_defect_count = 0
    defect_description = ""
    
    if has_defects:
        if defect_types:
            # 개선된 불량유형 선택 UI
            st.write(f"**🎯 {t('불량유형 선택 및 수량 입력')}**")
            
            # 세션 상태에 선택된 불량유형들 저장
            if 'selected_defect_types' not in st.session_state:
                st.session_state.selected_defect_types = []
            
            # 불량유형 드롭다운 선택
            col1, col2 = st.columns([3, 1])
            with col1:
                available_types = [dt for dt in defect_types if dt not in st.session_state.selected_defect_types]
                if available_types:
                    new_defect_type = st.selectbox(
                        f"{t('불량유형을 선택하세요')}",
                        ["선택하세요"] + available_types,
                        key="new_defect_selector"
                    )
                else:
                    st.info(f"{t('모든 불량유형이 이미 선택되었습니다')}")
                    new_defect_type = "선택하세요"
            
            with col2:
                if st.button(f"➕ {t('추가')}", type="secondary", disabled=(new_defect_type == "선택하세요")):
                    if new_defect_type not in st.session_state.selected_defect_types:
                        st.session_state.selected_defect_types.append(new_defect_type)
                        st.rerun()
            
            # 선택된 불량유형들과 수량 입력
            if st.session_state.selected_defect_types:
                st.write(f"**📝 {t('선택된 불량유형별 수량 입력')}:**")
                
                # 각 선택된 불량유형에 대해 수량 입력 UI
                for defect_type in st.session_state.selected_defect_types:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"🔴 **{defect_type}**")
                    
                    with col2:
                        count = st.number_input(
                            f"{t('수량')}",
                            min_value=0,
                            value=0,
                            step=1,
                            key=f"defect_count_{defect_type}",
                            label_visibility="collapsed"
                        )
                        if count > 0:
                            defect_data[defect_type] = count
                            total_defect_count += count
                    
                    with col3:
                        if st.button(f"🗑️", key=f"remove_{defect_type}", help=f"{defect_type} {t('제거')}"):
                            st.session_state.selected_defect_types.remove(defect_type)
                            st.rerun()
                
                # 모든 선택 초기화 버튼
                if st.button(f"🔄 {t('모든 선택 초기화')}", type="secondary"):
                    st.session_state.selected_defect_types = []
                    st.rerun()
                
                # 불량 수량 요약
                if total_defect_count > 0:
                    st.success(f"📊 **{t('총 불량 수량')}: {total_defect_count}개**")
                    
                    # 선택된 불량유형별 수량 요약 표시
                    summary_text = " | ".join([f"{dtype}: {count}개" for dtype, count in defect_data.items()])
                    st.info(f"📋 {t('불량 상세')}: {summary_text}")
                    
                    # 불량 상세 설명
                    defect_description = st.text_area(
                        f"{t('불량 상세 설명')}",
                        placeholder=f"{t('불량 발생 원인이나 특이사항을 입력하세요 (선택사항)')}",
                        help=f"{t('불량에 대한 자세한 설명을 입력하세요')}"
                    )
                else:
                    st.warning(f"⚠️ {t('선택된 불량유형의 수량을 입력해주세요')}")
            else:
                st.info(f"💡 {t('위 드롭다운에서 불량유형을 선택하고 ➕ 추가 버튼을 클릭하세요')}")
        else:
            st.warning(f"{t('불량유형 데이터를 불러올 수 없습니다. 관리자에게 문의하세요.')}")

    # 입력 폼 (기본 정보만)
    with st.form(f"inspection_form", clear_on_submit=False):
        st.subheader(f"📋 {t('검사 기본 정보')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. 검사일자 (자동 계산된 작업일 표시)
            work_date = current_shift['work_date']
            st.date_input(
                f"📅 {t('작업일 (자동 계산')}", 
                value=work_date,
                disabled=True,
                help=f"{t('현재 시간')}({current_time.strftime('%H:%M')})을 기준으로 자동 계산된 작업일입니다"
            )
            
            # 2. 검사자 이름 (선택)
            inspector_options = ["검사자 선택"] + [f"{insp['name']}" for insp in inspectors]
            selected_inspector_name = st.selectbox(
                f"👤 {t('검사자 이름')}", 
                inspector_options,
                help=f"{t('검사를 담당한 검사자를 선택하세요')}"
            )
            
            # 3. 검사자 ID (자동 입력)
            inspector_id = ""
            selected_inspector = None
            if selected_inspector_name != "검사자 선택":
                selected_inspector = next((insp for insp in inspectors if insp['name'] == selected_inspector_name), None)
                inspector_id = selected_inspector['employee_id'] if selected_inspector else ""
            
            st.text_input(
                f"🆔 {t('검사자 ID')}", 
                value=inspector_id, 
                disabled=True,
                help=f"{t('검사자 선택 시 자동으로 입력됩니다')}"
            )
        
        with col2:
            # 4. 검사모델
            model_options = ["모델 선택"] + [f"{model['model_name']}" for model in models]
            selected_model_name = st.selectbox(
                f"🔧 {t('검사모델')}", 
                model_options,
                help=f"{t('검사할 제품의 모델을 선택하세요')}"
            )
            
            # 5. 검사공정
            process_options = [
                f"{t('공정 선택')}",
                "IQC", 
                "CNC1_PQC", 
                "CNC2_PQC", 
                "OQC", 
                "CNC OQC"
            ]
            selected_process = st.selectbox(
                f"⚙️ {t('검사공정')}", 
                process_options,
                help=f"{t('검사가 실시된 공정을 선택하세요')}"
            )
            
            # 추가 정보 (선택사항)
            total_inspected = st.number_input(
                f"📊 {t('총 검사 수량')}", 
                min_value=0, 
                value=100, 
                step=1,
                help=f"{t('검사한 총 제품 수량을 입력하세요')}"
            )
        
        # 비고
        notes = st.text_area(
            f"📄 {t('비고')}", 
            placeholder=f"{t('기타 특이사항이나 참고사항을 입력하세요')}",
            help=f"{t('검사와 관련된 추가 정보를 입력하세요')}"
        )
        
        # 제출 버튼
        submitted = st.form_submit_button(f"✅ {t('검사실적 저장')}", type="primary")
        
        if submitted:
            # 입력값 검증
            errors = []
            
            if selected_inspector_name == "검사자 선택":
                errors.append(f"{t('검사자를 선택하세요')}")
            
            if selected_model_name == "모델 선택":
                errors.append(f"{t('검사모델을 선택하세요')}")
            
            if selected_process == f"{t('공정 선택')}:":
                errors.append(f"{t('검사공정을 선택하세요')}")
            
            if has_defects and total_defect_count == 0:
                errors.append(f"{t('불량이 있다고 체크했지만 불량 수량이 입력되지 않았습니다')}")
            
            if total_inspected == 0:
                errors.append(f"{t('총 검사 수량을 입력하세요')}")
            
            if total_defect_count > total_inspected:
                errors.append(f"{t('불량 수량이 총 검사 수량보다 클 수 없습니다')}")
            
            # 오류가 있으면 표시
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
                return
            
            # 데이터 저장
            try:
                # 검사 결과 판정
                result = "불합격" if total_defect_count > 0 else "합격"
                
                # 모델 ID 가져오기
                selected_model = next((model for model in models if model['model_name'] == selected_model_name), None)
                model_id = selected_model['id'] if selected_model else None
                
                # 검사자 ID 가져오기 (UUID)
                inspector_uuid = selected_inspector['id'] if selected_inspector else None
                
                # 교대조 정보 자동 판별
                save_time = get_vietnam_now()
                shift_info = get_shift_for_time(save_time)
                
                # 검사 데이터 저장 (베트남 시간대로)
                inspection_data = {
                    "inspection_date": shift_info['work_date'].strftime('%Y-%m-%d'),  # 작업일 기준
                    "inspector_id": inspector_uuid,
                    "model_id": model_id,
                    "process": selected_process,
                    "quantity": total_inspected,  # quantity 필드 추가 (기존 테이블 호환성)
                    "total_inspected": total_inspected,
                    "defect_quantity": total_defect_count,
                    "result": result,
                    "shift": shift_info['shift_name'],  # 교대조 정보 자동 추가
                    "notes": notes if notes else None,
                    "created_at": get_database_time_iso()  # 베트남 시간대로 저장 (UTC+7)
                    # updated_at은 데이터베이스 기본값(now()) 사용
                }
                
                # Supabase에 검사 데이터 저장
                inspection_result = supabase.table('inspection_data').insert(inspection_data).execute()
                
                if inspection_result.data:
                    inspection_id = inspection_result.data[0]['id']
                    st.success(f"✅ {t('검사실적이 성공적으로 저장되었습니다!')} (ID: {inspection_id})")
                    
                    # 불량 데이터가 있으면 저장
                    if defect_data:
                        defect_save_count = 0
                        for defect_type, count in defect_data.items():
                            defect_record = {
                                "inspection_id": inspection_id,
                                "defect_type": defect_type,  # 기존 테이블 구조에 맞춘 필드명
                                "defect_count": count,
                                "description": defect_description if defect_description else None,  # 기존 테이블 구조에 맞춘 필드명
                                "created_at": get_database_time_iso()  # 베트남 시간대로 저장 (UTC+7)
                            }
                            
                            defect_result = supabase.table('defects').insert(defect_record).execute()
                            if defect_result.data:
                                defect_save_count += 1
                        
                        st.success(f"✅ {defect_save_count}개의 {t('불량 정보가 저장되었습니다!')}")
                    
                    # 저장 완료 후 세션 상태 초기화
                    if 'selected_defect_types' in st.session_state:
                        st.session_state.selected_defect_types = []
                    
                    # 저장된 데이터 요약 표시
                    with st.expander(f"📊 {t('저장된 데이터 요약')}"):
                        summary_data = {
                            f"{t('작업일')}:": shift_info['work_date'].strftime("%Y-%m-%d"),
                            f"{t('교대조')}:": shift_info['shift_name'],
                            f"{t('입력시간')}:": save_time.strftime("%Y-%m-%d %H:%M:%S"),
                            f"{t('검사자')}:": selected_inspector_name,
                            f"{t('검사자 ID')}:": inspector_id,
                            f"{t('검사모델')}:": selected_model_name,
                            f"{t('검사공정')}:": selected_process,
                            f"{t('총 검사수량')}:": total_inspected,
                            f"{t('불량수량')}:": total_defect_count,
                            f"{t('검사결과')}:": result
                        }
                        
                        for key, value in summary_data.items():
                            st.write(f"**{key}:** {value}")
                        
                        if defect_data:
                            st.write(f"**{t('불량유형별 수량')}:**")
                            for defect_type, count in defect_data.items():
                                st.write(f"  - {defect_type}: {count}개")
                
                else:
                    st.error(f"❌ {t('검사실적 저장에 실패했습니다')}")
                
            except Exception as e:
                st.error(f"❌ {t('저장 중 오류가 발생했습니다')}: {str(e)}")

def show_inspection_data_view():
    """검사실적 조회 화면"""
    st.header(f"📊 {t('검사실적 데이터 조회')}")
    
    try:
        supabase = get_supabase_client()
        
        # 검색 필터
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input(f"{t('시작일')}", value=date.today())
        with col2:
            end_date = st.date_input(f"{t('종료일')}", value=date.today())
        with col3:
            search_limit = st.selectbox(f"{t('조회 건수')}", [10, 20, 50, 100], index=1)
        
        if st.button(f"🔍 {t('조회')}", type="primary"):
            # 검사 데이터 조회 (단순 조회)
            query = supabase.table('inspection_data') \
                .select('*') \
                .gte('inspection_date', start_date.isoformat()) \
                .lte('inspection_date', end_date.isoformat()) \
                .order('inspection_date', desc=True) \
                .limit(search_limit)
            
            result = query.execute()
            
            # 검사자 및 모델 데이터 별도 조회
            inspectors_result = supabase.table('inspectors').select('*').execute()
            inspectors = {insp['id']: insp for insp in inspectors_result.data} if inspectors_result.data else {}
            
            models_result = supabase.table('production_models').select('*').execute()
            models = {model['id']: model for model in models_result.data} if models_result.data else {}
            
            if result.data:
                # 시간대 변환
                converted_data = convert_supabase_data_timezone(result.data)
                
                # 데이터프레임 생성
                df_data = []
                for row in converted_data:
                    inspector = inspectors.get(row.get('inspector_id'), {})
                    model = models.get(row.get('model_id'), {})
                    
                    inspector_name = inspector.get('name', '알 수 없음')
                    inspector_id = inspector.get('employee_id', '알 수 없음')
                    model_name = model.get('model_name', '알 수 없음')
                    
                    df_data.append({
                        f"{t('검사일자')}:": row['inspection_date'],
                        f"{t('검사자 이름')}:": inspector_name,
                        f"{t('검사자 ID')}:": inspector_id,
                        f"{t('검사모델')}:": model_name,
                        f"{t('검사공정')}:": row.get('process', ''),
                        f"{t('총 검사수량')}:": row.get('total_inspected', row.get('quantity', 0)),
                        f"{t('불량수량')}:": row.get('defect_quantity', 0),
                        f"{t('검사결과')}:": row['result'],
                        f"{t('비고')}:": row.get('notes', '')
                    })
                
                df = pd.DataFrame(df_data)
                
                # 결과 표시
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.success(f"✅ {len(df)}건의 {t('검사실적을 조회했습니다')}")
                
                # 통계 정보
                if len(df) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(f"{t('총 검사건수')}", len(df))
                    with col2:
                        pass_count = len(df[df[f"{t('검사결과')}"] == '합격'])
                        st.metric(f"{t('합격 건수')}", pass_count)
                    with col3:
                        fail_count = len(df[df[f"{t('검사결과')}"] == '불합격'])
                        st.metric(f"{t('불합격 건수')}", fail_count)
                    with col4:
                        pass_rate = (pass_count / len(df) * 100) if len(df) > 0 else 0
                        st.metric(f"{t('합격률')}", f"{pass_rate:.1f}%")
            
            else:
                st.info(f"📝 {t('해당 기간에 검사실적이 없습니다')}")
    
    except Exception as e:
        st.error(f"❌ {t('데이터 조회 중 오류')}: {str(e)}")
            
def generate_sample_inspection_data():
    """샘플 검사 데이터 생성"""
    today = get_vietnam_now().date()
    
    # 검사자 목록 (임시)
    inspectors = ["김검사", "이검사", "박검사"]
    
    # 모델 목록 (임시)
    models = ["PA1", "PA2", "PA3", "B6", "B6M"]
    
    # 공정 목록 (임시)
    processes = ["IQC", "CNC1_PQC", "CNC2_PQC", "OQC", "CNC OQC"]
    
    # 샘플 데이터 생성
    data = []
    for i in range(20):  # 20개의 샘플 데이터 생성
        inspection_date = today - timedelta(days=i % 10)  # 최근 10일간 분포
        inspector = random.choice(inspectors)
        model = random.choice(models)
        process = random.choice(processes)
        planned_qty = random.randint(80, 120)
        total_inspected = random.randint(70, planned_qty)
        defect_qty = random.randint(0, int(total_inspected * 0.1))  # 0~10% 불량
        
        data.append({
            f"{t('검사원')}:": inspector,
            f"{t('검사일자')}:": inspection_date,
            f"{t('검사원 ID')}:": f"INSP-{str(inspectors.index(inspector) + 1).zfill(3)}",
            f"{t('LOT 번호')}:": f"LOT-{str(i).zfill(4)}",
            f"{t('공정')}:": process,
            f"{t('작업 시간(분)')}:": random.randint(30, 90),
            f"{t('모델명')}:": model,
            f"{t('계획 수량')}:": planned_qty,
            f"{t('총 검사 수량')}:": total_inspected,
            f"{t('불량 수량')}:": defect_qty,
            f"{t('저장일시')}:": get_vietnam_display_time()
        })
    
    return data

def show_inspection_edit_form():
    """검사실적 수정 화면"""
    st.header(f"✏️ {t('검사실적 데이터 수정')}")
    
    try:
        supabase = get_supabase_client()
        
        # 수정할 데이터 검색
        st.subheader(f"🔍 {t('수정할 데이터 검색')}")
        
        col1, col2 = st.columns(2)
        with col1:
            search_date = st.date_input(f"{t('검사일자로 검색')}", value=date.today())
        with col2:
            if st.button(f"🔍 {t('검색')}", type="secondary"):
                st.session_state.search_performed = True
        
        if hasattr(st.session_state, 'search_performed') and st.session_state.search_performed:
            # 해당 날짜의 데이터 조회
            result = supabase.table('inspection_data') \
                .select('*') \
                .eq('inspection_date', search_date.isoformat()) \
                .order('created_at', desc=True) \
                .execute()
            
            if result.data:
                # 검사자 및 모델 데이터 조회
                inspectors_result = supabase.table('inspectors').select('*').execute()
                inspectors = {insp['id']: insp for insp in inspectors_result.data} if inspectors_result.data else {}
                
                models_result = supabase.table('production_models').select('*').execute()
                models = {model['id']: model for model in models_result.data} if models_result.data else {}
                
                # 수정할 데이터 선택
                st.subheader(f"📝 {t('수정할 데이터 선택')}")
                
                selection_data = []
                for i, row in enumerate(result.data):
                    inspector = inspectors.get(row.get('inspector_id'), {})
                    model = models.get(row.get('model_id'), {})
                    
                    inspector_name = inspector.get('name', '알 수 없음')
                    model_name = model.get('model_name', '알 수 없음')
                    
                    selection_data.append(f"{t('ID')}: {row['id'][:8]}... | {inspector_name} | {model_name} | {row.get('process', '')} | {t('수량')}: {row.get('total_inspected', 0)}")
                
                selected_index = st.selectbox(
                    f"{t('수정할 검사실적을 선택하세요')}",
                    range(len(selection_data)),
                    format_func=lambda x: selection_data[x]
                )
                
                selected_record = result.data[selected_index]
                
                # 수정 폼
                st.subheader(f"✏️ {t('데이터 수정')}")
                
                with st.form(f"edit_form"):
                    col1, col2 = st.columns(2)
    
                    with col1:
                        # 검사일자
                        edit_date = st.date_input(
                            f"📅 {t('검사일자')}",
                            value=datetime.strptime(selected_record['inspection_date'], '%Y-%m-%d').date()
                        )
                        
                        # 검사자 선택
                        inspector_options = [f"{insp['name']}" for insp in inspectors.values()]
                        current_inspector = inspectors.get(selected_record.get('inspector_id'), {})
                        current_inspector_name = current_inspector.get('name', '')
                        
                        try:
                            current_inspector_index = inspector_options.index(current_inspector_name)
                        except ValueError:
                            current_inspector_index = 0
                        
                        selected_inspector_name = st.selectbox(
                            f"👤 {t('검사자 이름')}",
                            inspector_options,
                            index=current_inspector_index
                        )
                        
                        # 검사공정
                        process_options = ["IQC", "CNC1_PQC", "CNC2_PQC", "OQC", "CNC OQC"]
                        current_process = selected_record.get('process', 'IQC')
                        try:
                            current_process_index = process_options.index(current_process)
                        except ValueError:
                            current_process_index = 0
                        
                        selected_process = st.selectbox(
                            f"⚙️ {t('검사공정')}",
                            process_options,
                            index=current_process_index
                        )
                    
                    with col2:
                        # 검사모델
                        model_options = [f"{model['model_name']}" for model in models.values()]
                        current_model = models.get(selected_record.get('model_id'), {})
                        current_model_name = current_model.get('model_name', '')
                        
                        try:
                            current_model_index = model_options.index(current_model_name)
                        except ValueError:
                            current_model_index = 0
                        
                        selected_model_name = st.selectbox(
                            f"🔧 {t('검사모델')}",
                            model_options,
                            index=current_model_index
                        )
                        
                        # 총 검사수량
                        total_inspected = st.number_input(
                            f"📊 {t('총 검사 수량')}",
                            min_value=0,
                            value=int(selected_record.get('total_inspected', 0)),
                            step=1
                        )
                        
                        # 불량수량
                        defect_quantity = st.number_input(
                            f"❌ {t('불량 수량')}",
                            min_value=0,
                            value=int(selected_record.get('defect_quantity', 0)),
                            step=1
                        )
                    
                    # 비고
                    notes = st.text_area(
                        f"📄 {t('비고')}",
                        value=selected_record.get('notes', '') or '',
                        placeholder=f"{t('기타 특이사항이나 참고사항을 입력하세요')}"
                    )
                    
                    # 수정 버튼
                    if st.form_submit_button(f"✅ {t('수정 완료')}", type="primary"):
                        try:
                            # 검사자 ID 찾기
                            selected_inspector = next((insp for insp in inspectors.values() if insp['name'] == selected_inspector_name), None)
                            inspector_uuid = selected_inspector['id'] if selected_inspector else None
                            
                            # 모델 ID 찾기
                            selected_model = next((model for model in models.values() if model['model_name'] == selected_model_name), None)
                            model_id = selected_model['id'] if selected_model else None
                            
                            # 검사 결과 판정
                            result_status = "불합격" if defect_quantity > 0 else "합격"
                            
                            # 수정 데이터
                            update_data = {
                                "inspection_date": edit_date.isoformat(),
                                "inspector_id": inspector_uuid,
                                "model_id": model_id,
                                "process": selected_process,
                                "quantity": total_inspected,
                                "total_inspected": total_inspected,
                                "defect_quantity": defect_quantity,
                                "result": result_status,
                                "notes": notes if notes else None
                            }
                            
                            # 데이터 업데이트
                            update_result = supabase.table('inspection_data') \
                                .update(update_data) \
                                .eq('id', selected_record['id']) \
                                .execute()
                            
                            if update_result.data:
                                st.success(f"✅ {t('검사실적이 성공적으로 수정되었습니다!')}")
                                st.session_state.search_performed = False  # 검색 상태 초기화
                                st.rerun()
                            else:
                                st.error(f"❌ {t('수정에 실패했습니다')}")
                        
                        except Exception as e:
                            st.error(f"❌ {t('수정 중 오류가 발생했습니다')}: {str(e)}")
            
            else:
                st.info(f"📝 {t('해당 날짜에 검사실적이 없습니다')}")
    
    except Exception as e:
        st.error(f"❌ {t('오류가 발생했습니다')}: {str(e)}")

def show_inspection_delete_form():
    """검사실적 삭제 화면"""
    st.header(f"🗑️ {t('검사실적 데이터 삭제')}")
    
    st.warning(f"⚠️ **{t('주의')}:** {t('삭제된 데이터는 복구할 수 없습니다!')}")
    
    try:
        supabase = get_supabase_client()
        
        # 삭제할 데이터 검색
        st.subheader(f"🔍 {t('삭제할 데이터 검색')}")
        
        # 검색 조건 입력
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            start_date = st.date_input(
                f"📅 {t('검색 시작일')}", 
                value=date.today() - timedelta(days=7),
                key="delete_start_date",
                help=f"{t('검색할 기간의 시작 날짜를 선택하세요')}"
            )
        with col2:
            end_date = st.date_input(
                f"📅 {t('검색 종료일')}", 
                value=date.today(),
                key="delete_end_date",
                help=f"{t('검색할 기간의 종료 날짜를 선택하세요')}"
            )
        with col3:
            st.write("")  # 버튼 정렬을 위한 공간
            if st.button(f"🔍 {t('검색')}", type="primary", key="delete_search"):
                if start_date <= end_date:
                    st.session_state.delete_search_performed = True
                    st.session_state.delete_start_date = start_date
                    st.session_state.delete_end_date = end_date
                else:
                    st.error(f"❌ {t('시작일이 종료일보다 늦을 수 없습니다!')}")
        
        # 검색 조건 표시
        if hasattr(st.session_state, 'delete_search_performed') and st.session_state.delete_search_performed:
            search_start = st.session_state.delete_start_date
            search_end = st.session_state.delete_end_date
            
            st.info(f"📅 {t('검색 기간')}: {search_start} ~ {search_end}")
            
            # 해당 기간의 데이터 조회
            result = supabase.table('inspection_data') \
                .select('*') \
                .gte('inspection_date', search_start.isoformat()) \
                .lte('inspection_date', search_end.isoformat()) \
                .order('inspection_date', desc=True) \
                .order('created_at', desc=True) \
                .execute()
            
            if result.data:
                # 검사자 및 모델 데이터 조회
                inspectors_result = supabase.table('inspectors').select('*').execute()
                inspectors = {insp['id']: insp for insp in inspectors_result.data} if inspectors_result.data else {}
                
                models_result = supabase.table('production_models').select('*').execute()
                models = {model['id']: model for model in models_result.data} if models_result.data else {}
                
                # 검색 결과 요약
                total_records = len(result.data)
                st.success(f"📊 **{t('검색 결과')}: {total_records}건의 {t('검사실적이 발견되었습니다')}**")
                
                # 삭제할 데이터 선택
                st.subheader(f"🗑️ {t('삭제할 데이터 선택')}")
                st.warning(f"⚠️ {t('각 항목의 삭제 버튼을 클릭한 후 확인 체크박스를 선택하면 삭제됩니다')}")
                
                for i, row in enumerate(result.data, 1):
                    inspector = inspectors.get(row.get('inspector_id'), {})
                    model = models.get(row.get('model_id'), {})
                    
                    inspector_name = inspector.get('name', '알 수 없음')
                    model_name = model.get('model_name', '알 수 없음')
                    
                    # 검사 결과에 따른 아이콘
                    result_icon = "✅" if row['result'] == "합격" else "❌"
                    
                    with st.expander(f"{i}. 📋 [{row['inspection_date']}] {inspector_name} | {model_name} | {row.get('process', '')} | {t('검사수량')}: {row.get('total_inspected', 0)} {result_icon}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # 기본 정보
                            info_col1, info_col2 = st.columns(2)
                            
                            with info_col1:
                                st.write(f"**📅 {t('검사일자')}:** {row['inspection_date']}")
                                st.write(f"**👤 {t('검사자')}:** {inspector_name}")
                                st.write(f"**🔧 {t('검사모델')}:** {model_name}")
                                st.write(f"**⚙️ {t('검사공정')}:** {row.get('process', '')}")
                            
                            with info_col2:
                                st.write(f"**📊 {t('총 검사수량')}:** {row.get('total_inspected', 0)}")
                                st.write(f"**❌ {t('불량수량')}:** {row.get('defect_quantity', 0)}")
                                st.write(f"**📋 {t('검사결과')}:** {result_icon} {row['result']}")
                                
                                # 불량률 계산
                                total_qty = row.get('total_inspected', 0)
                                defect_qty = row.get('defect_quantity', 0)
                                if total_qty > 0:
                                    defect_rate = (defect_qty / total_qty) * 100
                                    st.write(f"**📈 {t('불량률')}:** {defect_rate:.2f}%")
                            
                            if row.get('notes'):
                                st.write(f"**📝 {t('비고')}:** {row['notes']}")
                        
                        with col2:
                            st.write(f"**🗑️ {t('삭제 작업')}**")
                            
                            # 삭제 버튼을 먼저 표시
                            delete_clicked = st.button(
                                f"🗑️ {t('삭제')}", 
                                key=f"delete_{row['id']}", 
                                type="secondary",
                                use_container_width=True
                            )
                            
                            # 삭제 버튼이 클릭되면 확인 체크박스 표시
                            if delete_clicked or f"delete_clicked_{row['id']}" in st.session_state:
                                st.session_state[f"delete_clicked_{row['id']}"] = True
                                
                                st.error(f"⚠️ **{t('삭제 확인')}**")
                                confirm_delete = st.checkbox(
                                    f"{t('정말 삭제하시겠습니까?')}", 
                                    key=f"confirm_{row['id']}",
                                    help=f"{t('이 작업은 되돌릴 수 없습니다!')}"
                                )
                                
                                if confirm_delete:
                                    if st.button(f"✅ {t('최종 삭제')}", key=f"final_delete_{row['id']}", type="primary"):
                                        try:
                                            # 관련 불량 데이터 먼저 삭제
                                            defects_result = supabase.table('defects') \
                                                .delete() \
                                                .eq('inspection_id', row['id']) \
                                                .execute()
                                            
                                            # 검사 데이터 삭제
                                            delete_result = supabase.table('inspection_data') \
                                                .delete() \
                                                .eq('id', row['id']) \
                                                .execute()
                                            
                                            if delete_result:
                                                st.success(f"✅ {t('데이터가 성공적으로 삭제되었습니다!')}")
                                                # 세션 상태 초기화
                                                if f"delete_clicked_{row['id']}" in st.session_state:
                                                    del st.session_state[f"delete_clicked_{row['id']}"]
                                                st.session_state.delete_search_performed = False
                                                st.rerun()
                                            else:
                                                st.error(f"❌ {t('삭제에 실패했습니다')}")
                                        
                                        except Exception as e:
                                            st.error(f"❌ {t('삭제 중 오류가 발생했습니다')}: {str(e)}")
                                
                                # 취소 버튼
                                if st.button(f"❌ {t('취소')}", key=f"cancel_{row['id']}"):
                                    if f"delete_clicked_{row['id']}" in st.session_state:
                                        del st.session_state[f"delete_clicked_{row['id']}"]
                                    st.rerun()
            
            else:
                st.info(f"📝 {search_start} ~ {search_end} {t('기간에 검사실적이 없습니다')}")
    
    except Exception as e:
        st.error(f"❌ {t('오류가 발생했습니다')}: {str(e)}")

def show_photo_attachment_tab():
    """사진 첨부 탭 - 검사 데이터와 연동"""
    st.header(f"📷 {t('검사 사진 첨부')}")
    
    try:
        supabase = get_supabase_client()
        
        # 검사 데이터 목록 조회 (최근 30일)
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        inspection_result = supabase.table('inspection_data')\
            .select('*, inspectors(name), production_models(model_name)')\
            .gte('inspection_date', thirty_days_ago)\
            .order('created_at', desc=True)\
            .limit(50)\
            .execute()
        
        if not inspection_result.data:
            st.info(f"📋 {t('최근 30일간 검사 데이터가 없습니다')}.")
            return
        
        # 검사 데이터 목록 표시
        st.subheader(f"🔍 {t('검사 데이터 선택')}")
        
        inspection_options = []
        for item in inspection_result.data:
            inspector_name = item.get('inspectors', {}).get('name', 'Unknown') if item.get('inspectors') else 'Unknown'
            model_name = item.get('production_models', {}).get('model_name', 'Unknown') if item.get('production_models') else 'Unknown'
            
            option_text = f"{item['inspection_date']} | {inspector_name} | {model_name} | {item.get('result', 'N/A')}"
            inspection_options.append((option_text, item['id']))
        
        if not inspection_options:
            st.info(f"📋 {t('사용 가능한 검사 데이터가 없습니다')}.")
            return
        
        # 검사 데이터 선택
        selected_option = st.selectbox(
            f"{t('사진을 첨부할 검사 데이터를 선택하세요')}:",
            options=[opt[0] for opt in inspection_options],
            help=f"{t('날짜 | 검사자 | 모델 | 결과 순으로 표시됩니다')}"
        )
        
        if selected_option:
            selected_inspection_id = next(opt[1] for opt in inspection_options if opt[0] == selected_option)
            
            # 선택된 검사 데이터 상세 정보
            selected_inspection = next(item for item in inspection_result.data if item['id'] == selected_inspection_id)
            
            with st.expander(f"📋 {t('선택된 검사 데이터 상세 정보')}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**📅 {t('검사일')}:** {selected_inspection['inspection_date']}")
                    st.write(f"**👤 {t('검사자')}:** {selected_inspection.get('inspectors', {}).get('name', 'Unknown') if selected_inspection.get('inspectors') else 'Unknown'}")
                    st.write(f"**🔧 {t('모델')}:** {selected_inspection.get('production_models', {}).get('model_name', 'Unknown') if selected_inspection.get('production_models') else 'Unknown'}")
                with col2:
                    st.write(f"**✅ {t('결과')}:** {selected_inspection.get('result', 'N/A')}")
                    st.write(f"**📊 {t('검사수량')}:** {selected_inspection.get('total_inspected', 'N/A')}")
                    st.write(f"**❌ {t('불량수량')}:** {selected_inspection.get('defect_quantity', 'N/A')}")
                
                if selected_inspection.get('notes'):
                    st.write(f"**📝 {t('비고')}:** {selected_inspection['notes']}")
            
            st.divider()
            
            # 사진 첨부 기능 - 새로운 PhotoManager 사용
            current_user = st.session_state.get('user_name', 'Unknown User')
            render_photo_upload_tab(selected_inspection_id, current_user)
    
    except Exception as e:
        st.error(f"❌ {t('사진 첨부 기능 오류')}: {str(e)}")
        st.error(f"📝 {t('상세 오류')}: {str(e)}")
        
        # 오프라인 모드로 사진 첨부 기능 제공
        st.warning(f"⚠️ {t('데이터베이스 연결 오류로 인해 오프라인 모드로 전환합니다')}.")
        
        # 더미 검사 ID로 사진 첨부 기능 테스트
        dummy_inspection_id = "test-inspection-" + datetime.now().strftime('%Y%m%d-%H%M%S')
        current_user = st.session_state.get('user_name', 'Test User')
        
        st.info(f"🧪 {t('테스트 모드')}: {dummy_inspection_id}")
        render_photo_upload_tab(dummy_inspection_id, current_user)

def get_inspection_items(model):
    """모델별 검사항목 반환"""
    # 실제 구현에서는 데이터베이스에서 가져와야 함
    default_items = [
        f"{t('외관 검사')}",
        f"{t('치수 측정')}", 
        f"{t('기능 테스트')}",
        f"{t('표면 거칠기')}",
        f"{t('조립 상태')}"
    ]
    return default_items 
