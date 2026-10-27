"""
Module 3: AI Risk Scoring & Anomaly Detection Engine
Computes LGA spatial risk indicators using XGBoost and flags unexpected spikes via Isolation Forest.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from .ai_config import AIConfig

class RiskEngine:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.risk_model = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=AIConfig.ISOLATION_FOREST_CONTAMINATION, random_state=42)
        self.is_trained = False

    def extract_lga_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates raw incident data into LGA-level risk feature vectors.
        """
        lga_features = []
        grouped = df.groupby(['state', 'lga'])
        
        for (state, lga), group in grouped:
            total_incidents = len(group)
            
            # Map severities to weights
            sev_weights = group['severity'].map(AIConfig.SEVERITY_WEIGHTS).fillna(1.0)
            avg_severity = sev_weights.mean()
            max_severity = sev_weights.max()
            
            # High severity ratio
            high_sev_count = (sev_weights >= 3.0).sum()
            high_sev_ratio = high_sev_count / total_incidents
            
            # Categories diversity score
            cat_count = group['category'].nunique()
            
            # Incident count approximations
            count_7d = max(1, int(total_incidents * 0.35))
            count_30d = total_incidents
            change_rate = (count_7d / (count_30d / 4.0 + 1.0))
            
            lga_features.append({
                'state': state,
                'lga': lga,
                'total_incidents': total_incidents,
                'count_7d': count_7d,
                'count_30d': count_30d,
                'change_rate': round(change_rate, 2),
                'avg_severity': round(avg_severity, 2),
                'max_severity': max_severity,
                'high_sev_ratio': round(high_sev_ratio, 2),
                'category_diversity': cat_count
            })
            
        return pd.DataFrame(lga_features)

    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Trains XGBoost Risk Scoring Regressor and Isolation Forest Anomaly Detector.
        """
        lga_df = self.extract_lga_features(df)
        feature_cols = ['count_7d', 'count_30d', 'change_rate', 'avg_severity', 'max_severity', 'high_sev_ratio', 'category_diversity']
        
        X = lga_df[feature_cols]
        X_scaled = self.scaler.fit_transform(X)
        
        # Synthetic risk target generation for training baseline
        y_risk = (
            lga_df['count_7d'] * 3.5 +
            lga_df['avg_severity'] * 15.0 +
            lga_df['high_sev_ratio'] * 25.0 +
            lga_df['change_rate'] * 10.0
        )
        y_risk = np.clip(y_risk, 0.0, 100.0)
        
        self.risk_model.fit(X_scaled, y_risk)
        self.anomaly_detector.fit(X_scaled)
        
        self.is_trained = True
        self.feature_names = feature_cols
        self.save_models()
        
        return {
            "lga_count": len(lga_df),
            "features_trained": feature_cols,
            "risk_score_min": float(y_risk.min()),
            "risk_score_max": float(y_risk.max())
        }

    def predict_lga_risk(self, lga_df: pd.DataFrame) -> pd.DataFrame:
        """
        Predicts LGA Risk Scores (0-100), Risk Levels, and Anomaly Flags.
        """
        if not self.is_trained:
            self.load_models()
            
        feature_cols = ['count_7d', 'count_30d', 'change_rate', 'avg_severity', 'max_severity', 'high_sev_ratio', 'category_diversity']
        X = lga_df[feature_cols]
        X_scaled = self.scaler.transform(X)
        
        risk_scores = self.risk_model.predict(X_scaled)
        risk_scores = np.clip(risk_scores, 0.0, 100.0)
        
        anomalies = self.anomaly_detector.predict(X_scaled)  # -1 = anomaly, 1 = normal
        
        result_df = lga_df.copy()
        result_df['risk_score'] = [round(float(s), 1) for s in risk_scores]
        result_df['is_anomaly'] = [bool(a == -1) for a in anomalies]
        
        def assign_level(score):
            if score < 30: return "LOW"
            elif score < 60: return "MODERATE"
            elif score < 80: return "ELEVATED"
            else: return "HIGH"
            
        result_df['risk_level'] = result_df['risk_score'].apply(assign_level)
        return result_df

    def save_models(self):
        joblib.dump(self.scaler, os.path.join(self.model_dir, "scaler.joblib"))
        joblib.dump(self.risk_model, os.path.join(self.model_dir, "risk_model.joblib"))
        joblib.dump(self.anomaly_detector, os.path.join(self.model_dir, "anomaly_model.joblib"))

    def load_models(self):
        scaler_path = os.path.join(self.model_dir, "scaler.joblib")
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
            self.risk_model = joblib.load(os.path.join(self.model_dir, "risk_model.joblib"))
            self.anomaly_detector = joblib.load(os.path.join(self.model_dir, "anomaly_model.joblib"))
            self.is_trained = True
        else:
            raise FileNotFoundError("Risk models not found. Please train first.")
