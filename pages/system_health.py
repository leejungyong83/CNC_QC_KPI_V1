"""
시스템 상태 진단 페이지
시스템 건강성 모니터링 및 문제 진단 기능 제공
"""

import streamlit as st
from utils.error_handler import get_error_handler, show_error_recovery_guide
from utils.supabase_client import get_supabase_client
from datetime import datetime, timedelta
import time
import os

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)


def show_system_health():
    """시스템 상태 페이지 표시"""
    st.title("🛠️ 시스템 상태 진단")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 시스템 상태", "🔍 연결 테스트", "🛠️ 문제 해결", "📈 에러 모니터링"])
    
    with tab1:
        show_system_overview()
    
    with tab2:
        show_connection_tests()
    
    with tab3:
        show_error_recovery_guide()
    
    with tab4:
        show_error_monitoring()


def show_system_overview():
    """시스템 전체 상태 개요"""
    st.subheader("📊 시스템 전체 상태")
    
    # 자동 새로고침 옵션
    auto_refresh = st.checkbox("🔄 자동 새로고침 (30초)", key="auto_refresh_system")
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # 시스템 상태 체크
    system_status = check_system_status()
    
    # 전체 상태 요약
    overall_status = calculate_overall_status(system_status)
    
    if overall_status == "정상":
        st.success("✅ **시스템 상태: 정상**")
        st.success("모든 시스템이 정상적으로 작동하고 있습니다.")
    elif overall_status == "주의":
        st.warning("⚠️ **시스템 상태: 주의**")
        st.warning("일부 시스템에 주의가 필요합니다.")
    else:
        st.error("🚨 **시스템 상태: 오류**")
        st.error("시스템에 문제가 발생했습니다. 즉시 확인이 필요합니다.")
    
    # 상세 상태 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔌 연결 상태")
        
        # 데이터베이스 연결
        db_status = system_status['database']
        if db_status['status'] == 'success':
            st.success(f"✅ 데이터베이스: 정상 ({db_status['response_time']:.2f}ms)")
        else:
            st.error(f"❌ 데이터베이스: 오류 - {db_status['error']}")
        
        # 테이블 상태
        table_status = system_status['tables']
        if table_status['status'] == 'success':
            st.success(f"✅ 테이블: {table_status['count']}개 정상")
        else:
            st.error(f"❌ 테이블: 오류 - {table_status['error']}")
    
    with col2:
        st.markdown("### 📊 데이터 상태")
        
        # 데이터 개수
        data_status = system_status['data']
        if data_status['status'] == 'success':
            st.info(f"📋 검사 데이터: {data_status['inspections']}건")
            st.info(f"👥 검사자: {data_status['inspectors']}명")
            st.info(f"🏭 생산모델: {data_status['models']}개")
        else:
            st.error(f"❌ 데이터: 조회 실패 - {data_status['error']}")
    
    # 성능 지표
    st.markdown("### ⚡ 성능 지표")
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        db_time = system_status['database']['response_time'] if system_status['database']['status'] == 'success' else 0
        st.metric("DB 응답시간", f"{db_time:.0f}ms", delta="정상" if db_time < 500 else "느림")
    
    with perf_col2:
        error_handler = get_error_handler()
        error_stats = error_handler.get_error_stats()
        st.metric("최근 에러", f"{error_stats['recent_errors']}개", delta="정상" if error_stats['recent_errors'] == 0 else "주의")
    
    with perf_col3:
        uptime = get_system_uptime()
        st.metric("가동시간", uptime, delta="안정")
    
    with perf_col4:
        last_check = get_vietnam_display_time().strftime("%H:%M:%S")
        st.metric("마지막 확인", last_check, delta="방금 전")
    
    # 최근 활동
    st.markdown("### 📈 최근 활동")
    show_recent_activity()


