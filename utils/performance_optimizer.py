"""
성능 최적화 모듈
캐시 전략, 쿼리 최적화, 로딩 성능 개선을 위한 시스템
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
import hashlib
import json
from functools import wraps
from utils.supabase_client import get_supabase_client


class CacheManager:
    """통합 캐시 관리 클래스"""
    
    def __init__(self):
        self.cache_prefix = "qc_cache_"
        self.default_ttl = 300  # 5분 기본 TTL
        self.max_cache_size = 100  # 최대 캐시 항목 수
        
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """캐시 키 생성"""
        # 함수명과 인수를 기반으로 고유한 캐시 키 생성
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return self.cache_prefix + hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        cache_data = st.session_state.get(key)
        if cache_data is None:
            return None
        
        # TTL 확인
        if time.time() > cache_data['expires_at']:
            self.delete(key)
            return None
        
        # 조회수 업데이트
        cache_data['hits'] += 1
        cache_data['last_accessed'] = time.time()
        st.session_state[key] = cache_data
        
        return cache_data['data']
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """캐시에 데이터 저장"""
        if ttl is None:
            ttl = self.default_ttl
        
        # 캐시 크기 제한 확인
        self._cleanup_cache()
        
        cache_data = {
            'data': data,
            'created_at': time.time(),
            'expires_at': time.time() + ttl,
            'last_accessed': time.time(),
            'hits': 0,
            'size': len(str(data)) if isinstance(data, (str, list, dict)) else 1
        }
        
        st.session_state[key] = cache_data
    
    def delete(self, key: str) -> None:
        """캐시에서 데이터 삭제"""
        if key in st.session_state:
            del st.session_state[key]
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """캐시 정리"""
        cleared_count = 0
        keys_to_delete = []
        
        for key in st.session_state.keys():
            if key.startswith(self.cache_prefix):
                if pattern is None or pattern in key:
                    keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del st.session_state[key]
            cleared_count += 1
        
        return cleared_count
    
    def _cleanup_cache(self) -> None:
        """캐시 정리 (크기 제한 및 만료된 항목 제거)"""
        cache_keys = [k for k in st.session_state.keys() if k.startswith(self.cache_prefix)]
        
        # 만료된 항목 제거
        current_time = time.time()
        for key in cache_keys[:]:
            cache_data = st.session_state.get(key)
            if cache_data and current_time > cache_data['expires_at']:
                del st.session_state[key]
                cache_keys.remove(key)
        
        # 크기 제한 확인
        if len(cache_keys) >= self.max_cache_size:
            # 가장 오래된 항목부터 제거 (LRU 방식)
            cache_items = []
            for key in cache_keys:
                cache_data = st.session_state.get(key)
                if cache_data:
                    cache_items.append((key, cache_data['last_accessed']))
            
            # 마지막 접근 시간으로 정렬
            cache_items.sort(key=lambda x: x[1])
            
            # 초과분 제거
            excess_count = len(cache_items) - self.max_cache_size + 10  # 여유분 확보
            for i in range(excess_count):
                if i < len(cache_items):
                    del st.session_state[cache_items[i][0]]
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        cache_keys = [k for k in st.session_state.keys() if k.startswith(self.cache_prefix)]
        
        total_items = len(cache_keys)
        total_hits = 0
        total_size = 0
        expired_count = 0
        current_time = time.time()
        
        for key in cache_keys:
            cache_data = st.session_state.get(key)
            if cache_data:
                total_hits += cache_data['hits']
                total_size += cache_data.get('size', 1)
                if current_time > cache_data['expires_at']:
                    expired_count += 1
        
        return {
            'total_items': total_items,
            'total_hits': total_hits,
            'total_size': total_size,
            'expired_count': expired_count,
            'hit_rate': (total_hits / max(total_items, 1)) * 100
        }


# 글로벌 캐시 매니저 인스턴스
cache_manager = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """캐시 데코레이터"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            func_name = f"{key_prefix}{func.__name__}" if key_prefix else func.__name__
            cache_key = cache_manager._generate_cache_key(func_name, args, kwargs)
            
            # 캐시에서 조회
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 캐시 미스 시 함수 실행
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 결과를 캐시에 저장
            cache_manager.set(cache_key, result, ttl)
            
            # 성능 로그 기록 (선택적)
            if execution_time > 1.0:  # 1초 이상 걸린 경우
                st.session_state.setdefault('slow_queries', []).append({
                    'function': func_name,
                    'execution_time': execution_time,
                    'timestamp': datetime.now()
                })
            
            return result
        return wrapper
    return decorator


