"""
🔍 이상치 탐지 시스템
2025-07-30 추가

통계적 방법과 머신러닝을 활용한 이상치 탐지
"""

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.ensemble import IsolationForest
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    """이상치 탐지 클래스"""
    
    def __init__(self):
        self.isolation_forest = None
        self.threshold_z_score = 2.5
        self.contamination_rate = 0.1
    
    def detect_anomalies(self, df: pd.DataFrame) -> dict:
        """이상치 탐지 실행"""
        try:
            if len(df) < 5:
                return {
                    "status": "insufficient_data", 
                    "message": "이상치 탐지를 위해 최소 5개 이상의 데이터가 필요합니다."
                }
            
            # 불량률 계산
            df = df.copy()
            df['defect_rate'] = df['defect_quantity'] / df['total_inspected'].replace(0, 1)
            
            # 특성 준비
            features = ['defect_rate', 'total_inspected', 'defect_quantity']
            X = df[features].fillna(0)
            
            # Isolation Forest 이상치 탐지
            self.isolation_forest = IsolationForest(
                contamination=self.contamination_rate, 
                random_state=42
            )
            ml_anomalies = self.isolation_forest.fit_predict(X) == -1
            anomaly_scores = self.isolation_forest.score_samples(X)
            
            # Z-score 기반 통계적 이상치 탐지
            z_scores = np.abs(stats.zscore(df['defect_rate'].fillna(0)))
            statistical_anomalies = z_scores > self.threshold_z_score
            
            # 결과 정리
            anomalies = []
            for i, (ml_anom, stat_anom) in enumerate(zip(ml_anomalies, statistical_anomalies)):
                if ml_anom or stat_anom:
                    anomaly_data = {
                        'index': i,
                        'date': df.iloc[i]['inspection_date'],
                        'defect_rate': round(df.iloc[i]['defect_rate'], 4),
                        'total_inspected': int(df.iloc[i]['total_inspected']),
                        'defect_quantity': int(df.iloc[i]['defect_quantity']),
                        'anomaly_score': round(anomaly_scores[i], 4),
                        'z_score': round(z_scores[i], 4),
                        'detection_method': []
                    }
                    
                    if ml_anom:
                        anomaly_data['detection_method'].append('ML')
                    if stat_anom:
                        anomaly_data['detection_method'].append('Statistical')
                    
                    anomaly_data['detection_method'] = ', '.join(anomaly_data['detection_method'])
                    anomalies.append(anomaly_data)
            
            # 통계 계산
            total_data = len(df)
            total_anomalies = len(anomalies)
            anomaly_percentage = round(total_anomalies / total_data * 100, 2)
            
            # 심각도 분류
            severity = self._classify_severity(anomaly_percentage, anomalies)
            
            # 인사이트 생성
            insights = self._generate_insights(anomalies, anomaly_percentage, severity)
            
            return {
                "status": "success",
                "anomalies": anomalies,
                "statistics": {
                    "total_anomalies": total_anomalies,
                    "total_data": total_data,
                    "anomaly_percentage": anomaly_percentage,
                    "severity": severity
                },
                "insights": insights
            }
            
        except Exception as e:
            return {"status": "error", "message": f"이상치 탐지 오류: {str(e)}"}
    
    def _classify_severity(self, percentage: float, anomalies: list) -> str:
        """이상치 심각도 분류"""
        if percentage == 0:
            return "없음"
        elif percentage <= 3:
            return "낮음"
        elif percentage <= 8:
            return "보통"
        elif percentage <= 15:
            return "높음"
        else:
            return "심각"
    
    def _generate_insights(self, anomalies: list, percentage: float, severity: str) -> list:
        """인사이트 생성"""
        insights = []
        
        if not anomalies:
            insights.append("✅ 이상치가 발견되지 않았습니다. 품질이 안정적입니다.")
            return insights
        
        # 전체 평가
        if severity == "심각":
            insights.append(f"🚨 {len(anomalies)}개의 이상치 발견! 전체 데이터의 {percentage}%입니다. 즉시 조치가 필요합니다.")
        elif severity == "높음":
            insights.append(f"⚠️ {len(anomalies)}개의 이상치가 발견되었습니다. ({percentage}%) 품질 관리 강화가 필요합니다.")
        elif severity == "보통":
            insights.append(f"📊 {len(anomalies)}개의 이상치가 발견되었습니다. ({percentage}%) 정기적인 모니터링을 권장합니다.")
        else:
            insights.append(f"✅ 소수의 이상치({len(anomalies)}개)가 발견되었습니다. 정상 범위입니다.")
        
        # 가장 심각한 이상치 분석
        if anomalies:
            most_severe = max(anomalies, key=lambda x: abs(x['anomaly_score']))
            insights.append(f"🔍 가장 심각한 이상치: {most_severe['date']} (불량률: {most_severe['defect_rate']:.2%})")
        
        # 최근 이상치 분석
        recent_anomalies = [a for a in anomalies if isinstance(a['date'], str) and a['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')]
        if recent_anomalies:
            insights.append(f"📅 최근 7일간 {len(recent_anomalies)}개의 이상치가 발생했습니다.")
        
        return insights

# 전역 인스턴스
_detector = None

def get_detector() -> AnomalyDetector:
    """AnomalyDetector 싱글톤 인스턴스 반환"""
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
    return _detector