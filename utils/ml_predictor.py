"""
🤖 ML 예측 시스템
2025-07-30 추가

머신러닝 기반 품질 예측 시스템
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class MLPredictor:
    """머신러닝 예측 클래스"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = [
            'days_since_start', 'weekday', 'hour', 'month',
            'total_inspected', 'avg_defect_rate_7d', 'avg_defect_rate_30d'
        ]
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """특성 준비"""
        try:
            df = df.copy()
            df['inspection_date'] = pd.to_datetime(df['inspection_date'])
            
            # 기본 특성
            df['days_since_start'] = (df['inspection_date'] - df['inspection_date'].min()).dt.days
            df['weekday'] = df['inspection_date'].dt.weekday
            df['hour'] = df['inspection_date'].dt.hour
            df['month'] = df['inspection_date'].dt.month
            
            # 불량률 계산
            df['defect_rate'] = df['defect_quantity'] / df['total_inspected'].replace(0, 1)
            
            # 이동 평균
            df = df.sort_values('inspection_date')
            df['avg_defect_rate_7d'] = df['defect_rate'].rolling(window=7, min_periods=1).mean()
            df['avg_defect_rate_30d'] = df['defect_rate'].rolling(window=30, min_periods=1).mean()
            
            return df
            
        except Exception as e:
            st.error(f"특성 준비 오류: {str(e)}")
            return df
    
    def train_model(self, df: pd.DataFrame) -> dict:
        """모델 학습"""
        try:
            if len(df) < 10:
                return {"status": "error", "message": "학습을 위해 최소 10개 이상의 데이터가 필요합니다."}
            
            # 특성 준비
            df_prepared = self.prepare_features(df)
            
            # 특성과 타겟 분리
            X = df_prepared[self.feature_names].fillna(0)
            y = df_prepared['defect_rate'].fillna(0)
            
            # 학습/테스트 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 스케일링
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 모델 학습
            self.model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=8)
            self.model.fit(X_train_scaled, y_train)
            
            # 성능 평가
            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            return {
                "status": "success",
                "performance": {
                    "mae": round(mae, 4),
                    "r2_score": round(r2, 4),
                    "accuracy": round(max(0, r2) * 100, 2)
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"모델 학습 오류: {str(e)}"}
    
    def predict(self, target_days: int = 7) -> dict:
        """미래 불량률 예측"""
        try:
            if self.model is None or self.scaler is None:
                return {"status": "error", "message": "모델이 학습되지 않았습니다."}
            
            predictions = []
            base_date = datetime.now()
            
            for i in range(1, target_days + 1):
                future_date = base_date + timedelta(days=i)
                
                # 미래 특성 생성
                features = {
                    'days_since_start': i,
                    'weekday': future_date.weekday(),
                    'hour': 9,
                    'month': future_date.month,
                    'total_inspected': 100,  # 기본값
                    'avg_defect_rate_7d': 0.02,  # 기본값
                    'avg_defect_rate_30d': 0.02  # 기본값
                }
                
                X_future = np.array([[features[name] for name in self.feature_names]])
                X_future_scaled = self.scaler.transform(X_future)
                
                pred = self.model.predict(X_future_scaled)[0]
                pred = max(0, min(1, pred))  # 0-1 범위 제한
                
                predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_defect_rate': round(pred, 4)
                })
            
            return {"status": "success", "predictions": predictions}
            
        except Exception as e:
            return {"status": "error", "message": f"예측 오류: {str(e)}"}

# 전역 인스턴스
_predictor = None

def get_predictor() -> MLPredictor:
    """MLPredictor 싱글톤 인스턴스 반환"""
    global _predictor
    if _predictor is None:
        _predictor = MLPredictor()
    return _predictor