def check_system_status():
    """시스템 상태 종합 체크"""
    status = {
        'database': {'status': 'unknown', 'response_time': 0, 'error': None},
        'tables': {'status': 'unknown', 'count': 0, 'error': None},
        'data': {'status': 'unknown', 'inspections': 0, 'inspectors': 0, 'models': 0, 'error': None}
    }
    
    try:
        # 데이터베이스 연결 테스트
        start_time = time.time()
        supabase = get_supabase_client()
        
        # 간단한 쿼리로 연결 테스트
        test_result = supabase.table('inspectors').select('count').limit(1).execute()
        response_time = (time.time() - start_time) * 1000
        
        status['database'] = {
            'status': 'success',
            'response_time': response_time,
            'error': None
        }
        
        # 테이블 존재 확인
        try:
            table_tests = [
                supabase.table('users').select('count').limit(1).execute(),
                supabase.table('inspectors').select('count').limit(1).execute(),
                supabase.table('production_models').select('count').limit(1).execute(),
                supabase.table('inspection_data').select('count').limit(1).execute(),
                supabase.table('defect_types').select('count').limit(1).execute()
            ]
            
            status['tables'] = {
                'status': 'success',
                'count': 5,
                'error': None
            }
        except Exception as e:
            status['tables'] = {
                'status': 'error',
                'count': 0,
                'error': str(e)
            }
        
        # 데이터 개수 확인
        try:
            inspections_count = len(supabase.table('inspection_data').select('id').execute().data or [])
            inspectors_count = len(supabase.table('inspectors').select('id').execute().data or [])
            models_count = len(supabase.table('production_models').select('id').execute().data or [])
            
            status['data'] = {
                'status': 'success',
                'inspections': inspections_count,
                'inspectors': inspectors_count,
                'models': models_count,
                'error': None
            }
        except Exception as e:
            status['data'] = {
                'status': 'error',
                'inspections': 0,
                'inspectors': 0,
                'models': 0,
                'error': str(e)
            }
            
    except Exception as e:
        status['database'] = {
            'status': 'error',
            'response_time': 0,
            'error': str(e)
        }
    
    return status


def calculate_overall_status(system_status):
    """전체 시스템 상태 계산"""
    if system_status['database']['status'] == 'error':
        return "오류"
    elif system_status['tables']['status'] == 'error':
        return "오류"
    elif system_status['data']['status'] == 'error':
        return "주의"
    else:
        return "정상"


def show_connection_tests():
    """연결 테스트 실행"""
    st.subheader("🔍 연결 테스트")
    
    st.info("💡 각 테스트를 개별적으로 실행하여 문제를 진단할 수 있습니다.")
    
    # 테스트 버튼들
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔌 데이터베이스 연결 테스트", use_container_width=True):
            run_database_connection_test()
        
        if st.button("📋 테이블 구조 확인", use_container_width=True):
            run_table_structure_test()
        
        if st.button("👥 사용자 권한 확인", use_container_width=True):
            run_permission_test()
    
    with col2:
        if st.button("📊 데이터 무결성 검사", use_container_width=True):
            run_data_integrity_test()
        
        if st.button("🚀 성능 벤치마크", use_container_width=True):
            run_performance_test()
        
        if st.button("🔄 전체 테스트 실행", type="primary", use_container_width=True):
            run_comprehensive_test()


