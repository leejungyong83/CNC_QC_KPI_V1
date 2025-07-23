"""
성능 모니터링 페이지
시스템 성능 분석, 캐시 관리, 최적화 도구 제공
"""

import streamlit as st
from utils.performance_optimizer import show_performance_dashboard, cache_manager, loading_optimizer
import pandas as pd
from datetime import datetime, timedelta
import time

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)


def show_performance():
    """성능 모니터링 페이지 표시"""
    st.title("⚡ 성능 모니터링")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 성능 대시보드", "🧹 캐시 관리", "📈 성능 분석", "🛠️ 최적화 도구"])
    
    with tab1:
        show_performance_dashboard()
    
    with tab2:
        show_cache_management()
    
    with tab3:
        show_performance_analysis()
    
    with tab4:
        show_optimization_tools()


def show_cache_management():
    """캐시 관리 세부 기능"""
    st.subheader("🧹 캐시 관리")
    
    # 캐시 상세 통계
    cache_stats = cache_manager.get_stats()
    
    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "캐시 항목 수", 
            f"{cache_stats['total_items']}개",
            delta=f"최대 {cache_manager.max_cache_size}개"
        )
    
    with col2:
        st.metric(
            "총 히트 수", 
            f"{cache_stats['total_hits']}회",
            delta="누적 조회"
        )
    
    with col3:
        hit_rate = cache_stats['hit_rate']
        st.metric(
            "캐시 히트율", 
            f"{hit_rate:.1f}%",
            delta="효율성" if hit_rate > 70 else "개선 필요"
        )
    
    with col4:
        st.metric(
            "만료 항목", 
            f"{cache_stats['expired_count']}개",
            delta="정리 필요" if cache_stats['expired_count'] > 0 else "정상"
        )
    
    # 캐시 설정
    st.write("---")
    st.write("### ⚙️ 캐시 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_ttl = st.slider(
            "기본 TTL (초)", 
            min_value=60, 
            max_value=3600, 
            value=cache_manager.default_ttl,
            help="캐시 항목의 기본 생존 시간"
        )
        
        if st.button("TTL 업데이트", use_container_width=True):
            cache_manager.default_ttl = new_ttl
            st.success(f"기본 TTL이 {new_ttl}초로 업데이트되었습니다.")
    
    with col2:
        new_size = st.slider(
            "최대 캐시 크기", 
            min_value=50, 
            max_value=500, 
            value=cache_manager.max_cache_size,
            help="메모리에 보관할 최대 캐시 항목 수"
        )
        
        if st.button("크기 업데이트", use_container_width=True):
            cache_manager.max_cache_size = new_size
            st.success(f"최대 캐시 크기가 {new_size}개로 업데이트되었습니다.")
    
    # 캐시 상세 정보
    st.write("---")
    st.write("### 📋 캐시 상세 정보")
    
    cache_keys = [k for k in st.session_state.keys() if k.startswith(cache_manager.cache_prefix)]
    
    if cache_keys:
        cache_details = []
        current_time = time.time()
        
        for key in cache_keys:
            cache_data = st.session_state.get(key)
            if cache_data:
                age = current_time - cache_data['created_at']
                remaining_ttl = cache_data['expires_at'] - current_time
                
                # 베트남 시간대로 변환하여 표시
                created_at_vietnam = convert_utc_to_vietnam(datetime.fromtimestamp(cache_data['created_at']))
                
                cache_details.append({
                    '캐시 키': key.replace(cache_manager.cache_prefix, ''),
                    '생성 시간': created_at_vietnam.strftime('%H:%M:%S'),
                    '조회 횟수': cache_data['hits'],
                    '나이 (초)': f"{age:.0f}",
                    '남은 TTL (초)': f"{remaining_ttl:.0f}" if remaining_ttl > 0 else "만료됨",
                    '크기': cache_data.get('size', 1),
                    '상태': "활성" if remaining_ttl > 0 else "만료"
                })
        
        if cache_details:
            df = pd.DataFrame(cache_details)
            st.dataframe(df, use_container_width=True)
        
        # 개별 캐시 삭제
        selected_cache = st.selectbox(
            "삭제할 캐시 선택",
            options=[""] + [detail['캐시 키'] for detail in cache_details],
            help="특정 캐시 항목을 삭제할 수 있습니다"
        )
        
        if selected_cache and st.button(f"'{selected_cache}' 삭제"):
            full_key = cache_manager.cache_prefix + selected_cache
            cache_manager.delete(full_key)
            st.success(f"캐시 항목 '{selected_cache}'이 삭제되었습니다.")
            st.rerun()
    else:
        st.info("현재 활성 캐시가 없습니다.")


