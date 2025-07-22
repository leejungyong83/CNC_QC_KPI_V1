import streamlit as st
import pandas as pd
import plotly.express as px
from utils.defect_utils import get_defect_type_names
from utils.supabase_client import get_supabase_client
import random

def show_dashboard():
    """KPI 대시보드 화면 표시"""
    st.header("📊 KPI 대시보드")
    
    # KPI 데이터 계산 (개선된 버전)
    kpi_data = calculate_kpi_data()
    
    # 데이터 상태에 따른 처리
    data_status = kpi_data.get('data_status', 'unknown')
    
    if data_status == 'no_data':
        st.warning("⚠️ 최근 30일간 검사 데이터가 없습니다.")
        st.info("💡 '📝 검사데이터입력' 메뉴에서 검사 실적을 추가하거나, Supabase에서 샘플 데이터를 생성하세요.")
        
        # 기본 KPI 카드 (0 값으로 표시)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="총 검사 건수 (30일)", value="0건", delta="데이터 없음")
        with col2:
            st.metric(label="불량률", value="0.000%", delta="데이터 없음")
        with col3:
            st.metric(label="평균 검사수량/건", value="0개", delta="데이터 없음")
        with col4:
            st.metric(label="검사 효율성", value="0.0%", delta="데이터 없음")
    
    elif data_status in ['table_missing', 'connection_error', 'unknown_error']:
        st.error(f"❌ 데이터 조회 실패: {kpi_data.get('error_message', '알 수 없는 오류')}")
        
        with st.expander("🔧 문제 해결 방법"):
            if data_status == 'table_missing':
                st.write("**테이블이 존재하지 않습니다.**")
                st.write("1. Supabase SQL Editor에서 `database_schema_unified.sql` 실행")
                st.write("2. 'Supabase 설정' 메뉴에서 데이터베이스 연결 확인")
            elif data_status == 'connection_error':
                st.write("**데이터베이스 연결 문제입니다.**")
                st.write("1. 네트워크 연결 상태 확인")
                st.write("2. Supabase 프로젝트 상태 확인")
                st.write("3. `.streamlit/secrets.toml` 파일의 연결 정보 확인")
            else:
                st.write("**일반적인 해결 방법:**")
                st.write("1. 'Supabase 설정' 메뉴에서 연결 테스트")
                st.write("2. 브라우저 새로고침")
                st.write("3. 잠시 후 다시 시도")
        
        # 기본 KPI 카드 (에러 상태 표시)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="총 검사 건수 (30일)", value="--", delta="연결 오류")
        with col2:
            st.metric(label="불량률", value="--", delta="연결 오류")
        with col3:
            st.metric(label="평균 검사수량/건", value="--", delta="연결 오류")
        with col4:
            st.metric(label="검사 효율성", value="--", delta="연결 오류")
    
    else:  # data_status == 'success'
        # 정상 데이터 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_inspections = kpi_data['total_inspections']
            avg_per_day = total_inspections / 30 if total_inspections > 0 else 0
            st.metric(
                label="총 검사 건수 (30일)", 
                value=f"{total_inspections:,}건",
                delta=f"{avg_per_day:.1f}건/일 평균"
            )
        
        with col2:
            defect_rate = kpi_data['defect_rate']
            target_defect_rate = 2.0  # 목표 불량률 2.0%
            delta_color = "normal" if defect_rate <= target_defect_rate else "inverse"
            st.metric(
                label="불량률", 
                value=f"{defect_rate:.3f}%",
                delta=f"목표 {target_defect_rate}% {'달성' if defect_rate <= target_defect_rate else '미달'}",
                delta_color=delta_color
            )
        
        with col3:
            total_qty = kpi_data['total_inspected_qty']
            avg_qty_per_inspection = total_qty / total_inspections if total_inspections > 0 else 0
            st.metric(
                label="평균 검사수량/건", 
                value=f"{avg_qty_per_inspection:.0f}개",
                delta=f"총 {total_qty:,}개 검사"
            )
        
        with col4:
            efficiency = kpi_data['inspection_efficiency']
            target_efficiency = 95.0  # 목표 검사효율 95%
            delta_color = "normal" if efficiency >= target_efficiency else "inverse"
            st.metric(
                label="검사 효율성 (건수기준)", 
                value=f"{efficiency:.1f}%",
                delta=f"목표 {target_efficiency}% {'달성' if efficiency >= target_efficiency else '미달'}",
                delta_color=delta_color
            )
        
        # 추가 KPI 정보 (수량 기준)
        if kpi_data.get('quantity_pass_rate', 0) > 0:
            st.info(f"📊 **수량 기준 합격률**: {kpi_data['quantity_pass_rate']:.1f}% (합격: {kpi_data['total_pass_qty']:,}개 / 총검사: {total_qty:,}개)")
    
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
        # 실제 데이터 조회
        performance_data = get_inspector_performance_data()
        
        if performance_data and len(performance_data) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # BEST 검사자 (첫 번째 = 합격률 최고)
                best_inspector = performance_data[0]
                st.success("🏅 **BEST 검사자**")
                st.write(f"👤 **{best_inspector['name']}** ({best_inspector['employee_id']})")
                st.write(f"✅ 합격률: **{best_inspector['pass_rate']:.1f}%**")
                st.write(f"📊 검사 건수: **{best_inspector['total_inspections']}건**")
                st.write(f"🎯 불량률: **{best_inspector['defect_rate']:.2f}%**")
            
            with col2:
                # WORST 검사자 (마지막 = 합격률 최저, 단 2명 이상인 경우만)
                if len(performance_data) > 1:
                    worst_inspector = performance_data[-1]
                    st.warning("📈 **개선 필요 검사자**")
                    st.write(f"👤 **{worst_inspector['name']}** ({worst_inspector['employee_id']})")
                    st.write(f"❌ 합격률: **{worst_inspector['pass_rate']:.1f}%**")
                    st.write(f"📊 검사 건수: **{worst_inspector['total_inspections']}건**")
                    st.write(f"🎯 불량률: **{worst_inspector['defect_rate']:.2f}%**")
                else:
                    st.info("📊 **단일 검사자**")
                    st.write("비교할 다른 검사자가 없습니다.")
            
            # 전체 검사자 성과 요약 (접을 수 있는 형태)
            if len(performance_data) > 2:
                with st.expander(f"📊 전체 검사자 성과 순위 ({len(performance_data)}명)"):
                    for i, data in enumerate(performance_data, 1):
                        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}위"
                        st.write(f"{rank_emoji} {data['name']} ({data['employee_id']}) - 합격률: {data['pass_rate']:.1f}%, 검사건수: {data['total_inspections']}건")
        else:
            # 실제 데이터가 없을 때 기본 안내
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("📊 **BEST 검사자**")
                st.write("검사 실적 데이터가 없습니다.")
                
            with col2:
                st.info("📊 **개선 필요 검사자**")
                st.write("검사 실적 데이터가 없습니다.")
            
            st.warning("⚠️ 검사자 성과를 확인하려면 검사 실적을 먼저 입력해주세요.")
            st.info("💡 '📝 검사데이터입력' 메뉴에서 검사 실적을 추가할 수 있습니다.")
            
    except Exception as e:
        st.error(f"❌ 검사자 성과 데이터 조회 중 오류: {str(e)}")
        
        # 에러 발생 시에도 기본 안내 제공
        with st.expander("🔧 문제 해결 방법"):
            st.write("**가능한 원인:**")
            st.write("- Supabase 데이터베이스 연결 문제")
            st.write("- inspectors 또는 inspection_data 테이블이 없음")
            st.write("- 검사 실적 데이터가 없음")
            st.write("")
            st.write("**해결 방법:**")
            st.write("1. 'Supabase 설정' 메뉴에서 데이터베이스 연결 확인")
            st.write("2. '검사자 등록 및 관리' 메뉴에서 검사자 등록")
            st.write("3. '📝 검사데이터입력' 메뉴에서 검사 실적 입력")

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
    """검사자별 성과 데이터 조회 - 성능 최적화된 버전"""
    # 성능 최적화된 버전 사용
    try:
        from utils.performance_optimizer import query_optimizer
        return query_optimizer.get_optimized_inspector_performance()
    except ImportError:
        # 폴백: 기존 방식
        return get_inspector_performance_data_fallback()

