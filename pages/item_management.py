import streamlit as st
import pandas as pd

def show_production_model_management():
    """생산모델 관리 화면 표시"""
    st.title("생산모델 관리")
    
    # 세션 상태에 모델 데이터 초기화
    if "models_data" not in st.session_state:
        st.session_state.models_data = [
            {"id": 1, "name": "PA1", "process": "C1"},
            {"id": 2, "name": "PA1", "process": "C2"},
            {"id": 3, "name": "PA2", "process": "C1"},
            {"id": 4, "name": "PA2", "process": "C2"},
            {"id": 5, "name": "PA3", "process": "C1"},
            {"id": 6, "name": "PA3", "process": "C2"},
            {"id": 7, "name": "B6", "process": "C1"},
            {"id": 8, "name": "B6", "process": "C2"},
            {"id": 9, "name": "B6M", "process": "C1"},
            {"id": 10, "name": "B6M", "process": "C2"},
            {"id": 11, "name": "B6S6", "process": "C1"},
            {"id": 12, "name": "B6S6", "process": "C2"},
            {"id": 13, "name": "B5S6", "process": "C1"},
            {"id": 18, "name": "B5S6", "process": "C2"},
            {"id": 19, "name": "PS SUB6", "process": "C1"},
            {"id": 20, "name": "PS SUB6", "process": "C2"},
            {"id": 22, "name": "B7SUB", "process": "C2"},
            {"id": 23, "name": "B7SUB", "process": "C1"},
            {"id": 24, "name": "B7MMW", "process": "C1"},
            {"id": 25, "name": "B7MMW", "process": "C2"},
            {"id": 26, "name": "B7SUB6", "process": "C1"},
            {"id": 27, "name": "B7SUB6", "process": "C2"},
            {"id": 28, "name": "B7DUALSIM", "process": "C1"},
            {"id": 29, "name": "B7DUALSIM", "process": "C2"},
            {"id": 31, "name": "B7R SUB", "process": "C1"},
            {"id": 32, "name": "B7R SUB", "process": "C2"},
            {"id": 33, "name": "B7R MMW", "process": "C2"},
            {"id": 34, "name": "B7R MMW", "process": "C1"},
            {"id": 35, "name": "B7R SUB6", "process": "C1"},
            {"id": 36, "name": "B7R SUB6", "process": "C2"},
            {"id": 37, "name": "B5M", "process": "C1"},
            {"id": 38, "name": "B5M", "process": "C2"},
            {"id": 42, "name": "E1", "process": "C1"},
            {"id": 43, "name": "E1", "process": "C2"},
            {"id": 44, "name": "BY2", "process": "C2"},
            {"id": 45, "name": "BY2", "process": "C1"},
            {"id": 46, "name": "Y2", "process": "C1"},
            {"id": 47, "name": "Y2", "process": "C2"},
            {"id": 48, "name": "A516", "process": "C1"},
            {"id": 49, "name": "A516", "process": "C2"}
        ]
    
    # 탭 생성
    tabs = st.tabs(["생산모델 목록", "생산모델 추가/수정"])
    
    with tabs[0]:
        show_model_list()
    
    with tabs[1]:
        show_model_add_edit()