class QueryOptimizer:
    """쿼리 최적화 클래스"""
    
    def __init__(self):
        self.query_stats = {}
    
    @cached(ttl=600, key_prefix="optimized_")
    def get_dashboard_data(self):
        """대시보드용 최적화된 데이터 조회"""
        try:
            supabase = get_supabase_client()
            
            # 병렬 처리를 위한 쿼리 배치
            queries = {
                'inspections': supabase.table('inspection_data').select('id, result, total_inspected, defect_quantity').order('created_at', desc=True).limit(100),
                'inspectors': supabase.table('inspectors').select('id, name, employee_id').eq('is_active', True),
                'models': supabase.table('production_models').select('id, model_name, model_no').eq('is_active', True),
                'recent_activity': supabase.table('inspection_data').select('inspection_date, result, inspectors(name)').order('created_at', desc=True).limit(10)
            }
            
            # 쿼리 실행
            results = {}
            for key, query in queries.items():
                try:
                    results[key] = query.execute().data or []
                except Exception as e:
                    results[key] = []
                    st.warning(f"쿼리 '{key}' 실행 실패: {str(e)}")
            
            return results
            
        except Exception as e:
            st.error(f"대시보드 데이터 조회 실패: {str(e)}")
            return {}
    
    @cached(ttl=300, key_prefix="kpi_")
    def get_optimized_kpi_data(self):
        """최적화된 KPI 데이터 조회"""
        try:
            supabase = get_supabase_client()
            
            # 최근 30일 데이터만 조회 (성능 최적화)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # 필요한 컬럼만 선택
            result = supabase.table('inspection_data') \
                .select('result, total_inspected, defect_quantity, pass_quantity') \
                .gte('inspection_date', thirty_days_ago) \
                .execute()
            
            inspections = result.data if result.data else []
            
            # 메모리에서 계산 (DB 집계 함수 대신)
            total_inspections = len(inspections)
            pass_count = sum(1 for i in inspections if i.get('result') == '합격')
            total_inspected_qty = sum(i.get('total_inspected', 0) for i in inspections)
            total_defect_qty = sum(i.get('defect_quantity', 0) for i in inspections)
            total_pass_qty = sum(i.get('pass_quantity', 0) for i in inspections)
            
            # KPI 계산
            defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
            inspection_efficiency = (pass_count / total_inspections * 100) if total_inspections > 0 else 0.0
            quantity_pass_rate = (total_pass_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
            
            return {
                'defect_rate': round(defect_rate, 3),
                'inspection_efficiency': round(inspection_efficiency, 1),
                'quantity_pass_rate': round(quantity_pass_rate, 1),
                'total_inspections': total_inspections,
                'pass_count': pass_count,
                'total_inspected_qty': total_inspected_qty,
                'total_defect_qty': total_defect_qty,
                'total_pass_qty': total_pass_qty,
                'data_status': 'success'
            }
            
        except Exception as e:
            return {
                'defect_rate': 0.0,
                'inspection_efficiency': 0.0,
                'quantity_pass_rate': 0.0,
                'total_inspections': 0,
                'pass_count': 0,
                'data_status': 'error',
                'error_message': str(e)
            }
    
    @cached(ttl=1800, key_prefix="inspector_perf_")  # 30분 캐시
    def get_optimized_inspector_performance(self):
        """최적화된 검사자 성과 데이터"""
        try:
            supabase = get_supabase_client()
            
            # 조인 쿼리 최적화 - 필요한 데이터만 조회
            result = supabase.table('inspection_data') \
                .select('inspector_id, result, total_inspected, defect_quantity, inspectors(name, employee_id)') \
                .execute()
            
            inspections = result.data if result.data else []
            
            # 메모리에서 집계 (더 빠름)
            inspector_stats = {}
            
            for inspection in inspections:
                inspector_id = inspection.get('inspector_id')
                if not inspector_id:
                    continue
                
                if inspector_id not in inspector_stats:
                    inspector_data = inspection.get('inspectors', {})
                    inspector_stats[inspector_id] = {
                        'name': inspector_data.get('name', 'Unknown') if inspector_data else 'Unknown',
                        'employee_id': inspector_data.get('employee_id', 'N/A') if inspector_data else 'N/A',
                        'total_inspections': 0,
                        'pass_count': 0,
                        'total_inspected_qty': 0,
                        'total_defect_qty': 0
                    }
                
                stats = inspector_stats[inspector_id]
                stats['total_inspections'] += 1
                
                if inspection.get('result') == '합격':
                    stats['pass_count'] += 1
                
                inspected_qty = inspection.get('total_inspected', 0)
                defect_qty = inspection.get('defect_quantity', 0)
                
                stats['total_inspected_qty'] += inspected_qty
                stats['total_defect_qty'] += defect_qty
            
            # 성과 계산
            performance_data = []
            for inspector_id, stats in inspector_stats.items():
                if stats['total_inspections'] > 0:
                    pass_rate = (stats['pass_count'] / stats['total_inspections']) * 100
                    defect_rate = (stats['total_defect_qty'] / stats['total_inspected_qty'] * 100) if stats['total_inspected_qty'] > 0 else 0
                    
                    performance_data.append({
                        'name': stats['name'],
                        'employee_id': stats['employee_id'],
                        'total_inspections': stats['total_inspections'],
                        'pass_rate': round(pass_rate, 1),
                        'defect_rate': round(defect_rate, 2)
                    })
            
            # 합격률 기준 정렬
            performance_data.sort(key=lambda x: x['pass_rate'], reverse=True)
            
            return performance_data
            
        except Exception as e:
            st.error(f"검사자 성과 데이터 조회 실패: {str(e)}")
            return []


class LoadingOptimizer:
    """로딩 성능 최적화 클래스"""
    
    def __init__(self):
        self.loading_times = {}
    
    def show_loading_spinner(self, message: str = "데이터를 로딩중입니다..."):
        """최적화된 로딩 스피너"""
        return st.spinner(message)
    
    def show_progress_bar(self, total_steps: int, current_step: int, message: str = ""):
        """진행률 표시"""
        progress = current_step / total_steps
        st.progress(progress)
        if message:
            st.text(f"{message} ({current_step}/{total_steps})")
    
    def lazy_load_data(self, data_loader: Callable, container_key: str):
        """지연 로딩"""
        if container_key not in st.session_state:
            with self.show_loading_spinner("데이터 로딩 중..."):
                st.session_state[container_key] = data_loader()
        
        return st.session_state[container_key]
    
    def paginate_data(self, data: list, page_size: int = 20, page_key: str = "page"):
        """데이터 페이지네이션"""
        if not data:
            return [], 0, 0, 0
        
        # 현재 페이지 번호
        current_page = st.session_state.get(page_key, 1)
        total_pages = (len(data) + page_size - 1) // page_size
        
        # 페이지 범위 계산
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, len(data))
        
        # 페이지네이션 컨트롤
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("◀ 이전", disabled=(current_page <= 1), key=f"{page_key}_prev"):
                st.session_state[page_key] = current_page - 1
                st.rerun()
        
        with col2:
            st.write(f"페이지 {current_page} / {total_pages} (총 {len(data)}개 항목)")
        
        with col3:
            if st.button("다음 ▶", disabled=(current_page >= total_pages), key=f"{page_key}_next"):
                st.session_state[page_key] = current_page + 1
                st.rerun()
        
        return data[start_idx:end_idx], current_page, total_pages, len(data)


