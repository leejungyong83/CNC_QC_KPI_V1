# 🌐 월요일 언어전환 기능 개발 가이드

## 📅 **2025년 7월 30일 월요일 실행 계획**

### 🎯 **최종 목표**
QC KPI 대시보드에 **4개 언어** (한국어, 영어, 베트남어, 중국어) 실시간 번역 기능 완전 구현

---

## 🚀 **1단계: 환경 준비 (09:00-09:30)**

### 필수 패키지 설치:
```bash
# 터미널에서 실행
cd C:\CURSOR\QC_KPI
pip install googletrans==4.0.0rc1 langdetect==1.0.9 streamlit-option-menu==0.3.6 pycountry==22.3.5
```

### 설치 확인:
```bash
python -c "from googletrans import Translator; print('✅ Google Translate 설치 성공')"
python -c "import langdetect; print('✅ Language Detect 설치 성공')"
python -c "from streamlit_option_menu import option_menu; print('✅ Option Menu 설치 성공')"
```

---

## 🏗️ **2단계: 핵심 번역 엔진 구현 (09:30-11:00)**

### 파일 생성 체크리스트:
- ✅ `utils/language_manager.py` - **이미 생성됨**
- ✅ `utils/translation_ui.py` - **이미 생성됨**
- 🔲 `utils/google_translator.py` - **월요일 생성 필요**
- 🔲 `utils/translation_cache.py` - **월요일 생성 필요**

### 구현할 파일 1: `utils/google_translator.py`
```python
"""
Google Translate API 연동 모듈
실시간 번역 기능 구현
"""

from googletrans import Translator
import langdetect
from typing import Optional, Dict
import time
import streamlit as st

class GoogleTranslator:
    def __init__(self):
        self.translator = Translator()
        self.request_count = 0
        self.last_request_time = 0
        
    def translate_text(self, text: str, target_lang: str = 'en') -> str:
        """텍스트 번역 (요청 제한 고려)"""
        try:
            # 요청 제한 (1초에 1회)
            current_time = time.time()
            if current_time - self.last_request_time < 1:
                time.sleep(1)
            
            result = self.translator.translate(text, dest=target_lang)
            self.last_request_time = current_time
            return result.text
            
        except Exception as e:
            st.warning(f"번역 실패: {e}")
            return text  # 원본 텍스트 반환
```

### 구현할 파일 2: `utils/translation_cache.py`
```python
"""
번역 결과 캐싱 시스템
성능 최적화를 위한 캐시 관리
"""

import json
import hashlib
from typing import Dict, Optional
import streamlit as st

class TranslationCache:
    def __init__(self):
        if 'translation_cache' not in st.session_state:
            st.session_state.translation_cache = {}
    
    def get_cache_key(self, text: str, target_lang: str) -> str:
        """캐시 키 생성"""
        content = f"{text}_{target_lang}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, target_lang: str) -> Optional[str]:
        """캐시에서 번역 결과 조회"""
        key = self.get_cache_key(text, target_lang)
        return st.session_state.translation_cache.get(key)
    
    def set(self, text: str, target_lang: str, translation: str):
        """번역 결과 캐시에 저장"""
        key = self.get_cache_key(text, target_lang)
        st.session_state.translation_cache[key] = translation
```

---

## 🎨 **3단계: UI 컴포넌트 통합 (11:00-12:00)**

### `app.py` 수정사항:
```python
# 기존 import에 추가
from utils.translation_ui import show_language_selector, create_translated_menu
from utils.language_manager import t

# main() 함수 내 사이드바 상단에 추가
def main():
    st.set_page_config(...)
    
    # 언어 선택기 (사이드바 최상단)
    show_language_selector("sidebar")
    
    # 번역된 메뉴 생성
    translated_menu = create_translated_menu()
    
    # 기존 메뉴를 번역된 메뉴로 교체
    selected_page = st.sidebar.radio(
        t('navigation', '메뉴'),
        list(translated_menu.keys()),
        format_func=lambda x: f"{translated_menu[x]['icon']} {translated_menu[x]['title']}"
    )
```

---

## 📊 **4단계: 대시보드 페이지 다국어화 (13:00-15:00)**