def show_model_list():
    """생산모델 목록 페이지"""
    st.header("생산모델 목록 🔗")
    
    # 검색어 필드
    search = st.text_input("검색어", placeholder="검색어를 입력하세요", key="search_input")
    
    # 세션 상태에서 모델 데이터 가져오기
    models_df = pd.DataFrame(st.session_state.models_data)
    
    # 검색어 필터링
    if search and not models_df.empty:
        models_df = models_df[models_df['name'].str.contains(search, case=False)]
    
    # 테이블로 표시
    if not models_df.empty:
        st.dataframe(
            models_df,
            column_config={
                "id": st.column_config.NumberColumn("모델No.", format="%d", width="small"),
                "name": st.column_config.TextColumn("모델명", width="medium"),
                "process": st.column_config.TextColumn("공정", width="medium"),
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("등록된 생산모델이 없습니다.")

def show_model_add_edit():
    """생산모델 추가/수정 페이지"""
    # 세션 상태 초기화
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
        st.session_state.edit_model_id = None
    
    # 모델 삭제 섹션
    st.header("생산모델 삭제")
    
    if st.session_state.models_data:
        model_options = ["모델 선택"] + [f"{m['id']}-{m['name']}" for m in st.session_state.models_data]
        selected_model = st.selectbox("삭제할 모델 선택", model_options, key="delete_model_select")
        
        if selected_model != "모델 선택" and st.button("삭제"):
            model_id = int(selected_model.split('-')[0])
            # 세션 상태에서 해당 모델 삭제
            st.session_state.models_data = [m for m in st.session_state.models_data if m['id'] != model_id]
            st.warning(f"모델 '{selected_model}'이(가) 삭제되었습니다.")
            # 편집 모드 초기화
            st.session_state.edit_mode = False
            st.session_state.edit_model_id = None
            st.rerun()
    else:
        st.info("등록된 모델이 없습니다.")
    
    # 모델 선택 (수정 용)
    st.header("생산모델 수정")
    if st.session_state.models_data:
        edit_model_options = ["새 모델 추가"] + [f"{m['id']}-{m['name']}" for m in st.session_state.models_data]
        selected_edit_model = st.selectbox(
            "수정할 모델 선택 (또는 새 모델 추가)", 
            edit_model_options, 
            key="edit_model_select"
        )
        
        if selected_edit_model != "새 모델 추가":
            # 선택한 모델 ID 저장
            model_id = int(selected_edit_model.split('-')[0])
            st.session_state.edit_mode = True
            st.session_state.edit_model_id = model_id
        else:
            # 새 모델 추가 모드
            st.session_state.edit_mode = False
            st.session_state.edit_model_id = None
    else:
        st.info("등록된 모델이 없습니다. 새 모델을 추가해주세요.")
    
    # 모델 정보 가져오기
    selected_model_data = None
    if st.session_state.edit_mode and st.session_state.edit_model_id:
        selected_model_data = next(
            (m for m in st.session_state.models_data if m['id'] == st.session_state.edit_model_id), 
            None
        )
    
    # 모델 추가/수정 폼
    form_title = "생산모델 수정" if st.session_state.edit_mode else "생산모델 추가"
    st.header(form_title)
    
    # 항목 입력 폼
    with st.form(key="model_form"):
        # 수정 모드일 경우 기존 값으로 필드를 미리 채움
        if st.session_state.edit_mode and selected_model_data:
            # 수정 모드에서는 hidden model_id 사용
            st.text_input("모델No.", value=str(selected_model_data["id"]), disabled=True, key="display_model_no")
            # 실제 model_id는 hidden 상태로 유지
            model_id = selected_model_data["id"]
            name = st.text_input("모델명", value=selected_model_data["name"])
            process = st.text_input("공정", value=selected_model_data["process"])
        else:
            model_id = None
            model_no = st.text_input("모델No.")
            name = st.text_input("모델명")
            process = st.text_input("공정")
        
        # 제출 버튼
        submit_label = "수정" if st.session_state.edit_mode else "저장"
        submit = st.form_submit_button(submit_label)
        
        if submit:
            if st.session_state.edit_mode:
                # 수정 모드
                if not name or not process:
                    st.error("모든 필드를 입력해주세요.")
                else:
                    # 모델 수정 (이미 model_id가 있음)
                    for i, model in enumerate(st.session_state.models_data):
                        if model['id'] == model_id:
                            st.session_state.models_data[i] = {"id": model_id, "name": name, "process": process}
                            st.success(f"생산모델 '{name}'이(가) 수정되었습니다.")
                            # 편집 모드 초기화
                            st.session_state.edit_mode = False 
                            st.session_state.edit_model_id = None
                            st.rerun()
                            break
            else:
                # 추가 모드
                if not model_no or not name or not process:
                    st.error("모든 필드를 입력해주세요.")
                else:
                    try:
                        model_id = int(model_no)
                        
                        # 중복 모델 번호 확인
                        for model in st.session_state.models_data:
                            if model['id'] == model_id:
                                st.error(f"모델No. {model_no}는 이미 존재합니다. 다른 번호를 사용해주세요.")
                                return
                        
                        # 세션 상태에 모델 추가
                        new_model = {"id": model_id, "name": name, "process": process}
                        st.session_state.models_data.append(new_model)
                        st.success(f"생산모델 '{name}'이(가) 추가되었습니다.")
                        st.rerun()
                    except ValueError:
                        st.error("모델No.는 숫자로 입력해주세요.")

def get_all_models():
    """모든 생산모델 반환 (세션 상태에서)"""
    if "models_data" not in st.session_state:
        st.session_state.models_data = [
            {"id": 1, "name": "PA1", "process": "C1"},
            {"id": 2, "name": "PA1", "process": "C2"},
            {"id": 3, "name": "PA2", "process": "C1"},
            {"id": 4, "name": "PA2", "process": "C2"},
            {"id": 5, "name": "PA3", "process": "C1"},
            {"id": 6, "name": "PA3", "process": "C2"},
            {"id": 7, "name": "B6", "process": "C1"},
            {"id": 8, "name": "B6", "process": "C2"},
            {"id": 9, "name": "B6M", "process": "C1"},
            {"id": 10, "name": "B6M", "process": "C2"},
            {"id": 11, "name": "B6S6", "process": "C1"},
            {"id": 12, "name": "B6S6", "process": "C2"},
            {"id": 13, "name": "B5S6", "process": "C1"},
            {"id": 18, "name": "B5S6", "process": "C2"},
            {"id": 19, "name": "PS SUB6", "process": "C1"},
            {"id": 20, "name": "PS SUB6", "process": "C2"},
            {"id": 22, "name": "B7SUB", "process": "C2"},
            {"id": 23, "name": "B7SUB", "process": "C1"},
            {"id": 24, "name": "B7MMW", "process": "C1"},
            {"id": 25, "name": "B7MMW", "process": "C2"},
            {"id": 26, "name": "B7SUB6", "process": "C1"},
            {"id": 27, "name": "B7SUB6", "process": "C2"},
            {"id": 28, "name": "B7DUALSIM", "process": "C1"},
            {"id": 29, "name": "B7DUALSIM", "process": "C2"},
            {"id": 31, "name": "B7R SUB", "process": "C1"},
            {"id": 32, "name": "B7R SUB", "process": "C2"},
            {"id": 33, "name": "B7R MMW", "process": "C2"},
            {"id": 34, "name": "B7R MMW", "process": "C1"},
            {"id": 35, "name": "B7R SUB6", "process": "C1"},
            {"id": 36, "name": "B7R SUB6", "process": "C2"},
            {"id": 37, "name": "B5M", "process": "C1"},
            {"id": 38, "name": "B5M", "process": "C2"},
            {"id": 42, "name": "E1", "process": "C1"},
            {"id": 43, "name": "E1", "process": "C2"},
            {"id": 44, "name": "BY2", "process": "C2"},
            {"id": 45, "name": "BY2", "process": "C1"},
            {"id": 46, "name": "Y2", "process": "C1"},
            {"id": 47, "name": "Y2", "process": "C2"},
            {"id": 48, "name": "A516", "process": "C1"},
            {"id": 49, "name": "A516", "process": "C2"}
        ]
    return pd.DataFrame(st.session_state.models_data) 