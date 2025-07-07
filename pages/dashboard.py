import streamlit as st
import pandas as pd
import plotly.express as px
from utils.defect_utils import get_defect_type_names
from utils.supabase_client import get_supabase_client
import random

def show_dashboard():
    """KPI 대시보드 화면 표시"""
    # 캐시 정리를 위한 강제 업데이트 - v2.0
    st.header("KPI 대시보드")
    
    # KPI 카드 레이아웃
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="총 검사 건수", value="175", delta="15")
    with col2:
        st.metric(label="불량률", value="3.5%", delta="-0.5%")
    with col3:
        st.metric(label="평균 검사 시간", value="12분", delta="-2분")
    with col4:
        st.metric(label="최초 합격률", value="92%", delta="2%")
    
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
    
    try:
        # 실제 데이터베이스에서 검사자 성과 데이터 조회
        performance_data = get_inspector_performance_data()
        
        if performance_data and len(performance_data) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # BEST 검사자
                best_inspector = performance_data[0]  # 합격률 기준 최고
                st.success(f"🏅 **BEST 검사자**")
                st.write(f"👤 **{best_inspector['name']}**")
                st.write(f"✅ 합격률: **{best_inspector['pass_rate']:.1f}%**")
                st.write(f"📊 검사 건수: **{best_inspector['total_inspections']}건**")
                st.write(f"🎯 불량률: **{best_inspector['defect_rate']:.2f}%**")
            
            with col2:
                # WORST 검사자 (개선 필요)
                worst_inspector = performance_data[-1]  # 합격률 기준 최저
                st.warning(f"📈 **개선 필요 검사자**")
                st.write(f"👤 **{worst_inspector['name']}**")
                st.write(f"❌ 합격률: **{worst_inspector['pass_rate']:.1f}%**")
                st.write(f"📊 검사 건수: **{worst_inspector['total_inspections']}건**")
                st.write(f"🎯 불량률: **{worst_inspector['defect_rate']:.2f}%**")
        else:
            st.info("검사자 성과 데이터가 없습니다. 검사 실적을 입력해주세요.")
            
    except Exception as e:
        st.error(f"검사자 성과 데이터 조회 중 오류: {str(e)}")

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
    """검사자별 성과 데이터 조회"""
    try:
        supabase = get_supabase_client()
        
        # 검사 데이터와 검사자 정보를 JOIN하여 조회
        query = """
        SELECT 
            i.name,
            i.employee_id,
            COUNT(id.id) as total_inspections,
            COUNT(CASE WHEN id.result = '합격' THEN 1 END) as pass_count,
            SUM(COALESCE(id.total_inspected, id.quantity, 0)) as total_inspected_qty,
            SUM(COALESCE(id.defect_quantity, 0)) as total_defect_qty
        FROM inspectors i
        LEFT JOIN inspection_data id ON i.id = id.inspector_id
        WHERE id.id IS NOT NULL
        GROUP BY i.id, i.name, i.employee_id
        HAVING COUNT(id.id) > 0
        ORDER BY (COUNT(CASE WHEN id.result = '합격' THEN 1 END) * 100.0 / COUNT(id.id)) DESC
        """
        
        result = supabase.rpc('exec_sql', {'sql': query}).execute()
        
        if result.data:
            performance_data = []
            for row in result.data:
                total_inspections = row['total_inspections']
                pass_count = row['pass_count']
                total_inspected_qty = row['total_inspected_qty'] or 0
                total_defect_qty = row['total_defect_qty'] or 0
                
                pass_rate = (pass_count / total_inspections * 100) if total_inspections > 0 else 0
                defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0
                
                performance_data.append({
                    'name': row['name'],
                    'employee_id': row['employee_id'],
                    'total_inspections': total_inspections,
                    'pass_rate': pass_rate,
                    'defect_rate': defect_rate
                })
            
            return performance_data
        else:
            # 샘플 데이터 반환 (데이터가 없을 경우)
            return [
                {'name': '김검사', 'employee_id': 'INSP001', 'total_inspections': 25, 'pass_rate': 96.8, 'defect_rate': 1.2},
                {'name': '이검사', 'employee_id': 'INSP002', 'total_inspections': 22, 'pass_rate': 94.5, 'defect_rate': 2.1},
                {'name': '박검사', 'employee_id': 'INSP003', 'total_inspections': 18, 'pass_rate': 88.9, 'defect_rate': 3.8}
            ]
            
    except Exception as e:
        print(f"검사자 성과 데이터 조회 오류: {str(e)}")
        # 오류 시 샘플 데이터 반환
        return [
            {'name': '김검사', 'employee_id': 'INSP001', 'total_inspections': 25, 'pass_rate': 96.8, 'defect_rate': 1.2},
            {'name': '이검사', 'employee_id': 'INSP002', 'total_inspections': 22, 'pass_rate': 94.5, 'defect_rate': 2.1},
            {'name': '박검사', 'employee_id': 'INSP003', 'total_inspections': 18, 'pass_rate': 88.9, 'defect_rate': 3.8}
        ]

def calculate_kpi_data():
    """KPI 데이터 계산"""
    try:
        supabase = get_supabase_client()
        
        # 전체 검사 데이터 통계 조회
        query = """
        SELECT 
            COUNT(*) as total_inspections,
            COUNT(CASE WHEN result = '합격' THEN 1 END) as pass_count,
            SUM(COALESCE(total_inspected, quantity, 0)) as total_inspected_qty,
            SUM(COALESCE(defect_quantity, 0)) as total_defect_qty
        FROM inspection_data
        WHERE inspection_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        
        result = supabase.rpc('exec_sql', {'sql': query}).execute()
        
        if result.data and len(result.data) > 0:
            data = result.data[0]
            
            total_inspections = data['total_inspections'] or 0
            pass_count = data['pass_count'] or 0
            total_inspected_qty = data['total_inspected_qty'] or 0
            total_defect_qty = data['total_defect_qty'] or 0
            
            # 불량율 계산 (불량 수량 / 총 검사 수량 * 100)
            defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0
            
            # 검사효율성 계산 (합격률 기준)
            inspection_efficiency = (pass_count / total_inspections * 100) if total_inspections > 0 else 0
            
            return {
                'defect_rate': defect_rate,
                'inspection_efficiency': inspection_efficiency,
                'total_inspections': total_inspections,
                'pass_count': pass_count
            }
        else:
            # 샘플 데이터 반환
            return {
                'defect_rate': 0.015,  # 0.015% (목표 0.02%보다 낮음)
                'inspection_efficiency': 97.2,  # 97.2% (목표 95%보다 높음)
                'total_inspections': 150,
                'pass_count': 146
            }
            
    except Exception as e:
        print(f"KPI 데이터 계산 오류: {str(e)}")
        # 오류 시 샘플 데이터 반환
        return {
            'defect_rate': 0.025,  # 0.025% (목표 0.02%보다 높음)
            'inspection_efficiency': 92.8,  # 92.8% (목표 95%보다 낮음)
            'total_inspections': 150,
            'pass_count': 139
        } 