### `pages/dashboard.py` 수정사항:
```python
# 파일 상단에 추가
from utils.language_manager import t
from utils.translation_ui import show_translated_title, show_translated_metric

def show_dashboard():
    # 제목 번역
    show_translated_title('dashboard', '📊', level=1)
    
    # KPI 메트릭 번역
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_translated_metric('defect_rate', f"{defect_rate:.2%}")
    
    with col2:
        show_translated_metric('inspection_efficiency', f"{efficiency:.1%}")
    
    # 기존 텍스트를 t() 함수로 감싸기
    st.subheader(t('today_kpi', '오늘의 KPI'))
    st.write(t('shift_info', '교대조 정보'))
```

---

## 📝 **5단계: 검사 입력 페이지 다국어화 (15:00-16:00)**

### `pages/inspection_input.py` 주요 수정사항:
```python
from utils.language_manager import t
from utils.translation_ui import show_translated_title, show_translated_button

def show_inspection_input():
    show_translated_title('inspection_input', '📝')
    
    # 폼 라벨 번역
    inspection_date = st.date_input(t('inspection_date', '검사일'))
    inspector_name = st.selectbox(t('inspector', '검사자'), inspector_options)
    model_name = st.selectbox(t('model', '모델'), model_options)
    
    # 버튼 번역
    if show_translated_button('save', 'save_inspection'):
        # 저장 로직
        pass
```

---

## 📈 **6단계: 리포트 페이지 다국어화 (16:00-17:00)**

### `pages/reports.py` 주요 수정사항:
```python
from utils.language_manager import t
from utils.translation_ui import show_translated_title, show_translated_columns

def show_reports():
    show_translated_title('reports', '📈')
    
    # 탭 번역
    tab1, tab2, tab3 = st.tabs([
        t('daily_report', '일일 리포트'),
        t('weekly_report', '주간 리포트'),
        t('monthly_report', '월간 리포트')
    ])
    
    # 데이터프레임 컬럼 번역
    df.columns = show_translated_columns(['date', 'inspector', 'defect_rate'])
```

---

## 🧪 **7단계: 테스트 및 최종 검증 (17:00-18:00)**

### 테스트 체크리스트:
```bash
# 빌드 테스트
python -c "from utils.language_manager import get_language_manager; print('✅ 언어 매니저 정상')"
python -c "from utils.translation_ui import show_language_selector; print('✅ UI 컴포넌트 정상')"

# 전체 앱 테스트
streamlit run app.py
```

### 기능 테스트:
1. **언어 선택기** 정상 작동 확인
2. **4개 언어** 전환 테스트
3. **모든 페이지** 다국어 표시 확인
4. **번역 품질** 검증
5. **성능** 확인 (페이지 로딩 속도)

---

## 📦 **8단계: 배포 준비 (18:00-18:30)**

### requirements.txt 업데이트:
```bash
# 기존 내용 유지하고 추가
echo "googletrans==4.0.0rc1" >> requirements.txt
echo "langdetect==1.0.9" >> requirements.txt
echo "streamlit-option-menu==0.3.6" >> requirements.txt
echo "pycountry==22.3.5" >> requirements.txt
```

### Git 커밋:
```bash
git add .
git commit -m "feat: 다국어 지원 기능 완전 구현 v3.0.0

- Google Translate API 연동
- 4개 언어 지원 (한국어, 영어, 베트남어, 중국어)
- 실시간 번역 기능
- 정적 번역 사전 (KPI 전문 용어)
- 언어 선택 UI 컴포넌트
- 전체 페이지 다국어화 완료"

git push origin main
```

---

## ⚡ **성능 최적화 고려사항**

### 번역 전략:
1. **정적 번역 우선**: KPI 용어, 메뉴 항목
2. **동적 번역 보조**: 사용자 입력 텍스트, 긴 설명
3. **캐싱 활용**: 동일 텍스트 재번역 방지
4. **요청 제한**: Google API 제한 고려

### 에러 처리:
- **네트워크 오류** → 원본 텍스트 표시
- **API 제한** → 캐시된 결과 우선
- **번역 실패** → 기본 언어로 fallback

---

## 🎉 **완료 기준**

### 필수 달성 목표:
- ✅ **4개 언어** 완전 지원
- ✅ **모든 페이지** 다국어화
- ✅ **언어 선택기** 정상 작동
- ✅ **번역 품질** 85% 이상
- ✅ **페이지 로딩** 3초 이내

### 추가 달성 목표:
- 🎯 **번역 캐싱** 시스템 구현
- 🎯 **KPI 용어** 전문 번역 완료
- 🎯 **에러 처리** 완벽 구현
- 🎯 **성능 최적화** 완료

**월요일 18:30까지 완전한 다국어 QC KPI 대시보드 완성! 🌐✨** 