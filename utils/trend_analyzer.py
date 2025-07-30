"""
📈 트렌드 분석 시스템
2025-07-30 추가

품질 데이터의 트렌드 패턴 분석
"""

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.linear_model import LinearRegression
from scipy.signal import savgol_filter
import warnings
warnings.filterwarnings('ignore')

class TrendAnalyzer:
    """트렌드 분석 클래스"""
    
    def __init__(self):
        self.trend_models = {}
    
    def analyze_trends(self, df: pd.DataFrame) -> dict:
        """전체 트렌드 분석"""
        try:
            if len(df) < 7:
                return {
                    "status": "insufficient_data", 
                    "message": "트렌드 분석을 위해 최소 7일 이상의 데이터가 필요합니다."
                }
            
            # 데이터 준비
            df = df.copy()
            df['inspection_date'] = pd.to_datetime(df['inspection_date'])
            df['defect_rate'] = df['defect_quantity'] / df['total_inspected'].replace(0, 1)
            
            # 일별 집계
            daily_stats = df.groupby('inspection_date').agg({
                'defect_rate': 'mean',
                'total_inspected': 'sum',
                'defect_quantity': 'sum'
            }).reset_index()
            
            daily_stats = daily_stats.sort_values('inspection_date')
            
            # 트렌드 분석
            trend_analysis = self._calculate_trends(daily_stats)
            
            # 주기적 패턴 분석
            periodic_analysis = self._analyze_periodic_patterns(df)
            
            # 스무딩된 트렌드
            smoothed_trend = self._smooth_trend(daily_stats['defect_rate'])
            
            # 트렌드 분류 및 인사이트
            classification = self._classify_trends(trend_analysis)
            insights = self._generate_trend_insights(classification, trend_analysis)
            
            return {
                "status": "success",
                "trend_analysis": {
                    **trend_analysis,
                    "classification": classification,
                    "smoothed_trend": smoothed_trend.tolist(),
                    "dates": daily_stats['inspection_date'].dt.strftime('%Y-%m-%d').tolist()
                },
                "periodic_patterns": periodic_analysis,
                "insights": insights
            }
            
        except Exception as e:
            return {"status": "error", "message": f"트렌드 분석 오류: {str(e)}"}
    
    def _calculate_trends(self, daily_stats: pd.DataFrame) -> dict:
        """트렌드 계산"""
        try:
            X = np.arange(len(daily_stats)).reshape(-1, 1)
            
            # 불량률 트렌드
            defect_model = LinearRegression()
            defect_model.fit(X, daily_stats['defect_rate'])
            defect_slope = defect_model.coef_[0]
            defect_r2 = defect_model.score(X, daily_stats['defect_rate'])
            
            # 검사량 트렌드
            volume_model = LinearRegression()
            volume_model.fit(X, daily_stats['total_inspected'])
            volume_slope = volume_model.coef_[0]
            volume_r2 = volume_model.score(X, daily_stats['total_inspected'])
            
            return {
                "defect_rate_slope": round(defect_slope, 6),
                "defect_rate_r2": round(defect_r2, 4),
                "volume_slope": round(volume_slope, 2),
                "volume_r2": round(volume_r2, 4)
            }
            
        except Exception:
            return {
                "defect_rate_slope": 0,
                "defect_rate_r2": 0,
                "volume_slope": 0,
                "volume_r2": 0
            }
    
    def _analyze_periodic_patterns(self, df: pd.DataFrame) -> dict:
        """주기적 패턴 분석"""
        try:
            # 요일별 패턴
            df['weekday'] = df['inspection_date'].dt.weekday
            weekday_pattern = df.groupby('weekday')['defect_rate'].agg(['mean', 'std', 'count']).round(4)
            
            weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
            weekly_patterns = {}
            
            for i in range(7):
                if i in weekday_pattern.index:
                    weekly_patterns[weekday_names[i]] = {
                        'avg_defect_rate': weekday_pattern.loc[i, 'mean'],
                        'std_defect_rate': weekday_pattern.loc[i, 'std'],
                        'data_points': int(weekday_pattern.loc[i, 'count'])
                    }
            
            # 시간대별 패턴
            df['hour'] = df['inspection_date'].dt.hour
            hourly_pattern = df.groupby('hour')['defect_rate'].agg(['mean', 'std', 'count']).round(4)
            
            hourly_patterns = {}
            for hour in hourly_pattern.index:
                hourly_patterns[f"{hour}시"] = {
                    'avg_defect_rate': hourly_pattern.loc[hour, 'mean'],
                    'std_defect_rate': hourly_pattern.loc[hour, 'std'],
                    'data_points': int(hourly_pattern.loc[hour, 'count'])
                }
            
            return {
                "weekly": weekly_patterns,
                "hourly": hourly_patterns
            }
            
        except Exception:
            return {"weekly": {}, "hourly": {}}
    
    def _smooth_trend(self, data: pd.Series) -> np.ndarray:
        """트렌드 스무딩"""
        try:
            if len(data) >= 5:
                window_length = min(5, len(data))
                if window_length % 2 == 0:
                    window_length -= 1
                return savgol_filter(data, window_length, polyorder=2)
            else:
                return data.values
        except Exception:
            return data.values
    
    def _classify_trends(self, trend_analysis: dict) -> dict:
        """트렌드 분류"""
        defect_slope = trend_analysis.get('defect_rate_slope', 0)
        volume_slope = trend_analysis.get('volume_slope', 0)
        defect_r2 = trend_analysis.get('defect_rate_r2', 0)
        
        # 불량률 트렌드 분류
        if defect_slope < -0.001:
            defect_trend = "개선"
        elif defect_slope > 0.001:
            defect_trend = "악화"
        else:
            defect_trend = "안정"
        
        # 검사량 트렌드 분류
        if volume_slope > 1:
            volume_trend = "증가"
        elif volume_slope < -1:
            volume_trend = "감소"
        else:
            volume_trend = "안정"
        
        # 트렌드 강도 분류
        if abs(defect_slope) > 0.01:
            trend_strength = "강함"
        elif abs(defect_slope) > 0.005:
            trend_strength = "보통"
        else:
            trend_strength = "약함"
        
        # 신뢰도 분류
        if defect_r2 > 0.7:
            confidence = "높음"
        elif defect_r2 > 0.4:
            confidence = "보통"
        else:
            confidence = "낮음"
        
        return {
            "defect_rate_trend": defect_trend,
            "volume_trend": volume_trend,
            "trend_strength": trend_strength,
            "confidence": confidence
        }
    
    def _generate_trend_insights(self, classification: dict, trend_analysis: dict) -> list:
        """트렌드 인사이트 생성"""
        insights = []
        
        defect_slope = trend_analysis.get('defect_rate_slope', 0)
        volume_slope = trend_analysis.get('volume_slope', 0)
        confidence = classification.get('confidence', '낮음')
        
        # 불량률 트렌드 인사이트
        if classification['defect_rate_trend'] == "개선":
            insights.append(f"✅ 불량률이 개선되고 있습니다. (일일 {abs(defect_slope):.4f} 감소)")
        elif classification['defect_rate_trend'] == "악화":
            insights.append(f"⚠️ 불량률이 악화되고 있습니다. (일일 {defect_slope:.4f} 증가)")
        else:
            insights.append("📊 불량률이 안정적입니다.")
        
        # 검사량 트렌드 인사이트
        if classification['volume_trend'] == "증가":
            insights.append(f"📈 검사량이 증가하고 있습니다. (일일 {volume_slope:.1f}개 증가)")
        elif classification['volume_trend'] == "감소":
            insights.append(f"📉 검사량이 감소하고 있습니다. (일일 {abs(volume_slope):.1f}개 감소)")
        
        # 트렌드 강도 및 신뢰도 인사이트
        if classification['trend_strength'] == "강함" and confidence == "높음":
            insights.append("🎯 명확하고 신뢰할 수 있는 트렌드가 감지되었습니다.")
        elif classification['trend_strength'] == "약함":
            insights.append("📊 트렌드가 약해 지속적인 모니터링이 필요합니다.")
        elif confidence == "낮음":
            insights.append("⚠️ 트렌드 신뢰도가 낮습니다. 더 많은 데이터가 필요할 수 있습니다.")
        
        return insights

# 전역 인스턴스
_analyzer = None

def get_analyzer() -> TrendAnalyzer:
    """TrendAnalyzer 싱글톤 인스턴스 반환"""
    global _analyzer
    if _analyzer is None:
        _analyzer = TrendAnalyzer()
    return _analyzer