def show_performance_analysis():
    """성능 분석"""
    st.subheader("📈 성능 분석")
    
    # 느린 쿼리 분석
    slow_queries = st.session_state.get('slow_queries', [])
    
    if slow_queries:
        st.write("### 🐌 느린 쿼리 분석")
        
        # 시간별 분석 (베트남 시간대 기준)
        if len(slow_queries) > 1:
            # 최근 24시간 내 데이터만
            vietnam_now = get_vietnam_display_time()
            recent_queries = [
                q for q in slow_queries 
                if (vietnam_now - q['timestamp']).total_seconds() < 86400
            ]
            
            if recent_queries:
                # 함수별 평균 실행 시간
                func_stats = {}
                for query in recent_queries:
                    func_name = query['function']
                    if func_name not in func_stats:
                        func_stats[func_name] = {'times': [], 'count': 0}
                    func_stats[func_name]['times'].append(query['execution_time'])
                    func_stats[func_name]['count'] += 1
                
                # 통계 계산
                func_analysis = []
                for func_name, stats in func_stats.items():
                    times = stats['times']
                    func_analysis.append({
                        '함수': func_name,
                        '호출 횟수': stats['count'],
                        '평균 시간 (초)': f"{sum(times) / len(times):.3f}",
                        '최대 시간 (초)': f"{max(times):.3f}",
                        '최소 시간 (초)': f"{min(times):.3f}"
                    })
                
                # 평균 시간으로 정렬
                func_analysis.sort(key=lambda x: float(x['평균 시간 (초)']), reverse=True)
                
                df = pd.DataFrame(func_analysis)
                st.dataframe(df, use_container_width=True)
                
                # 시간별 추이 (간단한 차트)
                st.write("### 📊 최근 성능 추이")
                
                # 최근 10개 쿼리의 시간 추이
                recent_10 = recent_queries[-10:] if len(recent_queries) >= 10 else recent_queries
                
                chart_data = pd.DataFrame([
                    {
                        'Time': q['timestamp'].strftime('%H:%M:%S'),
                        'Execution Time': q['execution_time'],
                        'Function': q['function']
                    }
                    for q in recent_10
                ])
                
                if not chart_data.empty:
                    st.line_chart(chart_data.set_index('Time')['Execution Time'])
        
        # 성능 개선 제안
        st.write("### 💡 성능 개선 제안")
        
        # 가장 느린 함수 분석
        if func_analysis:
            slowest_func = func_analysis[0]
            st.warning(f"**가장 느린 함수**: {slowest_func['함수']} (평균 {slowest_func['평균 시간 (초)']}초)")
            
            # 개선 제안
            suggestions = get_performance_suggestions(slowest_func['함수'])
            for suggestion in suggestions:
                st.write(f"- {suggestion}")
    
    else:
        st.info("느린 쿼리 기록이 없습니다. (1초 이상 걸리는 쿼리만 기록됩니다)")
    
    # 시스템 리소스 모니터링 (근사치)
    st.write("---")
    st.write("### 💻 시스템 리소스")
    
    # 세션 상태 크기 계산
    session_size = len(str(st.session_state))
    cache_count = len([k for k in st.session_state.keys() if k.startswith(cache_manager.cache_prefix)])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("세션 데이터 크기", f"{session_size:,} chars")
    
    with col2:
        st.metric("캐시 항목 수", f"{cache_count}개")
    
    with col3:
        memory_usage = "정상" if session_size < 100000 else "주의"
        st.metric("메모리 사용량", memory_usage)