def get_inspector_performance_data_fallback():
    """검사자별 성과 데이터 조회 - 실제 데이터베이스에서 (기존 버전)"""
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
    """KPI 데이터 계산 - 성능 최적화된 버전"""
    # 성능 최적화된 버전 사용
    try:
        from utils.performance_optimizer import query_optimizer
        return query_optimizer.get_optimized_kpi_data()
    except ImportError:
        # 폴백: 기존 방식
        return calculate_kpi_data_fallback()

def calculate_kpi_data_fallback():
    """KPI 데이터 계산 - 실제 데이터베이스에서 (기존 버전)"""
    try:
        supabase = get_supabase_client()
        
        # 검사 데이터 조회 (최근 30일)
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 더 효율적인 쿼리: 필요한 컬럼만 조회
        inspection_result = supabase.table('inspection_data') \
            .select('result, total_inspected, defect_quantity, pass_quantity, quantity') \
            .gte('inspection_date', thirty_days_ago) \
            .execute()
        
        inspections = inspection_result.data if inspection_result.data else []
        
        # 데이터가 없을 때 기본값 반환 (에러 대신 정보성 메시지)
        if not inspections:
            return {
                'defect_rate': 0.0,
                'inspection_efficiency': 0.0,
                'total_inspections': 0,
                'pass_count': 0,
                'total_inspected_qty': 0,
                'total_defect_qty': 0,
                'data_status': 'no_data'
            }
        
        # KPI 계산 (개선된 로직)
        total_inspections = len(inspections)
        pass_count = 0
        total_inspected_qty = 0
        total_defect_qty = 0
        total_pass_qty = 0
        
        for inspection in inspections:
            # 합격 건수
            if inspection.get('result') == '합격':
                pass_count += 1
            
            # 수량 정보 (우선순위: total_inspected > quantity > 0)
            inspected_qty = inspection.get('total_inspected') or inspection.get('quantity') or 0
            defect_qty = inspection.get('defect_quantity') or 0
            pass_qty = inspection.get('pass_quantity') or 0
            
            # 데이터 정합성 체크
            if defect_qty > inspected_qty:
                defect_qty = inspected_qty  # 불량수량이 총 검사수량보다 클 수 없음
            
            if pass_qty == 0 and inspected_qty > 0:
                pass_qty = inspected_qty - defect_qty  # 합격수량이 없으면 계산
            
            total_inspected_qty += inspected_qty
            total_defect_qty += defect_qty
            total_pass_qty += pass_qty
        
        # KPI 계산 (개선된 공식)
        # 1. 불량률: 불량 수량 / 총 검사 수량 * 100
        defect_rate = (total_defect_qty / total_inspected_qty * 100) if total_inspected_qty > 0 else 0.0
        
        # 2. 검사효율성: 합격 건수 / 총 검사 건수 * 100 (건수 기준)
        inspection_efficiency = (pass_count / total_inspections * 100) if total_inspections > 0 else 0.0
        
        # 3. 수량 기준 합격률: 합격 수량 / 총 검사 수량 * 100
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
        # 에러 상황에서도 기본 구조 유지
        error_msg = str(e)
        
        # 연결 문제인지 데이터 문제인지 구분
        if "does not exist" in error_msg:
            data_status = 'table_missing'
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            data_status = 'connection_error'
        else:
            data_status = 'unknown_error'
        
        return {
            'defect_rate': 0.0,
            'inspection_efficiency': 0.0,
            'quantity_pass_rate': 0.0,
            'total_inspections': 0,
            'pass_count': 0,
            'total_inspected_qty': 0,
            'total_defect_qty': 0,
            'total_pass_qty': 0,
            'data_status': data_status,
            'error_message': error_msg
        } 