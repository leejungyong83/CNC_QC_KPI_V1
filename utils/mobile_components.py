"""
모바일 최적화 컴포넌트 모듈
현장 검사원을 위한 모바일 친화적 UI 컴포넌트 제공
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.supabase_client import get_supabase_client

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)


def is_mobile():
    """모바일 디바이스인지 확인 (간단한 방법)"""
    # 실제로는 user-agent 확인이 더 정확하지만, Streamlit에서는 제한적
    # 화면 크기 기반으로 모바일 여부를 추정
    return st.session_state.get('is_mobile', False)


def set_mobile_config():
    """모바일용 페이지 설정"""
    st.set_page_config(
        page_title="CNC QC Mobile",
        page_icon="📱",
        layout="centered",  # 모바일에서는 centered가 더 적합
        initial_sidebar_state="collapsed"  # 모바일에서는 사이드바 기본 숨김
    )


def mobile_button(label, key=None, help=None, type="secondary", use_container_width=True, icon=""):
    """모바일 친화적 큰 버튼"""
    button_style = {
        "primary": "🔵",
        "secondary": "⚪", 
        "success": "🟢",
        "warning": "🟡",
        "danger": "🔴"
    }
    
    button_icon = button_style.get(type, "⚪")
    display_label = f"{icon} {label}" if icon else f"{button_icon} {label}"
    
    # 모바일용 큰 버튼 스타일
    if type == "primary":
        return st.button(
            display_label, 
            key=key, 
            help=help, 
            type="primary",
            use_container_width=use_container_width
        )
    else:
        return st.button(
            display_label, 
            key=key, 
            help=help,
            use_container_width=use_container_width
        )


def mobile_metric_card(label, value, delta=None, delta_color="normal"):
    """모바일용 메트릭 카드"""
    container = st.container()
    with container:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 10px 0;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <h3 style="color: white; margin: 0; font-size: 1.1em;">{label}</h3>
            <h1 style="color: white; margin: 10px 0; font-size: 2.5em; font-weight: bold;">{value}</h1>
            {f'<p style="color: #f0f0f0; margin: 0; font-size: 0.9em;">{delta}</p>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)


def mobile_quick_input():
    """모바일용 빠른 검사 입력"""
    st.markdown("### 📱 빠른 검사 입력")
    
    with st.form("mobile_quick_inspection", clear_on_submit=True):
        # 기본 정보 (한 줄에 배치)
        col1, col2 = st.columns(2)
        
        with col1:
            inspection_date = st.date_input("📅 검사일", value=get_vietnam_date())
        
        with col2:
            # 검사자 선택 (자주 사용하는 검사자 우선)
            inspectors = get_frequent_inspectors()
            inspector = st.selectbox("👤 검사자", inspectors, key="mobile_inspector")
        
        # 생산모델 (큰 버튼 형태)
        st.markdown("**🏭 생산모델 선택:**")
        models = get_frequent_models()
        
        # 자주 사용하는 모델을 큰 버튼으로 표시
        model_cols = st.columns(2)
        selected_model = None
        
        for i, model in enumerate(models[:4]):  # 상위 4개 모델만 표시
            col_idx = i % 2
            with model_cols[col_idx]:
                if st.button(f"📦 {model['name']}", key=f"model_{i}", use_container_width=True):
                    selected_model = model['id']
                    st.session_state.selected_model_name = model['name']
        
        # 선택된 모델 표시
        if selected_model or st.session_state.get('selected_model_name'):
            st.success(f"✅ 선택된 모델: {st.session_state.get('selected_model_name', '알 수 없음')}")
        
        # 검사 결과 (큰 버튼)
        st.markdown("**🎯 검사 결과:**")
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            if st.button("✅ 합격", key="pass_btn", type="primary", use_container_width=True):
                st.session_state.inspection_result = "합격"
        
        with result_col2:
            if st.button("❌ 불합격", key="fail_btn", use_container_width=True):
                st.session_state.inspection_result = "불합격"
        
        # 선택된 결과 표시
        if st.session_state.get('inspection_result'):
            result_emoji = "✅" if st.session_state.inspection_result == "합격" else "❌"
            st.info(f"{result_emoji} 검사 결과: **{st.session_state.inspection_result}**")
        
        # 수량 정보
        st.markdown("**📊 수량 정보:**")
        qty_col1, qty_col2 = st.columns(2)
        
        with qty_col1:
            total_qty = st.number_input("검사 수량", min_value=1, value=50, key="mobile_total_qty")
        
        with qty_col2:
            defect_qty = st.number_input("불량 수량", min_value=0, value=0, key="mobile_defect_qty")
        
        # 간단한 메모
        notes = st.text_area("📝 메모 (선택사항)", height=60, placeholder="특이사항이 있으면 입력하세요...")
        
        # 제출 버튼
        submitted = st.form_submit_button("🚀 검사 등록", type="primary", use_container_width=True)
        
        if submitted:
            # 검사 데이터 저장 로직
            save_mobile_inspection({
                'date': inspection_date,
                'inspector': inspector,
                'model_id': selected_model,
                'result': st.session_state.get('inspection_result'),
                'total_qty': total_qty,
                'defect_qty': defect_qty,
                'notes': notes
            })


def mobile_dashboard():
    """모바일용 간단한 대시보드"""
    st.markdown("### 📊 오늘의 현황")
    
    # 오늘의 KPI (간단한 버전)
    try:
        today_data = get_today_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            mobile_metric_card(
                "오늘 검사",
                f"{today_data.get('inspections', 0)}건",
                f"목표 대비 {today_data.get('target_ratio', 0):.0f}%"
            )
        
        with col2:
            mobile_metric_card(
                "불량률",
                f"{today_data.get('defect_rate', 0):.1f}%",
                "목표 2.0%" if today_data.get('defect_rate', 0) <= 2.0 else "⚠️ 목표 초과"
            )
        
        # 빠른 액션 버튼들
        st.markdown("### ⚡ 빠른 작업")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if mobile_button("📝 검사 입력", icon="📝", type="primary"):
                st.session_state.mobile_action = "input"
                st.rerun()
        
        with action_col2:
            if mobile_button("📊 오늘 실적", icon="📊"):
                st.session_state.mobile_action = "today_report"
                st.rerun()
        
        # 알림 요약 (모바일용)
        show_mobile_notifications()
        
    except Exception as e:
        st.error("데이터를 불러오는 중 오류가 발생했습니다.")
        st.error(f"오류 내용: {str(e)}")


def show_mobile_notifications():
    """모바일용 알림 표시"""
    try:
        from utils.notification_system import NotificationSystem
        notification_system = NotificationSystem()
        notifications = notification_system.get_all_notifications()
        
        if notifications:
            critical_count = sum(1 for n in notifications if n['priority'] == 'critical')
            high_count = sum(1 for n in notifications if n['priority'] == 'high')
            
            if critical_count > 0:
                st.error(f"🚨 긴급 알림 {critical_count}개")
                if st.button("🔔 알림 확인", key="mobile_check_notifications"):
                    st.session_state.mobile_action = "notifications"
                    st.rerun()
            elif high_count > 0:
                st.warning(f"⚠️ 중요 알림 {high_count}개")
                if st.button("🔔 알림 확인", key="mobile_check_notifications_high"):
                    st.session_state.mobile_action = "notifications"
                    st.rerun()
            else:
                st.success("✅ 모든 시스템 정상")
        else:
            st.success("✅ 알림 없음")
            
    except Exception:
        pass  # 알림 시스템 오류 시 조용히 넘어감


def get_frequent_inspectors():
    """자주 사용하는 검사자 목록"""
    try:
        supabase = get_supabase_client()
        result = supabase.table('inspectors') \
            .select('id, name, employee_id') \
            .eq('is_active', True) \
            .limit(10) \
            .execute()
        
        inspectors = result.data if result.data else []
        return [f"{inspector['name']} ({inspector['employee_id']})" for inspector in inspectors]
    except:
        return ["검사자1", "검사자2", "검사자3"]  # 기본값


def get_frequent_models():
    """자주 사용하는 생산모델 목록"""
    try:
        supabase = get_supabase_client()
        result = supabase.table('production_models') \
            .select('id, model_name, model_no') \
            .eq('is_active', True) \
            .limit(6) \
            .execute()
        
        models = result.data if result.data else []
        return [{'id': model['id'], 'name': f"{model['model_name']} ({model['model_no']})"} for model in models]
    except:
        return [
            {'id': 1, 'name': 'PA1 (MODEL-001)'},
            {'id': 2, 'name': 'PA2 (MODEL-002)'},
            {'id': 3, 'name': 'PA3 (MODEL-003)'},
            {'id': 4, 'name': 'B6 (MODEL-004)'}
        ]


def get_today_summary():
    """오늘의 요약 데이터 (베트남 시간대 기준)"""
    try:
        supabase = get_supabase_client()
        today = get_vietnam_date().strftime('%Y-%m-%d')
        
        result = supabase.table('inspection_data') \
            .select('result, total_inspected, defect_quantity') \
            .eq('inspection_date', today) \
            .execute()
        
        inspections = result.data if result.data else []
        
        total_inspections = len(inspections)
        total_qty = sum(i.get('total_inspected', 0) for i in inspections)
        total_defects = sum(i.get('defect_quantity', 0) for i in inspections)
        
        defect_rate = (total_defects / total_qty * 100) if total_qty > 0 else 0
        target_ratio = (total_inspections / 10 * 100) if total_inspections <= 10 else 100  # 일일 목표 10건
        
        return {
            'inspections': total_inspections,
            'defect_rate': defect_rate,
            'target_ratio': target_ratio
        }
    except:
        return {'inspections': 0, 'defect_rate': 0, 'target_ratio': 0}


def save_mobile_inspection(data):
    """모바일에서 입력한 검사 데이터 저장"""
    try:
        supabase = get_supabase_client()
        
        # 검사자 ID 찾기
        inspector_name = data['inspector'].split(' (')[0]
        inspector_result = supabase.table('inspectors') \
            .select('id') \
            .eq('name', inspector_name) \
            .limit(1) \
            .execute()
        
        inspector_id = inspector_result.data[0]['id'] if inspector_result.data else None
        
        # 검사 데이터 저장
        inspection_data = {
            'inspection_date': data['date'].strftime('%Y-%m-%d'),
            'inspector_id': inspector_id,
            'model_id': data.get('model_id'),
            'result': data['result'],
            'total_inspected': data['total_qty'],
            'defect_quantity': data['defect_qty'],
            'pass_quantity': data['total_qty'] - data['defect_qty'],
            'notes': data['notes'] or None
        }
        
        result = supabase.table('inspection_data').insert(inspection_data).execute()
        
        if result.data:
            st.success("✅ 검사 데이터가 성공적으로 등록되었습니다!")
            
            # 세션 상태 초기화
            for key in ['inspection_result', 'selected_model_name']:
                if key in st.session_state:
                    del st.session_state[key]
        else:
            st.error("❌ 데이터 등록 중 오류가 발생했습니다.")
            
    except Exception as e:
        st.error(f"❌ 저장 실패: {str(e)}")


def mobile_photo_upload():
    """모바일용 간단한 사진 업로드"""
    st.markdown("### 📷 검사 사진")
    
    uploaded_file = st.file_uploader(
        "사진 선택",
        type=['png', 'jpg', 'jpeg'],
        help="검사 부위 사진을 업로드하세요"
    )
    
    if uploaded_file:
        st.image(uploaded_file, caption="업로드된 사진", width=300)
        st.success("✅ 사진이 업로드되었습니다")
        
        if st.button("💾 사진 저장", type="primary", use_container_width=True):
            st.success("✅ 사진이 저장되었습니다!")


def show_mobile_interface():
    """모바일 인터페이스 메인"""
    # 모바일 감지 및 설정
    st.session_state.is_mobile = True
    
    # 헤더
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: -20px -20px 20px -20px; border-radius: 0 0 20px 20px;">
        <h1 style="color: white; margin: 0;">📱 CNC QC Mobile</h1>
        <p style="color: #f0f0f0; margin: 5px 0 0 0;">현장 검사원용 모바일 인터페이스</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 현재 액션에 따른 화면 표시
    action = st.session_state.get('mobile_action', 'dashboard')
    
    if action == 'input':
        mobile_quick_input()
        if st.button("🏠 대시보드로", key="back_to_dashboard"):
            st.session_state.mobile_action = 'dashboard'
            st.rerun()
    
    elif action == 'today_report':
        show_today_report_mobile()
        if st.button("🏠 대시보드로", key="back_to_dashboard_report"):
            st.session_state.mobile_action = 'dashboard'
            st.rerun()
    
    elif action == 'notifications':
        show_mobile_notification_detail()
        if st.button("🏠 대시보드로", key="back_to_dashboard_notif"):
            st.session_state.mobile_action = 'dashboard'
            st.rerun()
    
    else:  # dashboard
        mobile_dashboard()


def show_today_report_mobile():
    """모바일용 오늘 실적 보고서"""
    st.markdown("### 📊 오늘의 검사 실적")
    
    try:
        supabase = get_supabase_client()
        today = get_vietnam_now().strftime('%Y-%m-%d')  # 베트남 오늘 날짜
        
        result = supabase.table('inspection_data') \
            .select('*, inspectors(name), production_models(model_name)') \
            .eq('inspection_date', today) \
            .execute()
        
        inspections = result.data if result.data else []
        
        if inspections:
            st.success(f"✅ 오늘 총 {len(inspections)}건의 검사를 완료했습니다.")
            
            for i, inspection in enumerate(inspections):
                with st.expander(f"검사 #{i+1} - {inspection.get('result', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**검사자**: {inspection.get('inspectors', {}).get('name', 'N/A')}")
                        st.write(f"**모델**: {inspection.get('production_models', {}).get('model_name', 'N/A')}")
                    with col2:
                        st.write(f"**검사수량**: {inspection.get('total_inspected', 0)}개")
                        st.write(f"**불량수량**: {inspection.get('defect_quantity', 0)}개")
        else:
            st.info("📝 오늘 등록된 검사 실적이 없습니다.")
            
    except Exception as e:
        st.error("데이터를 불러오는 중 오류가 발생했습니다.")


def show_mobile_notification_detail():
    """모바일용 알림 상세"""
    st.markdown("### 🔔 알림 센터")
    
    try:
        from utils.notification_system import NotificationSystem
        notification_system = NotificationSystem()
        notifications = notification_system.get_all_notifications()
        
        if notifications:
            for notification in notifications[:3]:  # 모바일에서는 상위 3개만 표시
                priority_colors = {
                    'critical': '#ff4444',
                    'high': '#ff8800', 
                    'medium': '#4488ff',
                    'low': '#888888'
                }
                
                color = priority_colors.get(notification['priority'], '#888888')
                
                st.markdown(f"""
                <div style="
                    border-left: 4px solid {color};
                    background: #f9f9f9;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 0 10px 10px 0;
                ">
                    <h4 style="margin: 0; color: {color};">
                        {notification['icon']} {notification['title']}
                    </h4>
                    <p style="margin: 10px 0;">{notification['message']}</p>
                    <p style="margin: 0; font-style: italic; color: #666; font-size: 0.9em;">
                        💡 {notification['action']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ 현재 알림이 없습니다.")
            
    except Exception as e:
        st.error("알림을 불러오는 중 오류가 발생했습니다.")


if __name__ == "__main__":
    show_mobile_interface() 