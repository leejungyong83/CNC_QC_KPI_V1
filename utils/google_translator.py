"""
Google Translate 연동 모듈
패키지 충돌 문제로 인해 기본 requests만 사용하여 구현
"""

import requests
import json
import time
import urllib.parse
from typing import Optional, Dict
import streamlit as st

class GoogleTranslator:
    """Google Translate API를 사용한 번역기"""
    
    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"
        self.request_count = 0
        self.last_request_time = 0
        self.session = requests.Session()
        
        # 사용자 에이전트 설정
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def translate_text(self, text: str, target_lang: str = 'en', source_lang: str = 'auto') -> str:
        """
        텍스트 번역
        
        Args:
            text: 번역할 텍스트
            target_lang: 목표 언어 코드 (en, vi, zh, ko)
            source_lang: 소스 언어 코드 (auto = 자동 감지)
            
        Returns:
            번역된 텍스트
        """
        if not text or not text.strip():
            return text
            
        # 요청 제한 (1초에 1회)
        current_time = time.time()
        if current_time - self.last_request_time < 1:
            time.sleep(1)
        
        try:
            # URL 파라미터 구성
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            # API 요청
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # 응답 파싱
            result = response.json()
            
            if result and len(result) > 0 and len(result[0]) > 0:
                translated_text = result[0][0][0]
                self.last_request_time = current_time
                return translated_text
            else:
                return text
                
        except Exception as e:
            # 에러 발생 시 원본 텍스트 반환
            if not st.session_state.get('translation_error_shown', False):
                st.warning(f"번역 서비스 일시 오류: {str(e)[:50]}...")
                st.session_state.translation_error_shown = True
            return text
    
    def detect_language(self, text: str) -> str:
        """
        언어 감지 (간단한 휴리스틱 방식)
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            감지된 언어 코드
        """
        if not text:
            return 'ko'
        
        # 한글 문자 범위 체크
        korean_chars = sum(1 for char in text if 0xAC00 <= ord(char) <= 0xD7A3)
        
        # 영어 문자 범위 체크  
        english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
        
        # 중국어 문자 범위 체크 (CJK 통합 한자)
        chinese_chars = sum(1 for char in text if 0x4E00 <= ord(char) <= 0x9FFF)
        
        # 베트남어 특수 문자 체크
        vietnamese_chars = sum(1 for char in text if char in 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ')
        
        total_chars = len([c for c in text if c.isalpha() or 0x4E00 <= ord(c) <= 0x9FFF or 0xAC00 <= ord(c) <= 0xD7A3])
        
        if total_chars == 0:
            return 'ko'
        
        # 비율로 언어 판단
        if korean_chars / total_chars > 0.3:
            return 'ko'
        elif english_chars / total_chars > 0.7:
            return 'en'
        elif chinese_chars / total_chars > 0.3:
            return 'zh'
        elif vietnamese_chars / total_chars > 0.1:
            return 'vi'
        else:
            return 'en'  # 기본값


class TranslationCache:
    """번역 결과 캐싱 시스템"""
    
    def __init__(self):
        if 'translation_cache' not in st.session_state:
            st.session_state.translation_cache = {}
    
    def get_cache_key(self, text: str, target_lang: str) -> str:
        """캐시 키 생성"""
        return f"{hash(text)}_{target_lang}"
    
    def get(self, text: str, target_lang: str) -> Optional[str]:
        """캐시에서 번역 결과 조회"""
        key = self.get_cache_key(text, target_lang)
        return st.session_state.translation_cache.get(key)
    
    def set(self, text: str, target_lang: str, translation: str):
        """번역 결과 캐시에 저장"""
        key = self.get_cache_key(text, target_lang)
        st.session_state.translation_cache[key] = translation
        
        # 캐시 크기 제한 (최대 1000개)
        if len(st.session_state.translation_cache) > 1000:
            # 가장 오래된 항목들 삭제
            items = list(st.session_state.translation_cache.items())
            st.session_state.translation_cache = dict(items[-800:])
    
    def clear(self):
        """캐시 초기화"""
        st.session_state.translation_cache = {}


# 전역 인스턴스
_google_translator = None
_translation_cache = None

def get_google_translator() -> GoogleTranslator:
    """Google Translator 싱글톤 인스턴스 반환"""
    global _google_translator
    if _google_translator is None:
        _google_translator = GoogleTranslator()
    return _google_translator

def get_translation_cache() -> TranslationCache:
    """Translation Cache 싱글톤 인스턴스 반환"""
    global _translation_cache
    if _translation_cache is None:
        _translation_cache = TranslationCache()
    return _translation_cache

def translate_with_cache(text: str, target_lang: str, source_lang: str = 'auto') -> str:
    """
    캐시를 사용한 번역 함수
    
    Args:
        text: 번역할 텍스트
        target_lang: 목표 언어
        source_lang: 소스 언어 (기본값: auto)
        
    Returns:
        번역된 텍스트
    """
    if not text or not text.strip():
        return text
    
    # 같은 언어면 번역하지 않음
    if source_lang == target_lang:
        return text
    
    cache = get_translation_cache()
    
    # 캐시에서 확인
    cached_result = cache.get(text, target_lang)
    if cached_result:
        return cached_result
    
    # 번역 수행
    translator = get_google_translator()
    translated = translator.translate_text(text, target_lang, source_lang)
    
    # 캐시에 저장
    if translated != text:  # 번역이 실제로 수행된 경우만 캐시
        cache.set(text, target_lang, translated)
    
    return translated 