def show_performance_dashboard():
    """성능 대시보드 표시"""
    st.subheader("⚡ 성능 모니터링 대시보드")
    
    # 캐시 통계
    cache_stats = cache_manager.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("캐시 항목", f"{cache_stats['total_items']}개")
    
    with col2:
        st.metric("캐시 히트", f"{cache_stats['total_hits']}회")
    
    with col3:
        st.metric("히트율", f"{cache_stats['hit_rate']:.1f}%")
    
    with col4:
        st.metric("만료 항목", f"{cache_stats['expired_count']}개")
    
    # 캐시 관리 버튼들
    st.write("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 만료된 캐시 정리", use_container_width=True):
            cache_manager._cleanup_cache()
            st.success("만료된 캐시가 정리되었습니다.")
            st.rerun()
    
    with col2:
        if st.button("🔄 전체 캐시 초기화", use_container_width=True):
            cleared_count = cache_manager.clear()
            st.success(f"{cleared_count}개 캐시 항목이 삭제되었습니다.")
            st.rerun()
    
    with col3:
        if st.button("📊 성능 테스트", use_container_width=True):
            run_performance_benchmark()
    
    # 느린 쿼리 모니터링
    slow_queries = st.session_state.get('slow_queries', [])
    if slow_queries:
        st.write("### 🐌 느린 쿼리 (1초 이상)")
        
        # 최근 10개만 표시
        recent_slow_queries = slow_queries[-10:]
        for query in reversed(recent_slow_queries):
            st.write(f"- **{query['function']}**: {query['execution_time']:.2f}초 ({query['timestamp'].strftime('%H:%M:%S')})")
        
        if st.button("느린 쿼리 기록 초기화"):
            st.session_state['slow_queries'] = []
            st.rerun()