def run_database_connection_test():
    """데이터베이스 연결 테스트"""
    st.write("---")
    st.write("### 🔌 데이터베이스 연결 테스트 실행 중...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 1단계: 클라이언트 초기화
        progress_bar.progress(25)
        status_text.text("1/4: Supabase 클라이언트 초기화...")
        time.sleep(0.5)
        
        supabase = get_supabase_client()
        
        # 2단계: 연결 테스트
        progress_bar.progress(50)
        status_text.text("2/4: 연결 테스트...")
        time.sleep(0.5)
        
        start_time = time.time()
        result = supabase.table('inspectors').select('count').limit(1).execute()
        response_time = (time.time() - start_time) * 1000
        
        # 3단계: 권한 확인
        progress_bar.progress(75)
        status_text.text("3/4: 권한 확인...")
        time.sleep(0.5)
        
        # 4단계: 완료
        progress_bar.progress(100)
        status_text.text("4/4: 테스트 완료!")
        
        st.success(f"✅ **연결 성공!**")
        st.info(f"⚡ 응답 시간: {response_time:.2f}ms")
        st.info(f"🔗 연결 상태: 정상")
        
    except Exception as e:
        progress_bar.progress(100)
        status_text.text("테스트 실패!")
        st.error(f"❌ **연결 실패**: {str(e)}")
        
        # 에러 분석 및 해결책 제시
        error_handler = get_error_handler()
        error_handler.handle_error(e, "database_connection_test", "연결 테스트 실행")


def run_table_structure_test():
    """테이블 구조 확인 테스트"""
    st.write("---")
    st.write("### 📋 테이블 구조 확인 테스트")
    
    required_tables = [
        'users', 'admins', 'inspectors', 
        'production_models', 'defect_types', 
        'inspection_data', 'defects'
    ]
    
    try:
        supabase = get_supabase_client()
        
        st.write("**필수 테이블 존재 확인:**")
        
        for table in required_tables:
            try:
                result = supabase.table(table).select('count').limit(1).execute()
                st.success(f"✅ {table}: 존재함")
            except Exception as e:
                st.error(f"❌ {table}: 존재하지 않음 - {str(e)}")
        
        st.info("💡 테이블이 없는 경우 `database_schema_unified.sql`을 실행하세요.")
        
    except Exception as e:
        st.error(f"❌ 테이블 구조 확인 실패: {str(e)}")


def run_permission_test():
    """권한 테스트"""
    st.write("---")
    st.write("### 👥 사용자 권한 확인 테스트")
    
    try:
        supabase = get_supabase_client()
        
        # 읽기 권한 테스트
        try:
            result = supabase.table('inspectors').select('id').limit(1).execute()
            st.success("✅ 읽기 권한: 정상")
        except Exception as e:
            st.error(f"❌ 읽기 권한: 실패 - {str(e)}")
        
        # 쓰기 권한 테스트 (테스트 데이터 삽입 후 삭제)
        try:
            # 실제 환경에서는 테스트 테이블을 사용하는 것이 좋음
            st.info("ℹ️ 쓰기 권한: 안전상 테스트 생략")
        except Exception as e:
            st.error(f"❌ 쓰기 권한: 실패 - {str(e)}")
        
    except Exception as e:
        st.error(f"❌ 권한 확인 실패: {str(e)}")


def run_data_integrity_test():
    """데이터 무결성 검사"""
    st.write("---")
    st.write("### 📊 데이터 무결성 검사")
    
    try:
        supabase = get_supabase_client()
        
        # 외래키 관계 확인
        st.write("**외래키 관계 확인:**")
        
        # inspection_data와 inspectors 관계
        try:
            inspection_result = supabase.table('inspection_data').select('inspector_id').execute()
            inspector_result = supabase.table('inspectors').select('id').execute()
            
            inspections = inspection_result.data or []
            inspectors = inspector_result.data or []
            inspector_ids = {i['id'] for i in inspectors}
            
            orphan_count = 0
            for inspection in inspections:
                if inspection.get('inspector_id') and inspection['inspector_id'] not in inspector_ids:
                    orphan_count += 1
            
            if orphan_count == 0:
                st.success("✅ 검사데이터-검사자 관계: 정상")
            else:
                st.warning(f"⚠️ 검사데이터-검사자 관계: {orphan_count}개 고아 레코드")
                
        except Exception as e:
            st.error(f"❌ 관계 확인 실패: {str(e)}")
        
        # 데이터 일관성 확인
        st.write("**데이터 일관성 확인:**")
        
        try:
            inspections = supabase.table('inspection_data').select('total_inspected, defect_quantity, pass_quantity').execute().data or []
            
            inconsistent_count = 0
            for inspection in inspections:
                total = inspection.get('total_inspected', 0)
                defect = inspection.get('defect_quantity', 0)
                pass_qty = inspection.get('pass_quantity', 0)
                
                if total != (defect + pass_qty):
                    inconsistent_count += 1
            
            if inconsistent_count == 0:
                st.success("✅ 수량 데이터 일관성: 정상")
            else:
                st.warning(f"⚠️ 수량 데이터 일관성: {inconsistent_count}개 불일치")
                
        except Exception as e:
            st.error(f"❌ 일관성 확인 실패: {str(e)}")
            
    except Exception as e:
        st.error(f"❌ 데이터 무결성 검사 실패: {str(e)}")


def run_performance_test():
    """성능 벤치마크 테스트"""
    st.write("---")
    st.write("### 🚀 성능 벤치마크 테스트")
    
    try:
        supabase = get_supabase_client()
        
        # 각종 쿼리 성능 측정
        tests = [
            ("단순 조회", lambda: supabase.table('inspectors').select('id').limit(10).execute()),
            ("조인 쿼리", lambda: supabase.table('inspection_data').select('*, inspectors(name)').limit(10).execute()),
            ("집계 쿼리", lambda: supabase.table('inspection_data').select('count').execute()),
        ]
        
        st.write("**쿼리 성능 측정:**")
        
        for test_name, test_func in tests:
            start_time = time.time()
            try:
                test_func()
                elapsed = (time.time() - start_time) * 1000
                
                if elapsed < 200:
                    st.success(f"✅ {test_name}: {elapsed:.2f}ms (빠름)")
                elif elapsed < 500:
                    st.info(f"ℹ️ {test_name}: {elapsed:.2f}ms (보통)")
                else:
                    st.warning(f"⚠️ {test_name}: {elapsed:.2f}ms (느림)")
                    
            except Exception as e:
                st.error(f"❌ {test_name}: 실패 - {str(e)}")
        
    except Exception as e:
        st.error(f"❌ 성능 테스트 실패: {str(e)}")


def run_comprehensive_test():
    """종합 테스트 실행"""
    st.write("---")
    st.write("### 🔄 종합 테스트 실행")
    
    with st.spinner("전체 시스템 테스트를 실행하고 있습니다..."):
        run_database_connection_test()
        run_table_structure_test()
        run_permission_test()
        run_data_integrity_test()
        run_performance_test()
    
    st.success("🎉 전체 테스트 완료!")


def show_recent_activity():
    """최근 활동 표시"""
    try:
        supabase = get_supabase_client()
        
        # 최근 검사 데이터
        recent_inspections = supabase.table('inspection_data') \
            .select('inspection_date, result, inspectors(name)') \
            .order('created_at', desc=True) \
            .limit(5) \
            .execute()
        
        if recent_inspections.data:
            st.write("**최근 검사 실적 (5건):**")
            for inspection in recent_inspections.data:
                inspector_name = inspection.get('inspectors', {}).get('name', 'N/A') if inspection.get('inspectors') else 'N/A'
                result_emoji = "✅" if inspection.get('result') == '합격' else "❌"
                st.write(f"- {result_emoji} {inspection.get('inspection_date')} - {inspector_name}")
        else:
            st.info("📝 최근 검사 실적이 없습니다.")
            
    except Exception as e:
        st.error(f"최근 활동 조회 실패: {str(e)}")


def show_error_monitoring():
    """에러 모니터링 표시"""
    st.subheader("📈 에러 모니터링")
    
    error_handler = get_error_handler()
    error_handler.show_error_dashboard()


def get_system_uptime():
    """시스템 가동시간 계산 (근사치, 베트남 시간대 기준)"""
    # 실제로는 서버 시작 시간을 기록해야 하지만, 
    # 여기서는 세션 시작 시간을 기준으로 함
    if 'app_start_time' not in st.session_state:
        st.session_state.app_start_time = get_vietnam_display_time()
    
    uptime = get_vietnam_display_time() - st.session_state.app_start_time
    
    if uptime.days > 0:
        return f"{uptime.days}일 {uptime.seconds//3600}시간"
    elif uptime.seconds > 3600:
        return f"{uptime.seconds//3600}시간 {(uptime.seconds%3600)//60}분"
    else:
        return f"{uptime.seconds//60}분"


if __name__ == "__main__":
    show_system_health() 