def show_optimization_tools():
    """최적화 도구"""
    st.subheader("🛠️ 최적화 도구")
    
    # 자동 최적화 설정
    st.write("### ⚙️ 자동 최적화 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        auto_cache_cleanup = st.checkbox(
            "자동 캐시 정리", 
            value=st.session_state.get('auto_cache_cleanup', False),
            help="만료된 캐시를 자동으로 정리합니다"
        )
        st.session_state.auto_cache_cleanup = auto_cache_cleanup
        
        if auto_cache_cleanup:
            cleanup_interval = st.slider(
                "정리 간격 (분)", 
                min_value=5, 
                max_value=60, 
                value=st.session_state.get('cleanup_interval', 15)
            )
            st.session_state.cleanup_interval = cleanup_interval
    
    with col2:
        preload_data = st.checkbox(
            "데이터 프리로딩", 
            value=st.session_state.get('preload_data', False),
            help="자주 사용하는 데이터를 미리 로딩합니다"
        )
        st.session_state.preload_data = preload_data
    
    # 수동 최적화 도구
    st.write("---")
    st.write("### 🔧 수동 최적화 도구")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 전체 시스템 최적화", use_container_width=True):
            optimize_system()
    
    with col2:
        if st.button("🧹 메모리 정리", use_container_width=True):
            cleanup_memory()
    
    with col3:
        if st.button("📊 성능 프로파일링", use_container_width=True):
            run_performance_profiling()
    
    # 데이터 프리로딩
    if preload_data:
        st.write("---")
        st.write("### 📦 데이터 프리로딩")
        
        preload_options = st.multiselect(
            "프리로딩할 데이터 선택",
            options=[
                "KPI 데이터",
                "검사자 성과",
                "대시보드 데이터",
                "최근 검사 실적"
            ],
            default=st.session_state.get('preload_options', ["KPI 데이터"])
        )
        st.session_state.preload_options = preload_options
        
        if st.button("🔄 선택한 데이터 프리로딩"):
            preload_selected_data(preload_options)
    
    # 성능 벤치마크 기록
    benchmark_history = st.session_state.get('benchmark_history', [])
    if benchmark_history:
        st.write("---")
        st.write("### 📈 벤치마크 히스토리")
        
        # 최근 5개 벤치마크 결과
        recent_benchmarks = benchmark_history[-5:]
        
        for i, benchmark in enumerate(reversed(recent_benchmarks), 1):
            with st.expander(f"벤치마크 #{len(benchmark_history) - i + 1} - {benchmark['timestamp']}"):
                for test_name, result in benchmark['results'].items():
                    st.write(f"**{test_name}**: {result['improvement']:.1f}% 개선")


def get_performance_suggestions(func_name: str) -> list:
    """함수별 성능 개선 제안"""
    suggestions = {
        'get_optimized_kpi_data': [
            "KPI 데이터의 캐시 TTL을 늘려보세요 (현재 5분)",
            "필요한 컬럼만 선택하여 쿼리하고 있는지 확인하세요",
            "최근 30일 데이터로 제한하여 조회량을 줄이세요"
        ],
        'get_optimized_inspector_performance': [
            "검사자 성과 데이터의 캐시 TTL을 늘려보세요 (현재 30분)",
            "조인 쿼리 대신 별도 조회 후 메모리에서 결합을 고려하세요",
            "인덱스가 inspector_id에 설정되어 있는지 확인하세요"
        ],
        'get_dashboard_data': [
            "대시보드 데이터를 페이지네이션으로 나누어 로딩하세요",
            "병렬 쿼리 실행을 고려해보세요",
            "자주 변경되지 않는 데이터는 더 오래 캐시하세요"
        ]
    }
    
    return suggestions.get(func_name, [
        "함수 실행 시간을 줄이기 위해 캐시를 활용하세요",
        "불필요한 데이터 조회를 최소화하세요",
        "복잡한 연산은 메모리에서 수행하세요"
    ])