def run_performance_benchmark():
    """성능 벤치마크 실행"""
    st.write("### 🚀 성능 벤치마크 실행")
    
    optimizer = QueryOptimizer()
    
    # 벤치마크 테스트들
    tests = [
        ("대시보드 데이터", optimizer.get_dashboard_data),
        ("KPI 데이터", optimizer.get_optimized_kpi_data),
        ("검사자 성과", optimizer.get_optimized_inspector_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        st.write(f"🔄 {test_name} 테스트 중...")
        
        # 캐시 없이 실행 (첫 번째)
        cache_key = cache_manager._generate_cache_key(test_func.__name__, (), {})
        cache_manager.delete(cache_key)
        
        start_time = time.time()
        test_func()
        cold_time = time.time() - start_time
        
        # 캐시 있이 실행 (두 번째)
        start_time = time.time()
        test_func()
        warm_time = time.time() - start_time
        
        results.append({
            'test': test_name,
            'cold_time': cold_time,
            'warm_time': warm_time,
            'improvement': ((cold_time - warm_time) / cold_time * 100) if cold_time > 0 else 0
        })
    
    # 결과 표시
    st.write("### 📊 벤치마크 결과")
    
    for result in results:
        st.write(f"**{result['test']}**:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("캐시 없음", f"{result['cold_time']:.3f}초")
        with col2:
            st.metric("캐시 있음", f"{result['warm_time']:.3f}초")
        with col3:
            st.metric("개선율", f"{result['improvement']:.1f}%")
        st.write("---")


# 글로벌 최적화 인스턴스
query_optimizer = QueryOptimizer()
loading_optimizer = LoadingOptimizer()


if __name__ == "__main__":
    show_performance_dashboard() 