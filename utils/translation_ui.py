"""
언어 전환 UI 컴포넌트 - 개선된 버전
사이드바 언어 선택기 및 관련 UI 요소들 (향상된 UX)
"""

import streamlit as st
from typing import Optional, Dict, List
from .language_manager import get_language_manager, t

def show_language_selector(position: str = "sidebar") -> Optional[str]:
    """
    개선된 언어 선택기 표시 (시각적 향상)
    
    Args:
        position: 'sidebar' 또는 'main'
        
    Returns:
        선택된 언어 코드 또는 None
    """
    lang_manager = get_language_manager()
    languages = lang_manager.get_language_selector_data()
    
    current_lang = lang_manager.get_current_language()
    current_index = next((i for i, lang in enumerate(languages) if lang['code'] == current_lang), 0)
    
    # UI 컨테이너 선택
    container = st.sidebar if position == "sidebar" else st
    
    with container:
        # 더 깔끔한 헤더
        st.markdown("### 🌐 언어 / Language")
        
        # 현재 언어 표시 (시각적 강조)
        current_lang_info = languages[current_index]
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #f0f2f6 0%, #e8eaf0 100%);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #0066cc;
        ">
            <strong>🎯 현재: {current_lang_info['display']}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # 언어 선택 버튼들 (그리드 형태)
        st.markdown("**언어 선택 / Select Language:**")
        
        # 2x2 그리드로 언어 버튼 배치
        col1, col2 = st.columns(2)
        
        with col1:
            # 한국어 버튼
            if st.button(
                "🇰🇷 한국어", 
                use_container_width=True,
                type="primary" if current_lang == "ko" else "secondary",
                help="Korean / 한국어"
            ):
                if _change_language("ko", lang_manager):
                    st.rerun()
            
            # 베트남어 버튼  
            if st.button(
                "🇻🇳 Tiếng Việt", 
                use_container_width=True,
                type="primary" if current_lang == "vi" else "secondary",
                help="Vietnamese / 베트남어"
            ):
                if _change_language("vi", lang_manager):
                    st.rerun()
        
        with col2:
            # 영어 버튼
            if st.button(
                "🇺🇸 English", 
                use_container_width=True,
                type="primary" if current_lang == "en" else "secondary",
                help="English / 영어"
            ):
                if _change_language("en", lang_manager):
                    st.rerun()
            
            # 중국어 버튼
            if st.button(
                "🇨🇳 中文", 
                use_container_width=True,
                type="primary" if current_lang == "zh" else "secondary",
                help="Chinese / 중국어"
            ):
                if _change_language("zh", lang_manager):
                    st.rerun()
        
        # 언어 전환 상태 표시
        if "language_change_status" in st.session_state:
            status = st.session_state.language_change_status
            if status["type"] == "success":
                st.success(status["message"])
            elif status["type"] == "error":
                st.error(status["message"])
            # 상태 메시지 제거
            del st.session_state.language_change_status
        
        # 번역 진행 상태 표시
        _show_translation_status()
        
        return current_lang

def _change_language(target_lang: str, lang_manager) -> bool:
    """언어 변경 처리 (내부 함수)"""
    try:
        if lang_manager.set_language(target_lang):
            # 성공 메시지 저장
            lang_names = {
                'ko': '한국어',
                'en': 'English', 
                'vi': 'Tiếng Việt',
                'zh': '中文'
            }
            st.session_state.language_change_status = {
                "type": "success",
                "message": f"✅ 언어가 {lang_names.get(target_lang, target_lang)}로 변경되었습니다!"
            }
            return True
        else:
            st.session_state.language_change_status = {
                "type": "error", 
                "message": "❌ 언어 변경에 실패했습니다."
            }
            return False
    except Exception as e:
        st.session_state.language_change_status = {
            "type": "error",
            "message": f"❌ 오류: {str(e)}"
        }
        return False

