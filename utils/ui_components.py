"""
UI/UX 일관성을 위한 공통 컴포넌트 모듈
표준 스타일, 색상, 레이아웃 컴포넌트 제공
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime
from typing import Dict, List, Optional, Any


class UITheme:
    """UI 테마 및 색상 관리"""
    
    # 색상 팔레트
    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e', 
        'success': '#2ca02c',
        'warning': '#ff9800',
        'error': '#d62728',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40',
        'gray': '#6c757d'
    }
    
    # 상태별 색상
    STATUS_COLORS = {
        'active': COLORS['success'],
        'inactive': COLORS['gray'],
        'warning': COLORS['warning'],
        'danger': COLORS['error'],
        'info': COLORS['info']
    }
    
    # 차트 색상 팔레트
    CHART_COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]


class StandardComponents:
    """표준 UI 컴포넌트"""
    
    @staticmethod
    def page_header(title: str, subtitle: str = "", icon: str = "📊"):
        """표준 페이지 헤더"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, {UITheme.COLORS['primary']} 0%, {UITheme.COLORS['secondary']} 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
        ">
            <h1 style="margin: 0; font-size: 2.2rem;">
                {icon} {title}
            </h1>
            {f'<p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">{subtitle}</p>' if subtitle else ''}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def metric_card(title: str, value: str, delta: str = "", 
                   color: str = "primary", icon: str = "📊"):
        """표준 메트릭 카드"""
        bg_color = UITheme.COLORS.get(color, UITheme.COLORS['primary'])
        
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid {bg_color};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                <h4 style="margin: 0; color: {UITheme.COLORS['dark']}; font-size: 1rem;">{title}</h4>
            </div>
            <div style="font-size: 2rem; font-weight: bold; color: {bg_color}; margin-bottom: 0.5rem;">
                {value}
            </div>
            {f'<div style="color: {UITheme.COLORS["gray"]}; font-size: 0.9rem;">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def status_badge(text: str, status: str = "info"):
        """상태 배지"""
        color = UITheme.STATUS_COLORS.get(status, UITheme.COLORS['info'])
        
        return f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            display: inline-block;
        ">{text}</span>
        """
    
    @staticmethod
    def info_box(title: str, content: str, box_type: str = "info", icon: str = "ℹ️"):
        """정보 박스"""
        color_map = {
            'info': UITheme.COLORS['info'],
            'success': UITheme.COLORS['success'],
            'warning': UITheme.COLORS['warning'],
            'error': UITheme.COLORS['error']
        }
        
        bg_map = {
            'info': '#e3f2fd',
            'success': '#e8f5e8',
            'warning': '#fff3cd',
            'error': '#ffebee'
        }
        
        color = color_map.get(box_type, UITheme.COLORS['info'])
        bg_color = bg_map.get(box_type, '#e3f2fd')
        
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border-left: 4px solid {color};
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
                <strong style="color: {color};">{title}</strong>
            </div>
            <div style="color: {UITheme.COLORS['dark']};">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def section_divider(title: str = "", icon: str = ""):
        """섹션 구분선"""
        if title:
            st.markdown(f"""
            <div style="
                margin: 2rem 0 1rem 0;
                padding: 0.5rem 0;
                border-bottom: 2px solid {UITheme.COLORS['primary']};
            ">
                <h3 style="margin: 0; color: {UITheme.COLORS['primary']};">
                    {icon + ' ' if icon else ''}{title}
                </h3>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("---")
    
    @staticmethod
    def loading_spinner(message: str = "처리 중..."):
        """표준 로딩 스피너"""
        return st.spinner(f"🔄 {message}")
    
    @staticmethod
    def action_button(text: str, button_type: str = "primary", 
                     icon: str = "", use_container_width: bool = True):
        """표준 액션 버튼"""
        if button_type == "primary":
            return st.button(f"{icon} {text}" if icon else text, 
                           use_container_width=use_container_width, type="primary")
        elif button_type == "secondary":
            return st.button(f"{icon} {text}" if icon else text, 
                           use_container_width=use_container_width, type="secondary")
        else:
            return st.button(f"{icon} {text}" if icon else text, 
                           use_container_width=use_container_width)


class ChartComponents:
    """차트 컴포넌트"""
    
    @staticmethod
    def apply_standard_layout(fig: go.Figure, title: str = "") -> go.Figure:
        """표준 차트 레이아웃 적용"""
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': UITheme.COLORS['dark']}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'family': 'Arial, sans-serif', 'color': UITheme.COLORS['dark']},
            margin=dict(l=50, r=50, t=80, b=50),
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # 그리드 스타일
        fig.update_xaxes(
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            zeroline=False
        )
        fig.update_yaxes(
            gridcolor='rgba(128,128,128,0.2)',
            gridwidth=1,
            zeroline=False
        )
        
        return fig
    
    @staticmethod
    def create_kpi_gauge(value: float, title: str, min_val: float = 0, 
                        max_val: float = 100, threshold: float = 80):
        """KPI 게이지 차트"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            delta = {'reference': threshold},
            gauge = {
                'axis': {'range': [None, max_val]},
                'bar': {'color': UITheme.COLORS['primary']},
                'steps': [
                    {'range': [0, threshold * 0.8], 'color': UITheme.COLORS['error']},
                    {'range': [threshold * 0.8, threshold], 'color': UITheme.COLORS['warning']},
                    {'range': [threshold, max_val], 'color': UITheme.COLORS['success']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': threshold
                }
            }
        ))
        
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        return fig


class FormComponents:
    """폼 컴포넌트"""
    
    @staticmethod
    def date_range_picker(key_prefix: str = "", default_days: int = 30):
        """표준 날짜 범위 선택기"""
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "시작 날짜",
                value=datetime.now().date() - pd.Timedelta(days=default_days),
                key=f"{key_prefix}_start_date"
            )
        
        with col2:
            end_date = st.date_input(
                "종료 날짜",
                value=datetime.now().date(),
                key=f"{key_prefix}_end_date"
            )
        
        return start_date, end_date
    
    @staticmethod
    def filter_panel(title: str = "필터 옵션"):
        """표준 필터 패널"""
        with st.expander(f"🔍 {title}", expanded=False):
            return st.container()
    
    @staticmethod
    def search_box(placeholder: str = "검색어를 입력하세요...", key: str = "search"):
        """표준 검색 박스"""
        return st.text_input(
            "",
            placeholder=placeholder,
            key=key,
            help="검색어를 입력하여 결과를 필터링하세요"
        )


class DataComponents:
    """데이터 표시 컴포넌트"""
    
    @staticmethod
    def enhanced_dataframe(df, title: str = "", height: int = 400):
        """향상된 데이터프레임 표시"""
        if title:
            StandardComponents.section_divider(title, "📋")
        
        # 데이터 요약 정보
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**총 행 수:** {len(df):,}")
        
        with col2:
            st.write(f"**총 열 수:** {len(df.columns)}")
        
        with col3:
            if not df.empty:
                st.write(f"**마지막 업데이트:** {datetime.now().strftime('%H:%M:%S')}")
        
        # 데이터프레임 표시
        st.dataframe(df, height=height, use_container_width=True)
        
        # 다운로드 버튼
        if not df.empty:
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv.encode('utf-8-sig'),
                file_name=f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    @staticmethod
    def paginated_table(df, page_size: int = 20, key: str = "table"):
        """페이지네이션된 테이블"""
        if df.empty:
            st.info("표시할 데이터가 없습니다.")
            return
        
        total_rows = len(df)
        total_pages = (total_rows + page_size - 1) // page_size
        
        # 페이지 선택
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            page = st.selectbox(
                "페이지",
                range(1, total_pages + 1),
                format_func=lambda x: f"페이지 {x} / {total_pages}",
                key=f"{key}_page"
            )
        
        # 데이터 슬라이싱
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        
        page_df = df.iloc[start_idx:end_idx]
        
        # 페이지 정보
        st.write(f"**표시 중:** {start_idx + 1}-{end_idx} / {total_rows:,}개 항목")
        
        # 테이블 표시
        st.dataframe(page_df, use_container_width=True)


class LayoutComponents:
    """레이아웃 컴포넌트"""
    
    @staticmethod
    def two_column_layout(left_content, right_content, ratio=[1, 1]):
        """2열 레이아웃"""
        col1, col2 = st.columns(ratio)
        
        with col1:
            left_content()
        
        with col2:
            right_content()
    
    @staticmethod
    def three_column_layout(left_content, center_content, right_content, ratio=[1, 1, 1]):
        """3열 레이아웃"""
        col1, col2, col3 = st.columns(ratio)
        
        with col1:
            left_content()
        
        with col2:
            center_content()
        
        with col3:
            right_content()
    
    @staticmethod
    def sidebar_layout():
        """표준 사이드바 레이아웃"""
        with st.sidebar:
            st.markdown("""
            <style>
            .sidebar-content {
                padding: 1rem;
                background-color: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 1rem;
            }
            </style>
            """, unsafe_allow_html=True)
            
            return st.container()


def apply_global_styles():
    """전역 스타일 적용"""
    st.markdown(f"""
    <style>
    /* 전역 스타일 */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}
    
    /* 버튼 스타일 */
    .stButton > button {{
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }}
    
    /* 메트릭 스타일 */
    .metric-container {{
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {UITheme.COLORS['primary']};
    }}
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 10px 10px 0 0;
        font-weight: 600;
    }}
    
    /* 사이드바 스타일 */
    .stSidebar {{
        background-color: #f8f9fa;
    }}
    
    .stSidebar .stButton > button {{
        width: 100%;
        text-align: left;
        background-color: white;
        color: {UITheme.COLORS['dark']};
        border: 1px solid #dee2e6;
        margin-bottom: 0.5rem;
    }}
    
    .stSidebar .stButton > button:hover {{
        background-color: {UITheme.COLORS['primary']};
        color: white;
    }}
    
    /* 데이터프레임 스타일 */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* 알림 스타일 */
    .stAlert {{
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input {{
        border-radius: 8px;
        border: 2px solid #dee2e6;
        transition: border-color 0.3s ease;
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stDateInput > div > div > input:focus {{
        border-color: {UITheme.COLORS['primary']};
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
    }}
    
    /* 차트 컨테이너 스타일 */
    .stPlotlyChart {{
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background: white;
        padding: 1rem;
    }}
    
    /* 로딩 스피너 스타일 */
    .stSpinner > div {{
        border-color: {UITheme.COLORS['primary']} transparent transparent transparent;
    }}
    
    /* 푸터 스타일 */
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: {UITheme.COLORS['dark']};
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)


def show_success_message(message: str, auto_hide: bool = True):
    """성공 메시지 표시"""
    if auto_hide:
        placeholder = st.empty()
        placeholder.success(f"✅ {message}")
        time.sleep(3)
        placeholder.empty()
    else:
        st.success(f"✅ {message}")


def show_error_message(message: str, auto_hide: bool = False):
    """에러 메시지 표시"""
    if auto_hide:
        placeholder = st.empty()
        placeholder.error(f"❌ {message}")
        time.sleep(5)
        placeholder.empty()
    else:
        st.error(f"❌ {message}")


def show_warning_message(message: str, auto_hide: bool = False):
    """경고 메시지 표시"""
    if auto_hide:
        placeholder = st.empty()
        placeholder.warning(f"⚠️ {message}")
        time.sleep(4)
        placeholder.empty()
    else:
        st.warning(f"⚠️ {message}")


def show_info_message(message: str, auto_hide: bool = False):
    """정보 메시지 표시"""
    if auto_hide:
        placeholder = st.empty()
        placeholder.info(f"ℹ️ {message}")
        time.sleep(3)
        placeholder.empty()
    else:
        st.info(f"ℹ️ {message}")


# 전역적으로 사용할 수 있는 인스턴스들
ui_theme = UITheme()
std_components = StandardComponents()
chart_components = ChartComponents()
form_components = FormComponents()
data_components = DataComponents()
layout_components = LayoutComponents()


if __name__ == "__main__":
    # 테스트 실행
    print("UI Components Module Loaded Successfully!") 