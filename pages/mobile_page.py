"""
모바일 전용 페이지
현장 검사원을 위한 모바일 최적화 인터페이스
"""

import streamlit as st
from utils.mobile_components import show_mobile_interface


def show_mobile_page():
    """모바일 페이지 표시"""
    
    # 모바일 전용 CSS 스타일 적용
    st.markdown("""
    <style>
    /* 모바일 최적화 CSS */
    .main > div {
        padding-top: 0rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* 버튼 스타일 개선 */
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        margin: 5px 0;
    }
    
    /* Primary 버튼 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Secondary 버튼 */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.4);
    }
    
    /* 입력 필드 크기 조정 */
    .stSelectbox > div > div > div {
        font-size: 1.1rem;
    }
    
    .stNumberInput > div > div > input {
        font-size: 1.2rem;
        height: 3rem;
    }
    
    .stDateInput > div > div > input {
        font-size: 1.1rem;
        height: 3rem;
    }
    
    .stTextArea textarea {
        font-size: 1.1rem;
        border-radius: 10px;
    }
    
    /* 메트릭 카드 간격 조정 */
    .metric-container {
        margin: 1rem 0;
    }
    
    /* 폼 스타일 */
    .stForm {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* 제목 스타일 */
    h1, h2, h3 {
        color: #2c3e50;
        text-align: center;
    }
    
    /* 성공/에러 메시지 스타일 */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* 사이드바 숨김 (모바일에서) */
    .css-1d391kg {
        display: none;
    }
    
    /* Expander 스타일 */
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    /* 컨테이너 패딩 조정 */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* 컬럼 간격 조정 */
    .row-widget.stHorizontal > div {
        gap: 0.5rem;
    }
    
    /* 파일 업로더 스타일 */
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
    
    /* 진행률 바 스타일 */
    .stProgress > div > div {
        border-radius: 10px;
        height: 20px;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px 15px 0 0;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* 모바일 전용 헤더 */
    .mobile-header {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: white;
        padding: 1rem 0;
        border-bottom: 1px solid #eee;
        margin-bottom: 1rem;
    }
    
    /* 터치 친화적 인터랙션 */
    button:hover {
        transform: translateY(-2px);
        transition: all 0.2s ease;
    }
    
    /* 스크롤바 스타일 (웹킷 브라우저) */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5a67d8;
    }
    
    /* 모바일 전용 알림 스타일 */
    .mobile-alert {
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 1rem;
        text-align: center;
    }
    
    /* 로딩 애니메이션 */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(102, 126, 234, 0.3);
        border-radius: 50%;
        border-top-color: #667eea;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 모바일 전용 카드 */
    .mobile-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e0e6ed;
    }
    
    /* 빠른 액션 그리드 */
    .quick-action-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* 상태 표시기 */
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-success { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-danger { background-color: #dc3545; }
    .status-info { background-color: #17a2b8; }
    
    /* 모바일 네비게이션 */
    .mobile-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #eee;
        padding: 1rem;
        z-index: 1000;
    }
    
    /* 터치 피드백 */
    .touch-feedback {
        -webkit-tap-highlight-color: rgba(102, 126, 234, 0.3);
        user-select: none;
    }
    
    /* 반응형 텍스트 */
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem; }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.3rem; }
        p { font-size: 1rem; }
        
        .stButton > button {
            font-size: 1rem;
            height: 2.8rem;
        }
    }
    
    /* 가로 모드 최적화 */
    @media (orientation: landscape) and (max-height: 500px) {
        .mobile-header {
            padding: 0.5rem 0;
        }
        
        .stButton > button {
            height: 2.5rem;
            font-size: 0.95rem;
        }
        
        .mobile-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 모바일 인터페이스 표시
    show_mobile_interface()


def show_mobile_menu():
    """모바일용 간단한 메뉴"""
    st.sidebar.markdown("### 📱 모바일 메뉴")
    
    # 간소화된 메뉴
    menu_options = {
        "🏠 홈": "mobile_dashboard",
        "📝 검사입력": "mobile_input", 
        "📊 오늘실적": "mobile_today",
        "🔔 알림": "mobile_notifications",
        "📷 사진": "mobile_photo",
        "💻 PC버전": "desktop_mode"
    }
    
    for label, action in menu_options.items():
        if st.sidebar.button(label, key=f"mobile_menu_{action}", use_container_width=True):
            if action == "desktop_mode":
                st.session_state.is_mobile = False
                st.session_state.selected_menu = "종합 대시보드"
                st.rerun()
            else:
                st.session_state.mobile_action = action.replace("mobile_", "")
                st.rerun()


if __name__ == "__main__":
    show_mobile_page() 