def _show_translation_status():
    """번역 상태 정보 표시"""
    with st.expander("🔧 번역 정보", expanded=False):
        lang_manager = get_language_manager()
        
        # 캐시 통계
        cache_stats = getattr(lang_manager, '_translation_cache', {})
        st.write(f"📊 **번역 캐시**: {len(cache_stats)}개 항목")
        
        # 지원 언어 목록
        languages = lang_manager.get_language_selector_data()
        st.write("🌍 **지원 언어**:")
        for lang in languages:
            st.write(f"  • {lang['display']}")
        
        # 번역 엔진 정보
        st.write("⚙️ **번역 엔진**: Google Translate API + 정적 사전")
        st.write("🚀 **성능**: 캐시 기반 고속 번역")

def show_translation_loading(text: str = "번역 중...", show_progress: bool = True):
    """
    번역 로딩 상태 표시
    
    Args:
        text: 로딩 메시지
        show_progress: 진행률 표시 여부
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 애니메이션 효과
            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 30:
                    status_text.text("🔍 텍스트 분석 중...")
                elif i < 70:
                    status_text.text("🌐 번역 처리 중...")
                else:
                    status_text.text("✨ 번역 완료!")
                
                # 실제 사용시에는 time.sleep(0.01) 추가
            
            progress_bar.empty()
            status_text.empty()
        else:
            st.info(f"🔄 {text}")

def show_translation_error(error_msg: str, suggestion: str = None):
    """
    번역 오류 표시
    
    Args:
        error_msg: 오류 메시지
        suggestion: 해결 방안 제안
    """
    st.error(f"❌ **번역 오류**: {error_msg}")
    
    if suggestion:
        st.info(f"💡 **해결 방안**: {suggestion}")
    
    # 재시도 버튼
    if st.button("🔄 다시 시도", key="retry_translation"):
        st.rerun()

def show_language_stats():
    """언어별 사용 통계 표시"""
    lang_manager = get_language_manager()
    
    # 세션에서 언어 사용 통계 가져오기
    if "language_usage_stats" not in st.session_state:
        st.session_state.language_usage_stats = {}
    
    stats = st.session_state.language_usage_stats
    current_lang = lang_manager.get_current_language()
    
    # 현재 언어 사용 카운트 증가
    stats[current_lang] = stats.get(current_lang, 0) + 1
    
    st.markdown("### 📊 언어 사용 통계")
    
    if stats:
        # 막대 차트로 표시
        import pandas as pd
        
        lang_names = {
            'ko': '🇰🇷 한국어',
            'en': '🇺🇸 English',
            'vi': '🇻🇳 Tiếng Việt', 
            'zh': '🇨🇳 中文'
        }
        
        df = pd.DataFrame([
            {"언어": lang_names.get(lang, lang), "사용횟수": count}
            for lang, count in stats.items()
        ])
        
        st.bar_chart(df.set_index("언어")["사용횟수"])
    else:
        st.info("아직 사용 통계가 없습니다.")

def show_translation_quality_feedback():
    """번역 품질 피드백 수집"""
    st.markdown("### 💬 번역 품질 평가")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rating = st.select_slider(
            "번역 품질을 평가해주세요:",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x
        )
    
    with col2:
        feedback_type = st.selectbox(
            "피드백 유형:",
            ["일반 의견", "번역 오류 신고", "기능 개선 제안", "기타"]
        )
    
    feedback_text = st.text_area(
        "상세 의견 (선택사항):",
        placeholder="번역 품질이나 기능에 대한 의견을 자유롭게 작성해주세요..."
    )
    
    if st.button("📝 피드백 제출", type="primary"):
        # 피드백 저장 (실제로는 데이터베이스에 저장)
        if "translation_feedback" not in st.session_state:
            st.session_state.translation_feedback = []
        
        feedback_data = {
            "rating": rating,
            "type": feedback_type,
            "text": feedback_text,
            "timestamp": st.session_state.get("current_time", "지금"),
            "language": get_language_manager().get_current_language()
        }
        
        st.session_state.translation_feedback.append(feedback_data)
        st.success("✅ 피드백이 제출되었습니다. 감사합니다!")

def show_language_help():
    """언어 전환 도움말"""
    with st.expander("❓ 언어 전환 도움말", expanded=False):
        st.markdown("""
        ### 🌐 언어 전환 기능 사용법
        
        #### 📋 **지원 언어**
        - 🇰🇷 **한국어**: 기본 언어 (Korean)
        - 🇺🇸 **영어**: English 
        - 🇻🇳 **베트남어**: Tiếng Việt
        - 🇨🇳 **중국어**: 中文 (간체)
        
        #### 🔧 **사용 방법**
        1. 위의 언어 버튼을 클릭
        2. 자동으로 전체 인터페이스 번역
        3. 설정이 세션 동안 유지됨
        
        #### ⚡ **번역 기능**
        - **실시간 번역**: Google Translate API
        - **전문 용어**: QC/KPI 특화 사전
        - **고속 처리**: 캐시 기반 최적화
        
        #### 🚨 **문제 해결**
        - **번역이 안 되는 경우**: 페이지 새로고침
        - **로딩이 오래 걸리는 경우**: 인터넷 연결 확인
        - **번역 품질 문제**: 하단 피드백 제출
        
        #### 📧 **문의사항**
        번역 관련 문의는 시스템 관리자에게 연락하세요.
        """)

def show_language_status() -> None:
    """현재 언어 상태 표시 (작은 표시기)"""
    lang_manager = get_language_manager()
    current_lang_info = lang_manager.get_language_info()
    
    st.sidebar.markdown(
        f"**{current_lang_info['flag']} {current_lang_info['name']}**"
    )

def create_translated_menu() -> dict:
    """번역된 메뉴 항목 생성"""
    return {
        'dashboard': {
            'title': t('dashboard'),
            'icon': '📊'
        },
        'inspection_input': {
            'title': t('inspection_input'),
            'icon': '📝'
        },
        'reports': {
            'title': t('reports'),
            'icon': '📈'
        },
        'inspector_management': {
            'title': t('inspector_management'),
            'icon': '👥'
        },
        'item_management': {
            'title': t('item_management'),
            'icon': '📦'
        },
        'defect_type_management': {
            'title': t('defect_type_management'),
            'icon': '🔍'
        },
        'admin_management': {
            'title': t('admin_management'),
            'icon': '⚙️'
        },
        'shift_reports': {
            'title': t('shift_reports'),
            'icon': '🏭'
        }
    }

def show_translated_title(title_key: str, icon: str = "", level: int = 1) -> None:
    """번역된 제목 표시"""
    title_text = t(title_key)
    if icon:
        title_text = f"{icon} {title_text}"
    
    if level == 1:
        st.title(title_text)
    elif level == 2:
        st.header(title_text)
    elif level == 3:
        st.subheader(title_text)
    else:
        st.markdown(f"**{title_text}**")

def show_translated_button(key: str, help_text: str = "", disabled: bool = False) -> bool:
    """번역된 버튼 표시"""
    button_text = t(key)
    help_text_translated = t(help_text) if help_text else ""
    
    return st.button(
        button_text,
        help=help_text_translated if help_text_translated else None,
        disabled=disabled
    )

def show_translated_metric(label_key: str, value: str, delta: str = "", help_text: str = "") -> None:
    """번역된 메트릭 표시"""
    label_text = t(label_key)
    help_text_translated = t(help_text) if help_text else ""
    
    st.metric(
        label=label_text,
        value=value,
        delta=delta,
        help=help_text_translated if help_text_translated else None
    )

def show_translated_columns(column_keys: list) -> list:
    """번역된 컬럼 헤더 생성"""
    return [t(key) for key in column_keys]

def show_translated_status(status_key: str, status_type: str = "info") -> None:
    """번역된 상태 메시지 표시"""
    message = t(status_key)
    
    if status_type == "success":
        st.success(message)
    elif status_type == "error":
        st.error(message)
    elif status_type == "warning":
        st.warning(message)
    else:
        st.info(message)

def create_language_toggle() -> None:
    """간단한 언어 토글 버튼 (헤더용)"""
    lang_manager = get_language_manager()
    current_lang = lang_manager.get_current_language()
    
    # 현재 언어에 따라 다음 언어 결정
    next_lang_map = {
        'ko': 'en',
        'en': 'vi', 
        'vi': 'zh',
        'zh': 'ko'
    }
    
    next_lang = next_lang_map.get(current_lang, 'en')
    next_lang_info = lang_manager.get_language_info(next_lang)
    
    col1, col2, col3 = st.columns([8, 1, 1])
    
    with col3:
        if st.button(
            f"{next_lang_info['flag']}",
            help=f"Switch to {next_lang_info['name']}",
            key="quick_lang_toggle"
        ):
            lang_manager.set_language(next_lang)
            st.rerun()

def wrap_with_translation(func):
    """
    함수를 번역 컨텍스트로 래핑하는 데코레이터
    페이지 함수에 적용하여 자동으로 번역 활성화
    """
    def wrapper(*args, **kwargs):
        # 언어 매니저 초기화
        get_language_manager()
        # 원본 함수 실행
        return func(*args, **kwargs)
    
    return wrapper 

def show_performance_monitor():
    """성능 모니터링 대시보드"""
    from .advanced_cache import get_cache_performance_report
    from .language_manager import get_language_manager
    
    st.markdown("### 🚀 번역 성능 모니터링")
    
    try:
        # 성능 보고서 가져오기
        report = get_cache_performance_report()
        
        # 성능 지표 카드
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🎯 캐시 히트율",
                f"{report['hit_rate']:.1f}%",
                help="캐시에서 직접 조회된 비율"
            )
        
        with col2:
            st.metric(
                "⚡ 평균 응답시간", 
                f"{report['avg_response_time_ms']:.1f}ms",
                help="번역 요청의 평균 처리 시간"
            )
        
        with col3:
            st.metric(
                "💾 메모리 캐시",
                f"{report['memory_cache_size']}개",
                help="메모리에 저장된 번역 항목 수"
            )
            
        with col4:
            st.metric(
                "📊 총 요청수",
                f"{report['total_requests']}건",
                help="지금까지 처리된 총 번역 요청"
            )
        
        # 성능 등급 표시
        st.markdown(f"### {report['performance_grade']} 성능 등급")
        
        # 상세 통계
        with st.expander("📈 상세 통계", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**메모리 캐시 성능:**")
                st.write(f"- 히트 수: {report['memory_hits']}회")
                st.write(f"- 히트율: {report['memory_hit_rate']}%")
                
                st.write("**디스크 캐시 성능:**")
                st.write(f"- 히트 수: {report['disk_hits']}회") 
                st.write(f"- 히트율: {report['disk_hit_rate']}%")
            
            with col2:
                st.write("**API 호출 통계:**")
                st.write(f"- 총 API 호출: {report['api_calls']}회")
                st.write(f"- 캐시 저장: {report['cache_saves']}회")
                
        # 권장사항
        if report['recommendations']:
            st.markdown("### 💡 성능 개선 권장사항")
            for rec in report['recommendations']:
                st.info(f"• {rec}")
        
        # 캐시 관리 버튼들
        st.markdown("### 🔧 캐시 관리")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ 메모리 캐시 삭제", help="메모리 캐시만 삭제"):
                lang_manager = get_language_manager()
                lang_manager.clear_translation_cache("memory")
                st.success("메모리 캐시가 삭제되었습니다.")
                st.rerun()
        
        with col2:
            if st.button("💿 디스크 캐시 삭제", help="디스크 캐시만 삭제"):
                lang_manager = get_language_manager()
                lang_manager.clear_translation_cache("disk")
                st.success("디스크 캐시가 삭제되었습니다.")
                st.rerun()
        
        with col3:
            if st.button("🔄 캐시 최적화", help="캐시 성능 최적화 실행"):
                lang_manager = get_language_manager()
                lang_manager.optimize_performance()
                st.success("캐시가 최적화되었습니다.")
                st.rerun()
                
    except Exception as e:
        st.error(f"성능 모니터링 오류: {str(e)}")

def show_translation_benchmark():
    """번역 성능 벤치마크"""
    st.markdown("### 🏃‍♂️ 번역 성능 벤치마크")
    
    if st.button("▶️ 벤치마크 실행", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 테스트 데이터
        test_data = [
            "quality_control",
            "defect_analysis", 
            "inspection_process",
            "production_line",
            "shift_performance"
        ]
        
        from .language_manager import get_language_manager, t
        import time
        
        results = {}
        
        # 각 언어별 테스트
        languages = ['en', 'vi', 'zh']
        total_steps = len(languages) * len(test_data) * 2  # 2번씩 실행
        current_step = 0
        
        lang_manager = get_language_manager()
        
        for lang in languages:
            lang_manager.set_language(lang)
            lang_results = {"first_run": 0, "second_run": 0}
            
            # 첫 번째 실행 (캐시 미스)
            status_text.text(f"🔍 {lang} 언어 첫 번째 테스트...")
            start_time = time.time()
            
            for text in test_data:
                t(text)
                current_step += 1
                progress_bar.progress(current_step / total_steps)
                
            lang_results["first_run"] = time.time() - start_time
            
            # 두 번째 실행 (캐시 히트)
            status_text.text(f"⚡ {lang} 언어 두 번째 테스트...")
            start_time = time.time()
            
            for text in test_data:
                t(text)
                current_step += 1
                progress_bar.progress(current_step / total_steps)
                
            lang_results["second_run"] = time.time() - start_time
            results[lang] = lang_results
        
        progress_bar.empty()
        status_text.empty()
        
        # 결과 표시
        st.markdown("### 📊 벤치마크 결과")
        
        for lang, data in results.items():
            lang_names = {'en': '🇺🇸 English', 'vi': '🇻🇳 Tiếng Việt', 'zh': '🇨🇳 中文'}
            
            with st.expander(f"{lang_names[lang]} 결과", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("첫 번째 실행", f"{data['first_run']:.3f}초")
                
                with col2:
                    st.metric("두 번째 실행", f"{data['second_run']:.3f}초")
                
                with col3:
                    if data['second_run'] > 0:
                        speedup = data['first_run'] / data['second_run']
                        st.metric("성능 향상", f"{speedup:.1f}배")
                    else:
                        st.metric("성능 향상", "∞배")

# 메인 언어 선택기에 모든 컴포넌트 통합
def show_enhanced_language_selector(position: str = "sidebar"):
    """
    향상된 언어 선택기 (모든 기능 통합)
    """
    # 기본 언어 선택기
    show_language_selector(position)
    
    # 추가 기능들 (접을 수 있는 형태로)
    if position == "sidebar":
        st.markdown("---")
        
        # 고급 기능들
        with st.expander("🔧 고급 설정", expanded=False):
            show_language_stats()
            show_translation_quality_feedback()
        
        # 도움말
        show_language_help() 

# 메인 함수에 성능 모니터링 통합
def show_enhanced_language_selector_with_performance(position: str = "sidebar"):
    """
    성능 모니터링이 통합된 언어 선택기
    """
    # 기본 언어 선택기
    show_enhanced_language_selector(position)
    
    if position == "sidebar":
        st.markdown("---")
        
        # 성능 모니터링 (접을 수 있는 형태)
        with st.expander("🚀 성능 모니터링", expanded=False):
            show_performance_monitor()
            
        with st.expander("🏃‍♂️ 성능 벤치마크", expanded=False):
            show_translation_benchmark() 