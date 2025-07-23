"""
고급 분석 기능 모듈
트렌드 분석, 예측 분석, 통계적 공정 관리(SPC) 기능 제공
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 베트남 시간대 유틸리티 import
from utils.vietnam_timezone import (
    get_vietnam_now, get_vietnam_date, 
    convert_utc_to_vietnam, get_database_time,
    get_vietnam_display_time
)

# 선택적 import - scipy가 없어도 기본 기능은 작동하도록 함
try:
    from scipy import stats
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 고급 분석 기능을 위한 패키지가 없습니다: {e}")
    print("기본 분석 기능만 사용됩니다.")
    ADVANCED_FEATURES_AVAILABLE = False
    # 더미 클래스들 생성
    class LinearRegression:
        def fit(self, X, y): pass
        def predict(self, X): return [0] * len(X)
        def score(self, X, y): return 0.0
    
    class PolynomialFeatures:
        def __init__(self, degree=2): pass
        def fit_transform(self, X): return X
        def transform(self, X): return X
    
    class stats:
        @staticmethod
        def norm(): 
            class _norm:
                @staticmethod
                def ppf(x): return 1.96
            return _norm()

from utils.supabase_client import get_supabase_client
from utils.performance_optimizer import cached


class TrendAnalyzer:
    """트렌드 분석 클래스"""
    
    def __init__(self):
        self.supabase = None
        try:
            self.supabase = get_supabase_client()
        except Exception:
            pass
    
    @cached(ttl=1800, key_prefix="trend_")  # 30분 캐시
    def get_trend_data(self, start_date: date, end_date: date) -> pd.DataFrame:
        """트렌드 분석용 데이터 조회"""
        if not self.supabase:
            return self._generate_sample_trend_data(start_date, end_date)
        
        try:
            result = self.supabase.table('inspection_data') \
                .select('inspection_date, result, total_inspected, defect_quantity, pass_quantity, inspectors(name), production_models(model_name)') \
                .gte('inspection_date', start_date.strftime('%Y-%m-%d')) \
                .lte('inspection_date', end_date.strftime('%Y-%m-%d')) \
                .order('inspection_date') \
                .execute()
            
            data = result.data if result.data else []
            
            if not data:
                return self._generate_sample_trend_data(start_date, end_date)
            
            # DataFrame으로 변환 (베트남 시간대 적용)
            df_data = []
            for item in data:
                inspector_name = item.get('inspectors', {}).get('name', 'Unknown') if item.get('inspectors') else 'Unknown'
                model_name = item.get('production_models', {}).get('model_name', 'Unknown') if item.get('production_models') else 'Unknown'
                
                # 베트남 시간대로 변환
                inspection_datetime = convert_utc_to_vietnam(item['inspection_date'])
                
                df_data.append({
                    'date': inspection_datetime,
                    'result': item.get('result', ''),
                    'total_inspected': item.get('total_inspected', 0),
                    'defect_quantity': item.get('defect_quantity', 0),
                    'pass_quantity': item.get('pass_quantity', 0),
                    'inspector': inspector_name,
                    'model': model_name
                })
            
            df = pd.DataFrame(df_data)
            return df
            
        except Exception as e:
            st.warning(f"트렌드 데이터 조회 실패: {str(e)}")
            return self._generate_sample_trend_data(start_date, end_date)
    
    def _generate_sample_trend_data(self, start_date: date, end_date: date) -> pd.DataFrame:
        """샘플 트렌드 데이터 생성"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        np.random.seed(42)  # 일관된 샘플 데이터
        
        data = []
        for single_date in date_range:
            # 요일별 패턴 (주말 낮음)
            weekday_factor = 0.7 if single_date.weekday() >= 5 else 1.0
            
            # 시간적 트렌드 (점진적 개선)
            days_from_start = (single_date.date() - start_date).days
            trend_factor = 1.0 - (days_from_start * 0.001)  # 약간의 개선 트렌드
            
            # 랜덤 변동
            random_factor = np.random.normal(1.0, 0.1)
            
            base_inspected = int(100 * weekday_factor * trend_factor * random_factor)
            base_defect_rate = max(0.01, 0.05 * trend_factor * random_factor)  # 1~5% 불량률
            defect_qty = int(base_inspected * base_defect_rate)
            pass_qty = base_inspected - defect_qty
            
            data.append({
                'date': single_date,
                'result': '합격' if defect_qty <= base_inspected * 0.02 else '불합격',
                'total_inspected': base_inspected,
                'defect_quantity': defect_qty,
                'pass_quantity': pass_qty,
                'inspector': np.random.choice(['김검사', '이품질', '박정밀']),
                'model': np.random.choice(['PA1', 'PA2', 'PA3', 'B6'])
            })
        
        return pd.DataFrame(data)
    
    def calculate_daily_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """일별 트렌드 계산"""
        daily_stats = df.groupby(df['date'].dt.date).agg({
            'total_inspected': 'sum',
            'defect_quantity': 'sum',
            'pass_quantity': 'sum'
        }).reset_index()
        
        daily_stats['defect_rate'] = (daily_stats['defect_quantity'] / daily_stats['total_inspected'] * 100).round(3)
        daily_stats['pass_rate'] = (daily_stats['pass_quantity'] / daily_stats['total_inspected'] * 100).round(1)
        daily_stats['inspection_count'] = df.groupby(df['date'].dt.date).size().values
        
        return daily_stats
    
    def calculate_moving_averages(self, df: pd.DataFrame, windows: List[int] = [3, 7, 14]) -> pd.DataFrame:
        """이동 평균 계산"""
        result_df = df.copy()
        
        for window in windows:
            result_df[f'defect_rate_ma{window}'] = result_df['defect_rate'].rolling(window=window, min_periods=1).mean().round(3)
            result_df[f'inspection_count_ma{window}'] = result_df['inspection_count'].rolling(window=window, min_periods=1).mean().round(1)
        
        return result_df
    
    def detect_trend_changes(self, df: pd.DataFrame, column: str = 'defect_rate', sensitivity: float = 1.5) -> List[Dict]:
        """트렌드 변화점 감지"""
        values = df[column].values
        changes = []
        
        if len(values) < 5:
            return changes
        
        # 이동 평균과 표준편차 계산
        window = min(7, len(values) // 3)
        rolling_mean = pd.Series(values).rolling(window=window, min_periods=1).mean()
        rolling_std = pd.Series(values).rolling(window=window, min_periods=1).std()
        
        for i in range(window, len(values)):
            current_value = values[i]
            expected_value = rolling_mean.iloc[i-1]
            threshold = rolling_std.iloc[i-1] * sensitivity
            
            if abs(current_value - expected_value) > threshold:
                change_type = "증가" if current_value > expected_value else "감소"
                changes.append({
                    'date': df.iloc[i]['date'],
                    'value': current_value,
                    'expected': expected_value,
                    'change_type': change_type,
                    'magnitude': abs(current_value - expected_value)
                })
        
        return changes
    
    def create_trend_chart(self, df: pd.DataFrame, metric: str = 'defect_rate') -> go.Figure:
        """트렌드 차트 생성"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f'{metric.replace("_", " ").title()} 추이', '검사 건수'),
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # 메인 트렌드 라인
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df[metric],
                mode='lines+markers',
                name=f'{metric.replace("_", " ").title()}',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ),
            row=1, col=1
        )
        
        # 이동 평균 (7일)
        if f'{metric}_ma7' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df[f'{metric}_ma7'],
                    mode='lines',
                    name='7일 이동평균',
                    line=dict(color='red', width=2, dash='dash')
                ),
                row=1, col=1
            )
        
        # 검사 건수
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['inspection_count'],
                name='검사 건수',
                marker_color='lightblue',
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # 레이아웃 설정
        fig.update_layout(
            title=f"품질 트렌드 분석 - {metric.replace('_', ' ').title()}",
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="날짜", row=2, col=1)
        fig.update_yaxes(title_text=f"{metric.replace('_', ' ').title()} (%)", row=1, col=1)
        fig.update_yaxes(title_text="검사 건수", row=2, col=1)
        
        return fig


class PredictiveAnalyzer:
    """예측 분석 클래스"""
    
    def __init__(self):
        pass
    
    def predict_defect_rate(self, df: pd.DataFrame, days_ahead: int = 7) -> Dict:
        """불량률 예측"""
        if not ADVANCED_FEATURES_AVAILABLE:
            return {'error': 'scipy와 scikit-learn 패키지가 필요합니다. pip install scipy scikit-learn을 실행하세요.'}
        
        if len(df) < 7:
            return {'error': '예측을 위해서는 최소 7일 이상의 데이터가 필요합니다.'}
        
        # 데이터 준비
        df_clean = df.dropna(subset=['defect_rate'])
        if len(df_clean) < 7:
            return {'error': '유효한 데이터가 부족합니다.'}
        
        # 시계열 데이터를 숫자형으로 변환
        df_clean = df_clean.copy()
        df_clean['days'] = range(len(df_clean))
        
        X = df_clean[['days']].values
        y = df_clean['defect_rate'].values
        
        try:
            # 선형 회귀 예측
            linear_model = LinearRegression()
            linear_model.fit(X, y)
            
            # 다항식 회귀 예측 (2차)
            poly_features = PolynomialFeatures(degree=2)
            X_poly = poly_features.fit_transform(X)
            poly_model = LinearRegression()
            poly_model.fit(X_poly, y)
            
            # 미래 날짜 예측
            future_days = np.arange(len(df_clean), len(df_clean) + days_ahead).reshape(-1, 1)
            future_X_poly = poly_features.transform(future_days)
            
            linear_pred = linear_model.predict(future_days)
            poly_pred = poly_model.predict(future_X_poly)
            
            # 예측 결과 생성
            future_dates = pd.date_range(
                start=df_clean['date'].iloc[-1] + timedelta(days=1),
                periods=days_ahead,
                freq='D'
            )
            
            predictions = []
            for i, date in enumerate(future_dates):
                predictions.append({
                    'date': date,
                    'linear_prediction': max(0, linear_pred[i]),
                    'polynomial_prediction': max(0, poly_pred[i]),
                    'confidence_interval': self._calculate_confidence_interval(y, poly_pred[i])
                })
            
            # 모델 성능 평가
            y_pred_linear = linear_model.predict(X)
            y_pred_poly = poly_model.predict(X_poly)
            
            linear_r2 = linear_model.score(X, y)
            poly_r2 = poly_model.score(X_poly, y)
            
            return {
                'predictions': predictions,
                'model_performance': {
                    'linear_r2': linear_r2,
                    'polynomial_r2': poly_r2,
                    'recommended_model': 'polynomial' if poly_r2 > linear_r2 else 'linear'
                },
                'trend_analysis': self._analyze_trend_direction(df_clean['defect_rate'].values)
            }
            
        except Exception as e:
            return {'error': f'예측 모델 생성 실패: {str(e)}'}
    
    def _calculate_confidence_interval(self, historical_data: np.ndarray, prediction: float, confidence: float = 0.95) -> Tuple[float, float]:
        """신뢰구간 계산"""
        std_dev = np.std(historical_data)
        z_score = stats.norm.ppf((1 + confidence) / 2)
        margin = z_score * std_dev
        
        return (max(0, prediction - margin), prediction + margin)
    
    def _analyze_trend_direction(self, values: np.ndarray) -> str:
        """트렌드 방향 분석"""
        if len(values) < 3:
            return "불충분한 데이터"
        
        # 선형 회귀의 기울기로 트렌드 판단
        X = np.arange(len(values)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, values)
        slope = model.coef_[0]
        
        if slope > 0.1:
            return "증가 추세"
        elif slope < -0.1:
            return "감소 추세"
        else:
            return "안정적"
    
    def create_prediction_chart(self, df: pd.DataFrame, predictions: Dict) -> go.Figure:
        """예측 차트 생성"""
        fig = go.Figure()
        
        # 실제 데이터
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['defect_rate'],
                mode='lines+markers',
                name='실제 불량률',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            )
        )
        
        if 'predictions' in predictions:
            pred_data = predictions['predictions']
            dates = [p['date'] for p in pred_data]
            
            # 다항식 예측
            poly_values = [p['polynomial_prediction'] for p in pred_data]
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=poly_values,
                    mode='lines+markers',
                    name='예측 불량률',
                    line=dict(color='red', width=2, dash='dash'),
                    marker=dict(size=6, symbol='diamond')
                )
            )
            
            # 신뢰구간
            confidence_upper = [p['confidence_interval'][1] for p in pred_data]
            confidence_lower = [p['confidence_interval'][0] for p in pred_data]
            
            fig.add_trace(
                go.Scatter(
                    x=dates + dates[::-1],
                    y=confidence_upper + confidence_lower[::-1],
                    fill='toself',
                    fillcolor='rgba(255, 0, 0, 0.1)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='95% 신뢰구간',
                    showlegend=True
                )
            )
        
        fig.update_layout(
            title="불량률 예측 분석",
            xaxis_title="날짜",
            yaxis_title="불량률 (%)",
            height=500,
            hovermode='x unified'
        )
        
        return fig


class SPCAnalyzer:
    """통계적 공정 관리(SPC) 클래스"""
    
    def __init__(self):
        pass
    
    def calculate_control_limits(self, data: pd.Series, chart_type: str = 'x_chart') -> Dict:
        """관리한계 계산"""
        if len(data) < 5:
            return {'error': '관리한계 계산을 위해서는 최소 5개 이상의 데이터가 필요합니다.'}
        
        mean = data.mean()
        std_dev = data.std()
        
        if chart_type == 'x_chart':
            # X-차트 (개별값 차트)
            ucl = mean + 3 * std_dev  # 상한관리한계
            lcl = max(0, mean - 3 * std_dev)  # 하한관리한계 (음수 방지)
            
            return {
                'center_line': mean,
                'ucl': ucl,
                'lcl': lcl,
                'std_dev': std_dev,
                'chart_type': 'X-Chart (개별값 차트)'
            }
        
        elif chart_type == 'r_chart':
            # R-차트 (범위 차트)
            ranges = data.rolling(window=2).apply(lambda x: x.max() - x.min(), raw=False).dropna()
            r_bar = ranges.mean()
            
            # R-차트 상수 (샘플 크기 2)
            D3, D4 = 0, 3.267
            
            ucl_r = D4 * r_bar
            lcl_r = D3 * r_bar
            
            return {
                'center_line': r_bar,
                'ucl': ucl_r,
                'lcl': lcl_r,
                'chart_type': 'R-Chart (범위 차트)'
            }
    
    def detect_out_of_control_points(self, data: pd.Series, control_limits: Dict) -> List[Dict]:
        """관리 이탈점 감지"""
        out_of_control = []
        
        ucl = control_limits['ucl']
        lcl = control_limits['lcl']
        center_line = control_limits['center_line']
        
        for i, value in enumerate(data):
            if value > ucl:
                out_of_control.append({
                    'index': i,
                    'value': value,
                    'type': '상한관리한계 초과',
                    'severity': 'high'
                })
            elif value < lcl:
                out_of_control.append({
                    'index': i,
                    'value': value,
                    'type': '하한관리한계 미달',
                    'severity': 'high'
                })
        
        return out_of_control
    
    def apply_nelson_rules(self, data: pd.Series, control_limits: Dict) -> List[Dict]:
        """넬슨 규칙 적용"""
        violations = []
        
        ucl = control_limits['ucl']
        lcl = control_limits['lcl']
        center_line = control_limits['center_line']
        std_dev = control_limits.get('std_dev', data.std())
        
        # 1/3, 2/3 구간 계산
        upper_third = center_line + std_dev
        lower_third = center_line - std_dev
        upper_two_thirds = center_line + 2 * std_dev
        lower_two_thirds = center_line - 2 * std_dev
        
        values = data.values
        
        # 규칙 1: 관리한계 벗어남 (이미 위에서 체크됨)
        
        # 규칙 2: 연속 9점이 중심선 한쪽에 위치
        for i in range(len(values) - 8):
            subset = values[i:i+9]
            if all(v > center_line for v in subset) or all(v < center_line for v in subset):
                violations.append({
                    'start_index': i,
                    'end_index': i + 8,
                    'rule': '넬슨 규칙 2: 연속 9점이 중심선 한쪽에 위치',
                    'severity': 'medium'
                })
        
        # 규칙 3: 연속 6점이 계속 증가하거나 감소
        for i in range(len(values) - 5):
            subset = values[i:i+6]
            if all(subset[j] < subset[j+1] for j in range(5)) or \
               all(subset[j] > subset[j+1] for j in range(5)):
                violations.append({
                    'start_index': i,
                    'end_index': i + 5,
                    'rule': '넬슨 규칙 3: 연속 6점이 계속 증가/감소',
                    'severity': 'medium'
                })
        
        # 규칙 4: 연속 14점이 번갈아 상승/하강
        for i in range(len(values) - 13):
            subset = values[i:i+14]
            alternating = True
            for j in range(12):
                if (subset[j] < subset[j+1]) == (subset[j+1] < subset[j+2]):
                    alternating = False
                    break
            
            if alternating:
                violations.append({
                    'start_index': i,
                    'end_index': i + 13,
                    'rule': '넬슨 규칙 4: 연속 14점이 번갈아 상승/하강',
                    'severity': 'low'
                })
        
        return violations
    
    def create_control_chart(self, data: pd.Series, control_limits: Dict, 
                           dates: pd.Series = None, violations: List[Dict] = None) -> go.Figure:
        """관리도 생성"""
        fig = go.Figure()
        
        x_axis = dates if dates is not None else list(range(len(data)))
        
        # 데이터 포인트
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=data,
                mode='lines+markers',
                name='측정값',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            )
        )
        
        # 중심선
        fig.add_hline(
            y=control_limits['center_line'],
            line_dash="solid",
            line_color="green",
            annotation_text="중심선 (CL)"
        )
        
        # 상한관리한계
        fig.add_hline(
            y=control_limits['ucl'],
            line_dash="dash",
            line_color="red",
            annotation_text="상한관리한계 (UCL)"
        )
        
        # 하한관리한계
        fig.add_hline(
            y=control_limits['lcl'],
            line_dash="dash",
            line_color="red",
            annotation_text="하한관리한계 (LCL)"
        )
        
        # 위반점 표시
        if violations:
            violation_indices = []
            violation_values = []
            
            for violation in violations:
                if 'index' in violation:  # 단일점 위반
                    violation_indices.append(x_axis[violation['index']])
                    violation_values.append(data.iloc[violation['index']])
            
            if violation_indices:
                fig.add_trace(
                    go.Scatter(
                        x=violation_indices,
                        y=violation_values,
                        mode='markers',
                        name='관리 이탈점',
                        marker=dict(color='red', size=10, symbol='x')
                    )
                )
        
        fig.update_layout(
            title=f"SPC 관리도 - {control_limits['chart_type']}",
            xaxis_title="날짜" if dates is not None else "측정 순서",
            yaxis_title="측정값",
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def generate_spc_report(self, data: pd.Series, control_limits: Dict, 
                          violations: List[Dict]) -> str:
        """SPC 분석 보고서 생성"""
        total_points = len(data)
        out_of_control_count = len([v for v in violations if v.get('severity') == 'high'])
        
        capability_ratio = 3 * control_limits.get('std_dev', data.std()) / (control_limits['ucl'] - control_limits['lcl']) if control_limits['ucl'] != control_limits['lcl'] else 0
        
        report = f"""
        📊 **SPC 분석 보고서**
        
        **기본 통계:**
        - 총 측정점: {total_points}개
        - 중심선: {control_limits['center_line']:.3f}
        - 상한관리한계: {control_limits['ucl']:.3f}
        - 하한관리한계: {control_limits['lcl']:.3f}
        
        **공정 상태:**
        - 관리 이탈점: {out_of_control_count}개
        - 관리 상태: {'관리 상태' if out_of_control_count == 0 else '관리 이탈'}
        
        **넬슨 규칙 위반:**
        """
        
        for violation in violations:
            if 'rule' in violation:
                report += f"- {violation['rule']}\n"
        
        if capability_ratio > 0:
            report += f"\n**공정 능력:**\n- 공정 능력 지수 (추정): {capability_ratio:.3f}"
        
        return report


# 전역 인스턴스
trend_analyzer = TrendAnalyzer()
predictive_analyzer = PredictiveAnalyzer()
spc_analyzer = SPCAnalyzer()


if __name__ == "__main__":
    # 테스트 실행
    print("Advanced Analytics Module Loaded Successfully!") 