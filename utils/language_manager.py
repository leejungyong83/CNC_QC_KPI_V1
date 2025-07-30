"""
언어 관리 시스템
QC KPI 프로젝트의 다국어 지원을 위한 핵심 모듈
"""

import streamlit as st
from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime
from .google_translator import translate_with_cache
from .advanced_cache import get_advanced_cache, cache_translation, get_cache_performance_report

class LanguageManager:
    """언어 관리 및 번역 시스템"""
    
    # 지원 언어 목록
    SUPPORTED_LANGUAGES = {
        'ko': {'name': '한국어', 'flag': '🇰🇷', 'code': 'ko'},
        'en': {'name': 'English', 'flag': '🇺🇸', 'code': 'en'},
        'vi': {'name': 'Tiếng Việt', 'flag': '🇻🇳', 'code': 'vi'},
        'zh': {'name': '中文', 'flag': '🇨🇳', 'code': 'zh'},
    }
    
    # 기본 언어
    DEFAULT_LANGUAGE = 'ko'
    
    def __init__(self):
        """언어 매니저 초기화"""
        self.current_language = self._get_session_language()
        self.static_translations = self._load_static_translations()
        self.translation_cache = {}
        
    def _get_session_language(self) -> str:
        """세션에서 현재 언어 설정 가져오기"""
        if 'language' not in st.session_state:
            st.session_state.language = self.DEFAULT_LANGUAGE
        return st.session_state.language
    
    def set_language(self, language_code: str) -> bool:
        """언어 설정 변경"""
        if language_code in self.SUPPORTED_LANGUAGES:
            st.session_state.language = language_code
            self.current_language = language_code
            # 캐시 초기화 (새로운 언어로 전환)
            self.translation_cache.clear()
            return True
        return False
    
    def get_current_language(self) -> str:
        """현재 설정된 언어 코드 반환"""
        return self.current_language
    
    def get_language_info(self, language_code: Optional[str] = None) -> Dict[str, str]:
        """언어 정보 반환 (이름, 플래그, 코드)"""
        lang_code = language_code or self.current_language
        return self.SUPPORTED_LANGUAGES.get(lang_code, self.SUPPORTED_LANGUAGES[self.DEFAULT_LANGUAGE])
    
    def _load_static_translations(self) -> Dict[str, Dict[str, str]]:
        """정적 번역 사전 로드 - QC/KPI 전문 용어 확장 버전"""
        # KPI 전문 용어 및 UI 요소 번역사전
        return {
            'ko': {
                # 메뉴 항목
                'dashboard': '대시보드',
                'inspection_input': '검사 입력',
                'reports': '리포트',
                'inspector_management': '검사자 관리',
                'item_management': '제품 관리',
                'defect_type_management': '불량 유형 관리',
                'admin_management': '관리자 관리',
                'shift_reports': '교대조 리포트',
                
                # KPI 핵심 지표
                'defect_rate': '불량률',
                'inspection_efficiency': '검사 효율',
                'total_inspected': '총 검사 수량',
                'defect_quantity': '불량 수량',
                'pass_rate': '합격률',
                'overall_defect_rate': '전체 불량률',
                'daily_defect_rate': '일일 불량률',
                'inspection_count': '검사 건수',
                'inspection_frequency': '검사 빈도',
                'quality_target': '품질 목표',
                'performance_indicator': '성과 지표',
                
                # 품질 관련 용어
                'quality_control': '품질관리',
                'quality_assurance': '품질보증',
                'quality_improvement': '품질개선',
                'defect_analysis': '불량 분석',
                'defect_prevention': '불량 예방',
                'defect_trend': '불량 추이',
                'defect_classification': '불량 분류',
                'root_cause_analysis': '근본원인 분석',
                'corrective_action': '시정조치',
                'preventive_action': '예방조치',
                
                # 검사 프로세스
                'inspection_process': '검사 프로세스',
                'inspection_standard': '검사 기준',
                'inspection_method': '검사 방법',
                'inspection_criteria': '검사 기준',
                'inspection_result': '검사 결과',
                'inspection_record': '검사 기록',
                'inspection_data': '검사 데이터',
                'inspection_schedule': '검사 일정',
                'inspection_status': '검사 상태',
                'sampling_inspection': '샘플링 검사',
                'final_inspection': '최종 검사',
                'incoming_inspection': '입고 검사',
                
                # 생산 관련
                'production_line': '생산라인',
                'production_model': '생산모델',
                'production_quantity': '생산수량',
                'production_plan': '생산계획',
                'production_status': '생산상태',
                'manufacturing_process': '제조공정',
                'work_order': '작업지시',
                'batch_number': '배치번호',
                'lot_number': '로트번호',
                
                # 교대조 시스템 (확장)
                'day_shift': '주간',
                'night_shift': '야간',
                'shift_a': 'A조',
                'shift_b': 'B조',
                'work_date': '작업일',
                'shift_schedule': '교대 일정',
                'shift_handover': '교대 인수인계',
                'shift_performance': '교대 성과',
                'shift_comparison': '교대 비교',
                'shift_analysis': '교대 분석',
                
                # 작업자/검사자
                'inspector': '검사자',
                'operator': '작업자',
                'supervisor': '감독자',
                'manager': '관리자',
                'employee_id': '사번',
                'employee_name': '성명',
                'department': '부서',
                'position': '직급',
                'experience': '경력',
                'certification': '자격증',
                
                # 통계/분석 용어
                'statistical_analysis': '통계 분석',
                'trend_analysis': '추이 분석',
                'pareto_analysis': '파레토 분석',
                'correlation_analysis': '상관 관계 분석',
                'control_chart': '관리도',
                'process_capability': '공정 능력',
                'cpk_index': 'Cpk 지수',
                'standard_deviation': '표준편차',
                'average': '평균',
                'median': '중앙값',
                'percentile': '백분위수',
                
                # 보고서/문서
                'report_generation': '보고서 생성',
                'daily_report': '일일 보고서',
                'weekly_report': '주간 보고서',
                'monthly_report': '월간 보고서',
                'summary_report': '요약 보고서',
                'detailed_report': '상세 보고서',
                'inspection_report': '검사 보고서',
                'quality_report': '품질 보고서',
                'performance_report': '성과 보고서',
                
                # 시스템/기술 용어
                'real_time_monitoring': '실시간 모니터링',
                'data_collection': '데이터 수집',
                'data_analysis': '데이터 분석',
                'data_visualization': '데이터 시각화',
                'automated_inspection': '자동 검사',
                'manual_inspection': '수동 검사',
                'barcode_scanning': '바코드 스캔',
                'digital_recording': '디지털 기록',
                
                # 버튼 및 액션 (확장)
                'save': '저장',
                'delete': '삭제',
                'edit': '수정',
                'search': '검색',
                'export': '내보내기',
                'import': '가져오기',
                'refresh': '새로고침',
                'cancel': '취소',
                'confirm': '확인',
                'submit': '제출',
                'download': '다운로드',
                'upload': '업로드',
                'print': '인쇄',
                'email': '이메일',
                'notification': '알림',
                
                # 상태/결과 (확장)
                'success': '성공',
                'error': '오류',
                'warning': '경고',
                'info': '정보',
                'loading': '로딩 중...',
                'completed': '완료',
                'pending': '대기 중',
                'in_progress': '진행 중',
                'cancelled': '취소됨',
                'approved': '승인됨',
                'rejected': '거부됨',
                'pass': '합격',
                'fail': '불합격',
                'acceptable': '허용',
                'unacceptable': '불허용',
                
                # 시간/날짜 (확장)
                'date': '날짜',
                'time': '시간',
                'datetime': '일시',
                'created_at': '생성일시',
                'updated_at': '수정일시',
                'start_date': '시작일',
                'end_date': '종료일',
                'due_date': '마감일',
                'period': '기간',
                'duration': '소요시간',
                'timestamp': '타임스탬프',
                
                # 검사 관련 (확장)
                'model': '모델',
                'process': '공정',
                'result': '결과',
                'notes': '비고',
                'comment': '코멘트',
                'remark': '특이사항',
                'specification': '사양',
                'tolerance': '공차',
                'measurement': '측정값',
                'dimension': '치수',
                'weight': '무게',
                'temperature': '온도',
                'pressure': '압력',
                'humidity': '습도',
                
                # UI 공통 요소
                'login': '로그인',
                'logout': '로그아웃',
                'username': '사용자명',
                'password': '비밀번호',
                'email': '이메일',
                'welcome': '환영합니다',
                'menu': '메뉴',
                'settings': '설정',
                'preferences': '환경설정',
                'profile': '프로필',
                'help': '도움말',
                'about': '정보',
                'version': '버전',
                'language': '언어',
                'theme': '테마',
                
                # 페이지 제목들
                'CNC QC KPI 대시보드': 'CNC QC KPI 대시보드',
                'QC KPI 시스템': 'QC KPI 시스템',
                '검사실적 관리': '검사실적 관리',
                '실적 데이터 입력': '실적 데이터 입력',
                '실적 데이터 조회': '실적 데이터 조회',
                '데이터 수정': '데이터 수정',
                '데이터 삭제': '데이터 삭제',
                '보고서': '보고서',
                '오늘 교대조 타임라인': '오늘 교대조 타임라인',
                '오늘 불량률': '오늘 불량률',
                '목표': '목표',
                '현재': '현재',
                '달성률': '달성률',
                '초과 달성': '초과 달성',
                '불량율 목표 달성': '불량율 목표 달성',
                '불량율 목표 미달성': '불량율 목표 미달성',
                '개선 필요': '개선 필요',
                '검사효율성 목표 달성': '검사효율성 목표 달성',
                '검사효율성 목표 미달성': '검사효율성 목표 미달성',
                '부족분': '부족분',
                '불량률 우수': '불량률 우수',
                '효율성 우수': '효율성 우수',
                '차이': '차이',
                
                # 메뉴 번역
                '데이터입력': '데이터입력',
                '검사데이터입력': '검사데이터입력',
                '리포트': '리포트',
                '종합대시보드': '종합대시보드',
                '일별분석': '일별분석',
                '주별분석': '주별분석',
                '월별분석': '월별분석',
                '불량분석': '불량분석',
                '교대조분석': '교대조분석',
                '관리자 메뉴': '관리자 메뉴',
                '사용자관리': '사용자관리',
                '관리자관리': '관리자관리',
                '검사자관리': '검사자관리',
                '생산모델관리': '생산모델관리',
                '불량유형관리': '불량유형관리',
                'Supabase설정': 'Supabase설정',
                '시스템상태': '시스템상태',
                '성능모니터링': '성능모니터링',
                '자동보고서': '자동보고서',
                '고급분석': '고급분석',
                '알림': '알림',
                '알림센터': '알림센터',
                '파일': '파일',
                '파일관리': '파일관리',
                '모바일': '모바일',
                '모바일 모드': '모바일 모드',
                '로그아웃': '로그아웃',
                '환영합니다': '환영합니다',
                '권한': '권한',
                '메뉴': '메뉴',
                
                # 메시지들
                '로그인 성공!': '로그인 성공!',
                '이메일 또는 비밀번호가 올바르지 않습니다.': '이메일 또는 비밀번호가 올바르지 않습니다.',
                '이메일 또는 비밀번호가 잘못되었습니다.': '이메일 또는 비밀번호가 잘못되었습니다.',
                '로그인 중 오류 발생': '로그인 중 오류 발생',
                '이메일과 비밀번호를 모두 입력해주세요.': '이메일과 비밀번호를 모두 입력해주세요.',
                '이메일': '이메일',
                '비밀번호': '비밀번호',
                
                # 폼 관련
                '위 드롭다운에서 불량유형을 선택하고 ➕ 추가 버튼을 클릭하세요': '위 드롭다운에서 불량유형을 선택하고 ➕ 추가 버튼을 클릭하세요',
                '선택된 불량유형의 수량을 입력해주세요': '선택된 불량유형의 수량을 입력해주세요',
                '불량유형 데이터를 불러올 수 없습니다. 관리자에게 문의하세요.': '불량유형 데이터를 불러올 수 없습니다. 관리자에게 문의하세요.',
                '검사 기본 정보': '검사 기본 정보',
            },
            'en': {
                # 메뉴 항목
                'dashboard': 'Dashboard',
                'inspection_input': 'Inspection Input',
                'reports': 'Reports',
                'inspector_management': 'Inspector Management',
                'item_management': 'Item Management',
                'defect_type_management': 'Defect Type Management',
                'admin_management': 'Admin Management',
                'shift_reports': 'Shift Reports',
                
                # KPI 핵심 지표
                'defect_rate': 'Defect Rate',
                'inspection_efficiency': 'Inspection Efficiency',
                'total_inspected': 'Total Inspected',
                'defect_quantity': 'Defect Quantity',
                'pass_rate': 'Pass Rate',
                'overall_defect_rate': 'Overall Defect Rate',
                'daily_defect_rate': 'Daily Defect Rate',
                'inspection_count': 'Inspection Count',
                'inspection_frequency': 'Inspection Frequency',
                'quality_target': 'Quality Target',
                'performance_indicator': 'Performance Indicator',
                
                # 품질 관련 용어
                'quality_control': 'Quality Control',
                'quality_assurance': 'Quality Assurance',
                'quality_improvement': 'Quality Improvement',
                'defect_analysis': 'Defect Analysis',
                'defect_prevention': 'Defect Prevention',
                'defect_trend': 'Defect Trend',
                'defect_classification': 'Defect Classification',
                'root_cause_analysis': 'Root Cause Analysis',
                'corrective_action': 'Corrective Action',
                'preventive_action': 'Preventive Action',
                
                # 검사 프로세스
                'inspection_process': 'Inspection Process',
                'inspection_standard': 'Inspection Standard',
                'inspection_method': 'Inspection Method',
                'inspection_criteria': 'Inspection Criteria',
                'inspection_result': 'Inspection Result',
                'inspection_record': 'Inspection Record',
                'inspection_data': 'Inspection Data',
                'inspection_schedule': 'Inspection Schedule',
                'inspection_status': 'Inspection Status',
                'sampling_inspection': 'Sampling Inspection',
                'final_inspection': 'Final Inspection',
                'incoming_inspection': 'Incoming Inspection',
                
                # 생산 관련
                'production_line': 'Production Line',
                'production_model': 'Production Model',
                'production_quantity': 'Production Quantity',
                'production_plan': 'Production Plan',
                'production_status': 'Production Status',
                'manufacturing_process': 'Manufacturing Process',
                'work_order': 'Work Order',
                'batch_number': 'Batch Number',
                'lot_number': 'Lot Number',
                
                # 교대조 시스템 (확장)
                'day_shift': 'Day Shift',
                'night_shift': 'Night Shift',
                'shift_a': 'Shift A',
                'shift_b': 'Shift B',
                'work_date': 'Work Date',
                'shift_schedule': 'Shift Schedule',
                'shift_handover': 'Shift Handover',
                'shift_performance': 'Shift Performance',
                'shift_comparison': 'Shift Comparison',
                'shift_analysis': 'Shift Analysis',
                
                # 작업자/검사자
                'inspector': 'Inspector',
                'operator': 'Operator',
                'supervisor': 'Supervisor',
                'manager': 'Manager',
                'employee_id': 'Employee ID',
                'employee_name': 'Employee Name',
                'department': 'Department',
                'position': 'Position',
                'experience': 'Experience',
                'certification': 'Certification',
                
                # 통계/분석 용어
                'statistical_analysis': 'Statistical Analysis',
                'trend_analysis': 'Trend Analysis',
                'pareto_analysis': 'Pareto Analysis',
                'correlation_analysis': 'Correlation Analysis',
                'control_chart': 'Control Chart',
                'process_capability': 'Process Capability',
                'cpk_index': 'Cpk Index',
                'standard_deviation': 'Standard Deviation',
                'average': 'Average',
                'median': 'Median',
                'percentile': 'Percentile',
                
                # 보고서/문서
                'report_generation': 'Report Generation',
                'daily_report': 'Daily Report',
                'weekly_report': 'Weekly Report',
                'monthly_report': 'Monthly Report',
                'summary_report': 'Summary Report',
                'detailed_report': 'Detailed Report',
                'inspection_report': 'Inspection Report',
                'quality_report': 'Quality Report',
                'performance_report': 'Performance Report',
                
                # 시스템/기술 용어
                'real_time_monitoring': 'Real-time Monitoring',
                'data_collection': 'Data Collection',
                'data_analysis': 'Data Analysis',
                'data_visualization': 'Data Visualization',
                'automated_inspection': 'Automated Inspection',
                'manual_inspection': 'Manual Inspection',
                'barcode_scanning': 'Barcode Scanning',
                'digital_recording': 'Digital Recording',
                
                # 버튼 및 액션 (확장)
                'save': 'Save',
                'delete': 'Delete',
                'edit': 'Edit',
                'search': 'Search',
                'export': 'Export',
                'import': 'Import',
                'refresh': 'Refresh',
                'cancel': 'Cancel',
                'confirm': 'Confirm',
                'submit': 'Submit',
                'download': 'Download',
                'upload': 'Upload',
                'print': 'Print',
                'email': 'Email',
                'notification': 'Notification',
                
                # 상태/결과 (확장)
                'success': 'Success',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'loading': 'Loading...',
                'completed': 'Completed',
                'pending': 'Pending',
                'in_progress': 'In Progress',
                'cancelled': 'Cancelled',
                'approved': 'Approved',
                'rejected': 'Rejected',
                'pass': 'Pass',
                'fail': 'Fail',
                'acceptable': 'Acceptable',
                'unacceptable': 'Unacceptable',
                
                # 시간/날짜 (확장)
                'date': 'Date',
                'time': 'Time',
                'datetime': 'Date Time',
                'created_at': 'Created At',
                'updated_at': 'Updated At',
                'start_date': 'Start Date',
                'end_date': 'End Date',
                'due_date': 'Due Date',
                'period': 'Period',
                'duration': 'Duration',
                'timestamp': 'Timestamp',
                
                # 검사 관련 (확장)
                'model': 'Model',
                'process': 'Process',
                'result': 'Result',
                'notes': 'Notes',
                'comment': 'Comment',
                'remark': 'Remark',
                'specification': 'Specification',
                'tolerance': 'Tolerance',
                'measurement': 'Measurement',
                'dimension': 'Dimension',
                'weight': 'Weight',
                'temperature': 'Temperature',
                'pressure': 'Pressure',
                'humidity': 'Humidity',
                
                # UI 공통 요소
                'login': 'Login',
                'logout': 'Logout',
                'username': 'Username',
                'password': 'Password',
                'email': 'Email',
                'welcome': 'Welcome',
                'menu': 'Menu',
                'settings': 'Settings',
                'preferences': 'Preferences',
                'profile': 'Profile',
                'help': 'Help',
                'about': 'About',
                'version': 'Version',
                'language': 'Language',
                'theme': 'Theme',
                
                # 페이지 제목들
                'CNC QC KPI 대시보드': 'CNC QC KPI Dashboard',
                'QC KPI 시스템': 'QC KPI System',
                '검사실적 관리': 'Inspection Performance Management',
                '실적 데이터 입력': 'Performance Data Input',
                '실적 데이터 조회': 'Performance Data Inquiry',
                '데이터 수정': 'Data Modification',
                '데이터 삭제': 'Data Deletion',
                '보고서': 'Reports',
                '오늘 교대조 타임라인': "Today's Shift Timeline",
                '오늘 불량률': "Today's Defect Rate",
                '목표': 'Target',
                '현재': 'Current',
                '달성률': 'Achievement Rate',
                '초과 달성': 'Exceeded',
                '불량율 목표 달성': 'Defect Rate Target Achieved',
                '불량율 목표 미달성': 'Defect Rate Target Not Met',
                '개선 필요': 'Improvement Needed',
                '검사효율성 목표 달성': 'Inspection Efficiency Target Achieved',
                '검사효율성 목표 미달성': 'Inspection Efficiency Target Not Met',
                '부족분': 'Shortfall',
                '불량률 우수': 'Excellent Defect Rate',
                '효율성 우수': 'Excellent Efficiency',
                '차이': 'Difference',
                
                # 메뉴 번역
                '데이터입력': 'Data Input',
                '검사데이터입력': 'Inspection Data Input',
                '리포트': 'Reports',
                '종합대시보드': 'Main Dashboard',
                '일별분석': 'Daily Analysis',
                '주별분석': 'Weekly Analysis',
                '월별분석': 'Monthly Analysis',
                '불량분석': 'Defect Analysis',
                '교대조분석': 'Shift Analysis',
                '관리자 메뉴': 'Admin Menu',
                '사용자관리': 'User Management',
                '관리자관리': 'Admin Management',
                '검사자관리': 'Inspector Management',
                '생산모델관리': 'Production Model Management',
                '불량유형관리': 'Defect Type Management',
                'Supabase설정': 'Supabase Settings',
                '시스템상태': 'System Status',
                '성능모니터링': 'Performance Monitoring',
                '자동보고서': 'Auto Reports',
                '고급분석': 'Advanced Analytics',
                '알림': 'Notifications',
                '알림센터': 'Notification Center',
                '파일': 'Files',
                '파일관리': 'File Management',
                '모바일': 'Mobile',
                '모바일 모드': 'Mobile Mode',
                '로그아웃': 'Logout',
                '환영합니다': 'Welcome',
                '권한': 'Permission',
                '메뉴': 'Menu',
                
                # 메시지들
                '로그인 성공!': 'Login Successful!',
                '이메일 또는 비밀번호가 올바르지 않습니다.': 'Email or password is incorrect.',
                '이메일 또는 비밀번호가 잘못되었습니다.': 'Email or password is wrong.',
                '로그인 중 오류 발생': 'Error occurred during login',
                '이메일과 비밀번호를 모두 입력해주세요.': 'Please enter both email and password.',
                '이메일': 'Email',
                '비밀번호': 'Password',
                
                # 폼 관련
                '위 드롭다운에서 불량유형을 선택하고 ➕ 추가 버튼을 클릭하세요': 'Select defect type from dropdown above and click ➕ Add button',
                '선택된 불량유형의 수량을 입력해주세요': 'Please enter quantity for selected defect type',
                '불량유형 데이터를 불러올 수 없습니다. 관리자에게 문의하세요.': 'Cannot load defect type data. Please contact administrator.',
                '검사 기본 정보': 'Basic Inspection Information',
            },
            'vi': {
                # 메뉴 항목
                'dashboard': 'Bảng điều khiển',
                'inspection_input': 'Nhập kiểm tra',
                'reports': 'Báo cáo',
                'inspector_management': 'Quản lý kiểm tra viên',
                'item_management': 'Quản lý sản phẩm',
                'defect_type_management': 'Quản lý loại lỗi',
                'admin_management': 'Quản lý quản trị',
                'shift_reports': 'Báo cáo ca làm việc',
                
                # KPI 지표
                'defect_rate': 'Tỷ lệ lỗi',
                'inspection_efficiency': 'Hiệu quả kiểm tra',
                'total_inspected': 'Tổng số kiểm tra',
                'defect_quantity': 'Số lượng lỗi',
                'pass_rate': 'Tỷ lệ đạt',
                
                # 교대조 시스템
                'day_shift': 'Ca ngày',
                'night_shift': 'Ca đêm',
                'shift_a': 'Ca A',
                'shift_b': 'Ca B',
                'work_date': 'Ngày làm việc',
                
                # 버튼 및 액션
                'save': 'Lưu',
                'delete': 'Xóa',
                'edit': 'Sửa',
                'search': 'Tìm kiếm',
                'export': 'Xuất',
                'refresh': 'Làm mới',
                
                # 상태 메시지
                'success': 'Thành công',
                'error': 'Lỗi',
                'warning': 'Cảnh báo',
                'info': 'Thông tin',
                'loading': 'Đang tải...',
                
                # 날짜 및 시간
                'date': 'Ngày',
                'time': 'Thời gian',
                'created_at': 'Ngày tạo',
                'updated_at': 'Ngày cập nhật',
                
                # 검사 관련
                'inspector': 'Kiểm tra viên',
                'model': 'Mô hình',
                'process': 'Quy trình',
                'result': 'Kết quả',
                'notes': 'Ghi chú',
            },
            'zh': {
                # 메뉴 항목
                'dashboard': '仪表板',
                'inspection_input': '检查输入',
                'reports': '报告',
                'inspector_management': '检查员管理',
                'item_management': '产品管理',
                'defect_type_management': '缺陷类型管理',
                'admin_management': '管理员管理',
                'shift_reports': '班次报告',
                
                # KPI 지표
                'defect_rate': '缺陷率',
                'inspection_efficiency': '检查效率',
                'total_inspected': '总检查数',
                'defect_quantity': '缺陷数量',
                'pass_rate': '合格率',
                
                # 교대조 시스템
                'day_shift': '白班',
                'night_shift': '夜班',
                'shift_a': 'A班',
                'shift_b': 'B班',
                'work_date': '工作日期',
                
                # 버튼 및 액션
                'save': '保存',
                'delete': '删除',
                'edit': '编辑',
                'search': '搜索',
                'export': '导出',
                'refresh': '刷新',
                
                # 상태 메시지
                'success': '成功',
                'error': '错误',
                'warning': '警告',
                'info': '信息',
                'loading': '加载中...',
                
                # 날짜 및 시간
                'date': '日期',
                'time': '时间',
                'created_at': '创建时间',
                'updated_at': '更新时间',
                
                # 검사 관련
                'inspector': '检查员',
                'model': '型号',
                'process': '工艺',
                'result': '结果',
                'notes': '备注',
            }
        }
    
    def get_text(self, key: str, fallback: Optional[str] = None) -> str:
        """
        번역된 텍스트 가져오기
        1. 정적 번역사전에서 찾기
        2. 없으면 fallback 또는 원본 키 반환
        """
        # 정적 번역사전에서 찾기
        static_translation = self.static_translations.get(self.current_language, {}).get(key)
        if static_translation:
            return static_translation
        
        # 기본 언어(한국어)에서 찾기
        if self.current_language != self.DEFAULT_LANGUAGE:
            default_translation = self.static_translations.get(self.DEFAULT_LANGUAGE, {}).get(key)
            if default_translation:
                return default_translation
        
        # fallback 또는 원본 키 반환
        return fallback or key
    
    def translate_dynamic(self, text: str, target_language: Optional[str] = None) -> str:
        """
        동적 텍스트 실시간 번역 (Google Translate API 사용)
        """
        target_lang = target_language or self.current_language
        
        # 기본 언어이거나 번역이 필요 없는 경우
        if target_lang == self.DEFAULT_LANGUAGE or not text:
            return text
        
        # 캐시에서 찾기
        cache_key = f"{text}_{target_lang}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Google Translate API 사용
        try:
            translated = translate_with_cache(text, target_lang, 'ko')
            
            # 캐시에 저장
            self.translation_cache[cache_key] = translated
            return translated
            
        except Exception as e:
            # 번역 실패 시 원본 텍스트 반환
            return text
    
    def get_translated_text(self, key: str, target_language: Optional[str] = None) -> str:
        """
        텍스트 번역 (고급 캐시 통합)
        1. 정적 사전 확인
        2. 고급 캐시 확인 
        3. Google Translate API 호출
        4. 결과 캐시 저장
        """
        target_lang = target_language or self.current_language
        
        # 1. 한국어인 경우 원문 반환
        if target_lang == 'ko':
            return key
            
        # 2. 정적 번역 사전 확인
        static_translation = self.get_text(key)
        if static_translation and static_translation != key:
            return static_translation
        
        # 3. 고급 캐시에서 확인
        cache = get_advanced_cache()
        cached_result = cache.get(key, 'ko', target_lang)
        if cached_result:
            return cached_result
        
        # 4. Google Translate API 호출
        try:
            translated = translate_with_cache(key, target_lang, 'ko')
            
            if translated and translated != key:
                # 고급 캐시에 저장 (1시간 TTL)
                cache.set(key, 'ko', target_lang, translated, ttl=3600)
                return translated
                
        except Exception as e:
            print(f"번역 오류: {e}")
        
        # 5. 번역 실패시 원문 반환
        return key
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 성능 통계 반환"""
        return get_cache_performance_report()
    
    def optimize_performance(self):
        """성능 최적화 실행"""
        cache = get_advanced_cache()
        cache.optimize_cache()
        
    def clear_translation_cache(self, cache_type: str = "all"):
        """번역 캐시 삭제"""
        cache = get_advanced_cache()
        cache.clear_cache(cache_type)
    
    def get_language_selector_data(self) -> List[Dict[str, str]]:
        """언어 선택기를 위한 데이터 반환"""
        return [
            {
                'code': code,
                'name': info['name'],
                'flag': info['flag'],
                'display': f"{info['flag']} {info['name']}"
            }
            for code, info in self.SUPPORTED_LANGUAGES.items()
        ]


# 전역 언어 매니저 인스턴스
_language_manager = None

def get_language_manager() -> LanguageManager:
    """언어 매니저 싱글톤 인스턴스 반환"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager

def t(text: str, fallback: Optional[str] = None) -> str:
    """
    전역 번역 함수 (고급 캐시 통합)
    
    Args:
        text: 번역할 텍스트
        fallback: 번역 실패시 대체 텍스트
        
    Returns:
        번역된 텍스트
    """
    try:
        manager = get_language_manager()
        result = manager.get_translated_text(text)
        return result if result != text else (fallback or text)
    except Exception as e:
        print(f"번역 함수 오류: {e}")
        return fallback or text

def set_language(language_code: str) -> bool:
    """언어 설정 변경 (전역 함수)"""
    return get_language_manager().set_language(language_code)

def get_current_language() -> str:
    """현재 언어 코드 반환 (전역 함수)"""
    return get_language_manager().get_current_language() 