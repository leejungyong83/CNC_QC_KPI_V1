"""
고급 번역 캐싱 시스템
성능 최적화를 위한 다층 캐시 구조 및 압축 기능
"""

import json
import hashlib
import time
import gzip
import pickle
from typing import Dict, Any, Optional, Tuple, List
from functools import lru_cache
from collections import OrderedDict
import streamlit as st
import threading

class AdvancedTranslationCache:
    """고급 번역 캐싱 시스템"""
    
    def __init__(self, max_memory_size: int = 1000, max_disk_size: int = 10000):
        self.max_memory_size = max_memory_size
        self.max_disk_size = max_disk_size
        
        # 메모리 캐시 (LRU)
        self.memory_cache: OrderedDict = OrderedDict()
        
        # 디스크 캐시 (세션 기반)
        self.disk_cache_key = "advanced_translation_cache"
        
        # 통계 정보
        self.stats = {
            "memory_hits": 0,
            "disk_hits": 0,
            "api_calls": 0,
            "cache_saves": 0,
            "total_requests": 0,
            "avg_response_time": 0.0
        }
        
        # 스레드 안전성을 위한 락
        self._lock = threading.Lock()
        
        # 초기화시 디스크 캐시 로드
        self._load_disk_cache()
    
    def _generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """캐시 키 생성 (해시 기반)"""
        key_string = f"{text}|{source_lang}|{target_lang}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def _compress_data(self, data: Any) -> bytes:
        """데이터 압축"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            return gzip.compress(json_str.encode('utf-8'))
        except Exception:
            # JSON 직렬화 실패 시 pickle 사용
            return gzip.compress(pickle.dumps(data))
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """데이터 압축 해제"""
        try:
            decompressed = gzip.decompress(compressed_data)
            try:
                return json.loads(decompressed.decode('utf-8'))
            except json.JSONDecodeError:
                return pickle.loads(decompressed)
        except Exception:
            return None
    
    def _load_disk_cache(self):
        """디스크 캐시 로드 (세션 상태에서)"""
        try:
            if self.disk_cache_key in st.session_state:
                compressed_cache = st.session_state[self.disk_cache_key]
                disk_cache = self._decompress_data(compressed_cache)
                
                if disk_cache and isinstance(disk_cache, dict):
                    # 만료된 항목 제거
                    current_time = time.time()
                    valid_cache = {}
                    
                    for key, (data, timestamp, ttl) in disk_cache.items():
                        if current_time - timestamp < ttl:
                            valid_cache[key] = (data, timestamp, ttl)
                    
                    # 메모리 캐시에 일부 로드 (최신 항목 우선)
                    sorted_items = sorted(valid_cache.items(), 
                                        key=lambda x: x[1][1], reverse=True)
                    
                    for key, (data, timestamp, ttl) in sorted_items[:self.max_memory_size//2]:
                        self.memory_cache[key] = (data, timestamp, ttl)
                        
        except Exception as e:
            print(f"디스크 캐시 로드 실패: {e}")
    
    def _save_disk_cache(self):
        """디스크 캐시 저장 (세션 상태에)"""
        try:
            with self._lock:
                # 메모리 캐시와 기존 디스크 캐시 병합
                disk_cache = {}
                
                # 기존 디스크 캐시 로드
                if self.disk_cache_key in st.session_state:
                    try:
                        existing_cache = self._decompress_data(st.session_state[self.disk_cache_key])
                        if existing_cache:
                            disk_cache.update(existing_cache)
                    except Exception:
                        pass
                
                # 메모리 캐시 추가
                disk_cache.update(dict(self.memory_cache))
                
                # 크기 제한 적용
                if len(disk_cache) > self.max_disk_size:
                    # 가장 오래된 항목 제거
                    sorted_items = sorted(disk_cache.items(), 
                                        key=lambda x: x[1][1], reverse=True)
                    disk_cache = dict(sorted_items[:self.max_disk_size])
                
                # 압축하여 저장
                compressed_cache = self._compress_data(disk_cache)
                st.session_state[self.disk_cache_key] = compressed_cache
                
                self.stats["cache_saves"] += 1
                
        except Exception as e:
            print(f"디스크 캐시 저장 실패: {e}")
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """캐시에서 번역 조회"""
        start_time = time.time()
        cache_key = self._generate_cache_key(text, source_lang, target_lang)
        
        try:
            with self._lock:
                self.stats["total_requests"] += 1
                
                # 1. 메모리 캐시 확인
                if cache_key in self.memory_cache:
                    data, timestamp, ttl = self.memory_cache[cache_key]
                    
                    if time.time() - timestamp < ttl:
                        # LRU 업데이트
                        self.memory_cache.move_to_end(cache_key)
                        self.stats["memory_hits"] += 1
                        
                        response_time = time.time() - start_time
                        self._update_avg_response_time(response_time)
                        
                        return data
                    else:
                        # 만료된 항목 제거
                        del self.memory_cache[cache_key]
                
                # 2. 디스크 캐시 확인
                if self.disk_cache_key in st.session_state:
                    try:
                        disk_cache = self._decompress_data(st.session_state[self.disk_cache_key])
                        
                        if disk_cache and cache_key in disk_cache:
                            data, timestamp, ttl = disk_cache[cache_key]
                            
                            if time.time() - timestamp < ttl:
                                # 메모리 캐시로 승격
                                self._add_to_memory_cache(cache_key, data, timestamp, ttl)
                                self.stats["disk_hits"] += 1
                                
                                response_time = time.time() - start_time
                                self._update_avg_response_time(response_time)
                                
                                return data
                    except Exception:
                        pass
                
                return None
                
        except Exception as e:
            print(f"캐시 조회 오류: {e}")
            return None
    
    def set(self, text: str, source_lang: str, target_lang: str, 
            translation: str, ttl: int = 3600):
        """번역 결과를 캐시에 저장"""
        cache_key = self._generate_cache_key(text, source_lang, target_lang)
        timestamp = time.time()
        
        try:
            with self._lock:
                self._add_to_memory_cache(cache_key, translation, timestamp, ttl)
                
                # 주기적으로 디스크에 저장 (매 10번째마다)
                if self.stats["cache_saves"] % 10 == 0:
                    self._save_disk_cache()
                    
        except Exception as e:
            print(f"캐시 저장 오류: {e}")
    
    def _add_to_memory_cache(self, key: str, data: str, timestamp: float, ttl: int):
        """메모리 캐시에 추가 (LRU 관리)"""
        # 크기 제한 확인
        if len(self.memory_cache) >= self.max_memory_size:
            # 가장 오래된 항목 제거
            self.memory_cache.popitem(last=False)
        
        self.memory_cache[key] = (data, timestamp, ttl)
    
    def _update_avg_response_time(self, response_time: float):
        """평균 응답 시간 업데이트"""
        current_avg = self.stats["avg_response_time"]
        total_requests = self.stats["total_requests"]
        
        if total_requests == 1:
            self.stats["avg_response_time"] = response_time
        else:
            # 이동 평균 계산
            self.stats["avg_response_time"] = (current_avg * (total_requests - 1) + response_time) / total_requests
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_hits = self.stats["memory_hits"] + self.stats["disk_hits"]
        total_requests = self.stats["total_requests"]
        
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "memory_cache_size": len(self.memory_cache),
            "hit_rate": round(hit_rate, 2),
            "memory_hit_rate": round(self.stats["memory_hits"] / total_requests * 100, 2) if total_requests > 0 else 0,
            "disk_hit_rate": round(self.stats["disk_hits"] / total_requests * 100, 2) if total_requests > 0 else 0,
            "avg_response_time_ms": round(self.stats["avg_response_time"] * 1000, 2)
        }
    
    def clear_cache(self, cache_type: str = "all"):
        """캐시 삭제"""
        try:
            with self._lock:
                if cache_type in ["all", "memory"]:
                    self.memory_cache.clear()
                
                if cache_type in ["all", "disk"]:
                    if self.disk_cache_key in st.session_state:
                        del st.session_state[self.disk_cache_key]
                
                # 통계 초기화
                if cache_type == "all":
                    self.stats = {
                        "memory_hits": 0,
                        "disk_hits": 0,
                        "api_calls": 0,
                        "cache_saves": 0,
                        "total_requests": 0,
                        "avg_response_time": 0.0
                    }
                    
        except Exception as e:
            print(f"캐시 삭제 오류: {e}")
    
    def optimize_cache(self):
        """캐시 최적화 (백그라운드 작업)"""
        try:
            with self._lock:
                current_time = time.time()
                
                # 만료된 메모리 캐시 항목 제거
                expired_keys = []
                for key, (data, timestamp, ttl) in self.memory_cache.items():
                    if current_time - timestamp >= ttl:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.memory_cache[key]
                
                # 디스크 캐시 저장
                self._save_disk_cache()
                
        except Exception as e:
            print(f"캐시 최적화 오류: {e}")

# 전역 캐시 인스턴스
_global_cache = None

def get_advanced_cache() -> AdvancedTranslationCache:
    """전역 고급 캐시 인스턴스 반환"""
    global _global_cache
    if _global_cache is None:
        _global_cache = AdvancedTranslationCache()
    return _global_cache

@lru_cache(maxsize=100)
def get_cached_translation_fast(text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """빠른 캐시 조회 (LRU 데코레이터 사용)"""
    cache = get_advanced_cache()
    return cache.get(text, source_lang, target_lang)

def cache_translation(text: str, source_lang: str, target_lang: str, translation: str):
    """번역 결과 캐시 저장"""
    cache = get_advanced_cache()
    cache.set(text, source_lang, target_lang, translation)
    
    # LRU 캐시도 업데이트
    get_cached_translation_fast.cache_clear()

def get_cache_performance_report() -> Dict[str, Any]:
    """캐시 성능 보고서 생성"""
    cache = get_advanced_cache()
    stats = cache.get_stats()
    
    # 성능 등급 계산
    hit_rate = stats["hit_rate"]
    if hit_rate >= 90:
        performance_grade = "🟢 Excellent"
    elif hit_rate >= 70:
        performance_grade = "🟡 Good"
    elif hit_rate >= 50:
        performance_grade = "🟠 Average"
    else:
        performance_grade = "🔴 Poor"
    
    return {
        **stats,
        "performance_grade": performance_grade,
        "recommendations": _get_performance_recommendations(stats)
    }

def _get_performance_recommendations(stats: Dict[str, Any]) -> List[str]:
    """성능 개선 권장사항 생성"""
    recommendations = []
    
    if stats["hit_rate"] < 50:
        recommendations.append("캐시 크기를 늘려보세요")
        recommendations.append("TTL 시간을 증가시켜보세요")
    
    if stats["avg_response_time_ms"] > 100:
        recommendations.append("네트워크 연결을 확인하세요")
        recommendations.append("캐시 최적화를 실행하세요")
    
    if stats["memory_hit_rate"] < 30:
        recommendations.append("메모리 캐시 크기를 늘려보세요")
    
    if not recommendations:
        recommendations.append("현재 최적의 성능을 발휘하고 있습니다")
    
    return recommendations 