def optimize_system():
    """전체 시스템 최적화"""
    with st.spinner("시스템 최적화 진행 중..."):
        # 1. 만료된 캐시 정리
        cleaned_count = 0
        cache_keys = [k for k in st.session_state.keys() if k.startswith(cache_manager.cache_prefix)]
        current_time = time.time()
        
        for key in cache_keys:
            cache_data = st.session_state.get(key)
            if cache_data and current_time > cache_data['expires_at']:
                del st.session_state[key]
                cleaned_count += 1
        
        # 2. 느린 쿼리 기록 정리 (100개 이상 시)
        slow_queries = st.session_state.get('slow_queries', [])
        if len(slow_queries) > 100:
            st.session_state['slow_queries'] = slow_queries[-50:]  # 최근 50개만 유지
        
        # 3. 벤치마크 기록 정리 (20개 이상 시)
        benchmark_history = st.session_state.get('benchmark_history', [])
        if len(benchmark_history) > 20:
            st.session_state['benchmark_history'] = benchmark_history[-10:]  # 최근 10개만 유지
        
        time.sleep(1)  # 시각적 효과
    
    st.success(f"✅ 시스템 최적화 완료! (만료된 캐시 {cleaned_count}개 정리)")


def cleanup_memory():
    """메모리 정리"""
    with st.spinner("메모리 정리 중..."):
        # 임시 데이터 정리
        temp_keys = [k for k in st.session_state.keys() if k.startswith('temp_') or k.startswith('tmp_')]
        for key in temp_keys:
            del st.session_state[key]
        
        # 캐시 정리
        cache_manager._cleanup_cache()
        
        time.sleep(0.5)
    
    st.success("✅ 메모리 정리 완료!")


def run_performance_profiling():
    """성능 프로파일링 실행"""
    st.write("### 🔍 성능 프로파일링 결과")
    
    with st.spinner("성능 프로파일링 진행 중..."):
        # 각종 성능 테스트
        tests = [
            ("세션 상태 접근", lambda: len(st.session_state)),
            ("캐시 통계 계산", lambda: cache_manager.get_stats()),
            ("현재 시간 조회", lambda: datetime.now()),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            times = []
            
            # 각 테스트를 5번 실행하여 평균 계산
            for _ in range(5):
                start_time = time.time()
                test_func()
                elapsed = time.time() - start_time
                times.append(elapsed * 1000)  # 밀리초 변환
            
            avg_time = sum(times) / len(times)
            results.append({
                '테스트': test_name,
                '평균 시간 (ms)': f"{avg_time:.3f}",
                '최대 시간 (ms)': f"{max(times):.3f}",
                '최소 시간 (ms)': f"{min(times):.3f}"
            })
        
        time.sleep(0.5)
    
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)


def preload_selected_data(options: list):
    """선택한 데이터 프리로딩"""
    with st.spinner("데이터 프리로딩 중..."):
        from utils.performance_optimizer import query_optimizer
        
        for option in options:
            if option == "KPI 데이터":
                query_optimizer.get_optimized_kpi_data()
            elif option == "검사자 성과":
                query_optimizer.get_optimized_inspector_performance()
            elif option == "대시보드 데이터":
                query_optimizer.get_dashboard_data()
            
            time.sleep(0.2)  # 시각적 효과
    
    st.success(f"✅ 선택한 {len(options)}개 데이터 프리로딩 완료!")


if __name__ == "__main__":
    show_performance() 