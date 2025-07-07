import streamlit as st
import pandas as pd
import plotly.express as px
from utils.defect_utils import get_defect_type_names
from utils.supabase_client import get_supabase_client
import random

def show_dashboard():
    """KPI 대시보드 화면 표시"""
    # 캐시 정리를 위한 강제 업데이트 - v3.0 FINAL
    st.header("KPI 대시보드")
    
    # KPI 카드 레이아웃 - 실제 데이터 사용
    kpi_data = calculate_kpi_data()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="총 검사 건수 (30일)", 
            value=f"{kpi_data['total_inspections']}건",
            delta=f"+{kpi_data['total_inspections']//30}건/일 평균"
        )
    with col2:
        defect_rate = kpi_data['defect_rate']
        delta_color = "normal" if defect_rate <= 0.02 else "inverse"
        st.metric(
            label="불량률", 
            value=f"{defect_rate:.3f}%",
            delta=f"목표 0.02% {'달성' if defect_rate <= 0.02 else '미달'}",
            delta_color=delta_color
        )
    with col3:
        total_qty = kpi_data.get('total_inspected_qty', 0)
        avg_qty_per_inspection = total_qty / kpi_data['total_inspections'] if kpi_data['total_inspections'] > 0 else 0
        st.metric(
            label="평균 검사수량/건", 
            value=f"{avg_qty_per_inspection:.0f}개",
            delta=f"총 {total_qty}개 검사"
        )
    with col4:
        efficiency = kpi_data['inspection_efficiency']
        delta_color = "normal" if efficiency >= 95.0 else "inverse"
        st.metric(
            label="검사 효율성", 
            value=f"{efficiency:.1f}%",
            delta=f"목표 95% {'달성' if efficiency >= 95.0 else '미달'}",
            delta_color=delta_color
        )
    
    # BEST/WORST 검사자 섹션 추가
    st.markdown("---")
    show_inspector_performance()
    
    # 기간 선택기
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "기간 선택",
            ["일별", "주별", "월별"]
        )
    with col2:
        date_range = st.date_input(
            "날짜 범위",
            [pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now()]
        )
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["검사 현황", "불량 현황", "설비별 현황", "모델별 현황"])
    
    with tab1:
        st.subheader("검사 건수 추이")
        # 검사 건수 데이터 (예시)
        chart_data = pd.DataFrame({
            "날짜": pd.date_range(start="2023-01-01", periods=30),
            "검사 건수": [40, 42, 45, 47, 38, 39, 41, 43, 46, 48, 
                      50, 49, 47, 45, 43, 44, 45, 47, 49, 51,
                      50, 48, 46, 45, 44, 46, 48, 49, 50, 52]
        })
        fig = px.line(chart_data, x="날짜", y="검사 건수", title="일별 검사 건수")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.subheader("불량률 추이")
        # 불량률 데이터 (예시)
        chart_data = pd.DataFrame({
            "날짜": pd.date_range(start="2023-01-01", periods=30),
            "불량률": [4.0, 3.9, 4.2, 3.8, 3.7, 3.6, 3.3, 3.5, 3.6, 3.4, 
                     3.2, 3.5, 3.6, 3.7, 3.8, 3.6, 3.5, 3.4, 3.3, 3.4,
                     3.5, 3.6, 3.5, 3.4, 3.3, 3.2, 3.3, 3.4, 3.5, 3.4]
        })
        fig = px.line(chart_data, x="날짜", y="불량률", title="일별 불량률")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("주요 불량 유형")
        # 불량 유형 데이터베이스에서 가져오기
        defect_types = get_defect_type_names()
        
        # 각 불량 유형별 임의의 발생 건수 생성 (데모용)
        defect_counts = [random.randint(3, 15) for _ in range(len(defect_types))]
        
        # DataFrame 생성
        defect_data = pd.DataFrame({
            "불량 유형": defect_types,
            "발생 건수": defect_counts
        })
        
        # 발생 건수 기준으로 내림차순 정렬
        defect_data = defect_data.sort_values(by="발생 건수", ascending=False).reset_index(drop=True)
        
        fig = px.bar(defect_data, x="불량 유형", y="발생 건수", title="불량 유형별 발생 건수")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab3:
        st.subheader("설비별 검사 현황")
        # 설비별 데이터 (예시)
        equipment_data = pd.DataFrame({
            "설비": ["설비1", "설비2", "설비3", "설비4", "설비5"],
            "검사 건수": [45, 38, 42, 36, 30],
            "불량 건수": [2, 3, 1, 1, 2],
            "불량률": [4.4, 7.9, 2.4, 2.8, 6.7]
        })
        st.dataframe(equipment_data, use_container_width=True)
        
        fig = px.bar(equipment_data, x="설비", y="불량률", title="설비별 불량률")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("모델별 검사 현황")
        # 모델별 데이터 (예시)
        model_data = pd.DataFrame({
            "모델": ["모델A", "모델B", "모델C", "모델D", "모델E"],
            "검사 건수": [50, 42, 38, 25, 20],
            "불량 건수": [3, 2, 3, 1, 1],
            "불량률": [6.0, 4.8, 7.9, 4.0, 5.0]
        })
        st.dataframe(model_data, use_container_width=True)
        
        fig = px.bar(model_data, x="모델", y="불량률", title="모델별 불량률")
        st.plotly_chart(fig, use_container_width=True)
    
    # KPI 알림 섹션 추가
    st.markdown("---")
    show_kpi_alerts()

