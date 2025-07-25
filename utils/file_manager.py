"""
파일 관리 모듈
검사 사진 업로드, Excel 보고서 내보내기 등 파일 관련 기능 제공
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from io import BytesIO
import base64
from PIL import Image
import uuid
from utils.supabase_client import get_supabase_client
from utils.vietnam_timezone import get_vietnam_display_time

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)


class FileManager:
    """파일 관리 클래스"""
    
    def __init__(self):
        self.upload_dir = "uploads"
        self.allowed_image_types = ['png', 'jpg', 'jpeg', 'gif', 'bmp']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # 업로드 디렉토리 생성
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def upload_inspection_photos(self, inspection_id):
        """검사 사진 업로드 기능"""
        st.subheader("📷 검사 사진 첨부")
        
        # 파일 업로드 위젯
        uploaded_files = st.file_uploader(
            "검사 사진을 업로드하세요",
            type=self.allowed_image_types,
            accept_multiple_files=True,
            help=f"지원 형식: {', '.join(self.allowed_image_types).upper()}, 최대 크기: {self.max_file_size//1024//1024}MB"
        )
        
        if uploaded_files:
            st.write(f"📁 **업로드된 파일 수**: {len(uploaded_files)}개")
            
            saved_files = []
            
            for uploaded_file in uploaded_files:
                # 파일 크기 검증
                if uploaded_file.size > self.max_file_size:
                    st.error(f"❌ {uploaded_file.name}: 파일 크기가 {self.max_file_size//1024//1024}MB를 초과합니다.")
                    continue
                
                # 파일 확장자 검증
                file_ext = uploaded_file.name.split('.')[-1].lower()
                if file_ext not in self.allowed_image_types:
                    st.error(f"❌ {uploaded_file.name}: 지원하지 않는 파일 형식입니다.")
                    continue
                
                try:
                    # 고유 파일명 생성
                    unique_filename = f"{inspection_id}_{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
                    file_path = os.path.join(self.upload_dir, unique_filename)
                    
                    # 파일 저장
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    saved_files.append({
                        'original_name': uploaded_file.name,
                        'saved_name': unique_filename,
                        'file_path': file_path,
                        'file_size': uploaded_file.size
                    })
                    
                    st.success(f"✅ {uploaded_file.name} 업로드 완료")
                    
                    # 이미지 미리보기
                    try:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=uploaded_file.name, width=200)
                    except Exception:
                        st.write(f"📄 {uploaded_file.name} (미리보기 불가)")
                        
                except Exception as e:
                    st.error(f"❌ {uploaded_file.name} 업로드 실패: {str(e)}")
            
            if saved_files:
                st.info(f"💾 총 {len(saved_files)}개 파일이 저장되었습니다.")
                
                # 파일 목록 표시
                with st.expander("📂 저장된 파일 목록"):
                    for file_info in saved_files:
                        st.write(f"- **{file_info['original_name']}** ({file_info['file_size']:,} bytes)")
                
                return saved_files
        
        return []
    
    def export_to_excel(self, data_dict, filename_prefix="QC_Report"):
        """Excel 보고서 내보내기"""
        st.subheader("📊 Excel 보고서 내보내기")
        
        try:
            # 베트남 시간을 포함한 파일명 생성
            timestamp = get_vietnam_display_time().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.xlsx"
            
            # BytesIO 객체 생성
            output = BytesIO()
            
            # Excel 파일 생성
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, data in data_dict.items():
                    if isinstance(data, pd.DataFrame):
                        data.to_excel(writer, sheet_name=sheet_name, index=False)
                    elif isinstance(data, list):
                        # 리스트를 DataFrame으로 변환
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        # 단일 값이나 기타 데이터
                        df = pd.DataFrame([data])
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            output.seek(0)
            
            # 다운로드 버튼 제공
            st.download_button(
                label=f"📥 {filename} 다운로드",
                data=output.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="클릭하여 Excel 파일을 다운로드하세요"
            )
            
            st.success(f"✅ Excel 보고서가 준비되었습니다: **{filename}**")
            
            # 보고서 내용 미리보기
            with st.expander("📋 보고서 내용 미리보기"):
                for sheet_name, data in data_dict.items():
                    st.write(f"**📄 {sheet_name} 시트:**")
                    if isinstance(data, pd.DataFrame):
                        st.dataframe(data.head(), use_container_width=True)
                    elif isinstance(data, list) and len(data) > 0:
                        df = pd.DataFrame(data)
                        st.dataframe(df.head(), use_container_width=True)
                    else:
                        st.write(data)
                    st.write("---")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Excel 내보내기 실패: {str(e)}")
            return False
    
    def get_inspection_report_data(self, start_date, end_date):
        """검사 보고서 데이터 조회"""
        try:
            supabase = get_supabase_client()
            
            # 검사 데이터 조회
            inspection_result = supabase.table('inspection_data') \
                .select('*, inspectors(name), production_models(model_name, model_no)') \
                .gte('inspection_date', start_date.strftime('%Y-%m-%d')) \
                .lte('inspection_date', end_date.strftime('%Y-%m-%d')) \
                .execute()
            
            inspections = inspection_result.data if inspection_result.data else []
            
            # 데이터 가공
            report_data = []
            for inspection in inspections:
                report_data.append({
                    '검사일자': inspection.get('inspection_date'),
                    '검사자': inspection.get('inspectors', {}).get('name', 'N/A') if inspection.get('inspectors') else 'N/A',
                    '모델명': inspection.get('production_models', {}).get('model_name', 'N/A') if inspection.get('production_models') else 'N/A',
                    '모델번호': inspection.get('production_models', {}).get('model_no', 'N/A') if inspection.get('production_models') else 'N/A',
                    '검사결과': inspection.get('result'),
                    '계획수량': inspection.get('planned_quantity', 0),
                    '검사수량': inspection.get('total_inspected', 0),
                    '불량수량': inspection.get('defect_quantity', 0),
                    '합격수량': inspection.get('pass_quantity', 0),
                    '공정': inspection.get('process'),
                    '로트번호': inspection.get('lot_number'),
                    '비고': inspection.get('notes')
                })
            
            return report_data
            
        except Exception as e:
            st.error(f"데이터 조회 실패: {str(e)}")
            return []
    
    def get_kpi_summary_data(self, start_date, end_date):
        """KPI 요약 데이터 조회"""
        try:
            from pages.dashboard import calculate_kpi_data
            kpi_data = calculate_kpi_data()
            
            summary_data = [{
                '항목': 'KPI 요약',
                '기간': f"{start_date} ~ {end_date}",
                '총 검사 건수': kpi_data.get('total_inspections', 0),
                '합격 건수': kpi_data.get('pass_count', 0),
                '총 검사 수량': kpi_data.get('total_inspected_qty', 0),
                '불량 수량': kpi_data.get('total_defect_qty', 0),
                '합격 수량': kpi_data.get('total_pass_qty', 0),
                '불량률 (%)': kpi_data.get('defect_rate', 0),
                '검사 효율성 (%)': kpi_data.get('inspection_efficiency', 0),
                '수량 기준 합격률 (%)': kpi_data.get('quantity_pass_rate', 0)
            }]
            
            return summary_data
            
        except Exception as e:
            st.error(f"KPI 데이터 조회 실패: {str(e)}")
            return []
    
    def create_comprehensive_report(self, start_date, end_date):
        """종합 보고서 생성"""
        st.info("📊 보고서 데이터를 준비하고 있습니다...")
        
        # 데이터 수집
        inspection_data = self.get_inspection_report_data(start_date, end_date)
        kpi_data = self.get_kpi_summary_data(start_date, end_date)
        
        if not inspection_data and not kpi_data:
            st.warning("⚠️ 선택한 기간에 보고서 데이터가 없습니다.")
            return False
        
        # Excel 데이터 구성
        excel_data = {}
        
        if inspection_data:
            excel_data["검사 실적"] = pd.DataFrame(inspection_data)
        
        if kpi_data:
            excel_data["KPI 요약"] = pd.DataFrame(kpi_data)
        
        # 검사자별 성과 (추가 시트)
        try:
            from pages.dashboard import get_inspector_performance_data
            performance_data = get_inspector_performance_data()
            if performance_data:
                excel_data["검사자 성과"] = pd.DataFrame(performance_data)
        except Exception:
            pass
        
        # 보고서 메타정보 (베트남 시간대)
        meta_info = [{
            '보고서 생성일시': get_vietnam_display_time().strftime('%Y-%m-%d %H:%M:%S'),
            '보고서 기간': f"{start_date} ~ {end_date}",
            '시스템': 'CNC QC KPI 시스템',
            '버전': '1.0'
        }]
        excel_data["보고서 정보"] = pd.DataFrame(meta_info)
        
        # Excel 파일 생성 및 다운로드 제공
        return self.export_to_excel(excel_data, "CNC_QC_종합보고서")


def show_file_management():
    """파일 관리 페이지"""
    st.title("📁 파일 관리")
    
    file_manager = FileManager()
    
    tab1, tab2 = st.tabs(["📥 Excel 보고서 내보내기", "📷 사진 관리"])
    
    with tab1:
        show_export_tab(file_manager)
    
    with tab2:
        show_photo_management_tab(file_manager)


def show_export_tab(file_manager):
    """Excel 내보내기 탭"""
    st.subheader("📊 Excel 보고서 내보내기")
    
    # 기간 선택 (베트남 시간대 기준)
    vietnam_today = get_vietnam_date()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "시작 날짜",
            value=vietnam_today - timedelta(days=30),
            max_value=vietnam_today
        )
    with col2:
        end_date = st.date_input(
            "종료 날짜",
            value=vietnam_today,
            max_value=vietnam_today
        )
    
    if start_date > end_date:
        st.error("❌ 시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
        return
    
    # 보고서 유형 선택
    report_type = st.selectbox(
        "보고서 유형 선택",
        ["종합 보고서", "검사 실적만", "KPI 요약만"],
        help="내보낼 보고서의 유형을 선택하세요"
    )
    
    # 보고서 생성 버튼
    if st.button("📊 보고서 생성", type="primary", use_container_width=True):
        if report_type == "종합 보고서":
            file_manager.create_comprehensive_report(start_date, end_date)
        elif report_type == "검사 실적만":
            inspection_data = file_manager.get_inspection_report_data(start_date, end_date)
            if inspection_data:
                excel_data = {"검사 실적": pd.DataFrame(inspection_data)}
                file_manager.export_to_excel(excel_data, "검사실적보고서")
            else:
                st.warning("선택한 기간에 검사 실적 데이터가 없습니다.")
        elif report_type == "KPI 요약만":
            kpi_data = file_manager.get_kpi_summary_data(start_date, end_date)
            if kpi_data:
                excel_data = {"KPI 요약": pd.DataFrame(kpi_data)}
                file_manager.export_to_excel(excel_data, "KPI요약보고서")
            else:
                st.warning("KPI 데이터를 불러올 수 없습니다.")


def show_photo_management_tab(file_manager):
    """사진 관리 탭"""
    st.subheader("📷 검사 사진 관리")
    
    st.info("💡 검사 데이터 입력 시 사진을 첨부할 수 있습니다.")
    
    # 검사 ID 입력 (테스트용)
    test_inspection_id = st.text_input(
        "검사 ID (테스트용)",
        value="TEST_" + get_vietnam_display_time().replace(' ', '_').replace(':', ''),
        help="실제 검사 ID를 입력하거나 테스트용 ID를 사용하세요"
    )
    
    if test_inspection_id:
        uploaded_files = file_manager.upload_inspection_photos(test_inspection_id)
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)}개 파일이 업로드되었습니다.")
    
    # 업로드된 파일 목록 (실제 구현에서는 DB에서 조회)
    with st.expander("📂 업로드된 파일 목록 (샘플)"):
        st.write("실제 운영에서는 데이터베이스에서 파일 목록을 조회하여 표시합니다.")
        st.write("- 검사_001_20250115_001.jpg (불량 부위 사진)")
        st.write("- 검사_001_20250115_002.jpg (전체 모습)")
        st.write("- 검사_002_20250115_001.png (측정 결과 화면)")


if __name__ == "__main__":
    show_file_management() 