def show_inspector_performance():
    """BEST/WORST 검사자 성과 표시"""
    st.subheader("🏆 검사자 성과")
    
    # 단순한 테스트부터 - 일단 화면에 나타나는지 확인
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🏅 **BEST 검사자**")
        st.write("👤 **김우수검사** (INSP001)")
        st.write("✅ 합격률: **98.5%**")
        st.write("📊 검사 건수: **25건**")
        st.write("🎯 불량률: **0.8%**")
    
    with col2:
        st.warning("📈 **개선 필요 검사자**")
        st.write("👤 **이개선검사** (INSP003)")
        st.write("❌ 합격률: **85.2%**")
        st.write("📊 검사 건수: **18건**")
        st.write("🎯 불량률: **4.2%**")
    
    # 실제 데이터 조회 시도 (에러 발생해도 위의 고정 데이터는 표시됨)
    with st.expander("🔍 실제 데이터 조회 상태"):
        try:
            performance_data = get_inspector_performance_data()
            if performance_data:
                st.success(f"✅ 실제 데이터 {len(performance_data)}명 조회 성공!")
                for data in performance_data:
                    st.write(f"- {data['name']}: 합격률 {data['pass_rate']:.1f}%")
            else:
                st.warning("⚠️ 실제 데이터가 없습니다.")
        except Exception as e:
            st.error(f"❌ 실제 데이터 조회 실패: {str(e)}")

def show_kpi_alerts():
    """KPI 알림 표시"""
    st.subheader("🚨 KPI 알림")
    
    try:
        # 실제 KPI 데이터 계산
        kpi_data = calculate_kpi_data()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 불량율 KPI
            current_defect_rate = kpi_data['defect_rate']
            target_defect_rate = 0.02  # 목표 불량율 0.02%
            
            if current_defect_rate <= target_defect_rate:
                st.success(f"✅ **불량율 목표 달성**")
                st.write(f"🎯 목표: **{target_defect_rate}%**")
                st.write(f"📊 현재: **{current_defect_rate:.3f}%**")
                st.write(f"📈 달성률: **{((target_defect_rate - current_defect_rate) / target_defect_rate * 100):.1f}% 초과 달성**")
            else:
                st.error(f"❌ **불량율 목표 미달성**")
                st.write(f"🎯 목표: **{target_defect_rate}%**")
                st.write(f"📊 현재: **{current_defect_rate:.3f}%**")
                st.write(f"⚠️ 개선 필요: **{(current_defect_rate - target_defect_rate):.3f}%p**")
        
        with col2:
            # 검사효율성 KPI
            current_efficiency = kpi_data['inspection_efficiency']
            target_efficiency = 95.0  # 목표 검사효율 95%
            
            if current_efficiency >= target_efficiency:
                st.success(f"✅ **검사효율성 목표 달성**")
                st.write(f"🎯 목표: **{target_efficiency}%**")
                st.write(f"📊 현재: **{current_efficiency:.1f}%**")
                st.write(f"📈 달성률: **{(current_efficiency / target_efficiency * 100):.1f}%**")
            else:
                st.warning(f"⚠️ **검사효율성 목표 미달성**")
                st.write(f"🎯 목표: **{target_efficiency}%**")
                st.write(f"📊 현재: **{current_efficiency:.1f}%**")
                st.write(f"📉 부족분: **{(target_efficiency - current_efficiency):.1f}%p**")
                
    except Exception as e:
        st.error(f"KPI 데이터 계산 중 오류: {str(e)}")

def get_inspector_performance_data():
    """검사자별 성과 데이터 조회 - 실제 데이터베이스에서"""
    try:
        supabase = get_supabase_client()
        
        # 1. 검사 데이터 조회
        inspection_result = supabase.table('inspection_data').select('*').execute()
        inspections = inspection_result.data if inspection_result.data else []
        
        # 2. 검사자 정보 조회
        inspectors_result = supabase.table('inspectors').select('*').execute()
        inspectors = {insp['id']: insp for insp in inspectors_result.data} if inspectors_result.data else {}
        
        if not inspections or not inspectors:
            return None
        
        # 3. 검사자별 성과 계산
        inspector_stats = {}
        
        for inspection in inspections:
            inspector_id = inspection.get('inspector_id')
            if not inspector_id or inspector_id not in inspectors:
                continue
                
            if inspector_id not in inspector_stats:
                inspector_stats[inspector_id] = {
                    'name': inspectors[inspector_id]['name'],
                    'employee_id': inspectors[inspector_id].get('employee_id', 'N/A'),
                    'total_inspections': 0,
                    'pass_count': 0,
                    'total_inspected_qty': 0,
                    'total_defect_qty': 0
                }
            
            stats = inspector_stats[inspector_id]
            stats['total_inspections'] += 1
            
            if inspection.get('result') == '합격':
                stats['pass_count'] += 1
            
            # 수량 정보
            inspected_qty = inspection.get('total_inspected') or inspection.get('quantity') or 0
            defect_qty = inspection.get('defect_quantity') or 0
            
            stats['total_inspected_qty'] += inspected_qty
            stats['total_defect_qty'] += defect_qty
        
        # 4. 성과 지표 계산 및 정렬
        performance_data = []
        for inspector_id, stats in inspector_stats.items():
            if stats['total_inspections'] > 0:
                pass_rate = (stats['pass_count'] / stats['total_inspections']) * 100
                defect_rate = (stats['total_defect_qty'] / stats['total_inspected_qty'] * 100) if stats['total_inspected_qty'] > 0 else 0
                
                performance_data.append({
                    'name': stats['name'],
                    'employee_id': stats['employee_id'],
                    'total_inspections': stats['total_inspections'],
                    'pass_rate': pass_rate,
                    'defect_rate': defect_rate
                })
        
        # 합격률 기준으로 내림차순 정렬
        performance_data.sort(key=lambda x: x['pass_rate'], reverse=True)
        
        return performance_data if performance_data else None
        
    except Exception as e:
        st.error(f"검사자 성과 데이터 조회 실패: {str(e)}")
        return None

def calculate_kpi_data():
    """KPI 데이터 계산 - 실제 데이터베이스에서"""
    try:
        supabase = get_supabase_client()
        
        # 검사 데이터 조회 (최근 30일)
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        inspection_result = supabase.table('inspection_data') \
            .select('*') \
            .gte('inspection_date', thirty_days_ago) \
            .execute()
        
        inspections = inspection_result.data if inspection_result.data else []
        
        if not inspections:
            return {
                'defect_rate': 0.0,
                'inspection_efficiency': 0.0,
                'total_inspections': 0,
                'pass_count': 0
            }
        
        # KPI 계산
        total_inspections = len(inspections)
        pass_count = 0
        total_inspected_qty = 0
        total_defect_qty = 0
        
        for inspection in inspections:
            # 합격 건수
            if inspection.get('result') == '합격':
                pass_count += 1
            
            # 수량 정보
            inspected_qty = inspection.get('total_inspected') or inspection.get('quantity') or 0
            defect_qty = inspection.get('defect_quantity') or 0
            
            total_inspected_qty += inspected_qty
            total_defect_qty += defect_qty
        
        # 불량률 계산 (불량 수량 / 총 검사 수량 * 100)
        defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
        
        # 검사효율성 계산 (합격률)
        inspection_efficiency = (pass_count / total_inspections * 100) if total_inspections > 0 else 0.0
        
        return {
            'defect_rate': defect_rate,
            'inspection_efficiency': inspection_efficiency,
            'total_inspections': total_inspections,
            'pass_count': pass_count,
            'total_inspected_qty': total_inspected_qty,
            'total_defect_qty': total_defect_qty
        }
        
    except Exception as e:
        st.error(f"KPI 데이터 계산 실패: {str(e)}")
        return {
            'defect_rate': 0.0,
            'inspection_efficiency': 0.0,
            'total_inspections': 0,
            'pass_count': 0
        } 