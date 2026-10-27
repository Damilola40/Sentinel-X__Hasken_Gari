"""
Sentinel-X Unified AI Pipeline Integration Wrapper
Orchestrates Ingestion, NLP Classification, Correlation Clustering, Risk Engine, and XAI.
"""

import pandas as pd
from typing import Dict, Any, Tuple

from .ai_config import AIConfig
from preprocessing import TextPreprocessor
from classification import IncidentClassifier
from similarity import SimilarityEngine
from clustering import ReportCorrelator
from risk_engine import RiskEngine
from explainability import XAIExplainer

class SentinelXPipeline:
    def __init__(self, model_dir: str = "models"):
        self.preprocessor = TextPreprocessor()
        self.classifier = IncidentClassifier(model_dir=model_dir)
        self.similarity_engine = SimilarityEngine()
        self.correlator = ReportCorrelator()
        self.risk_engine = RiskEngine(model_dir=model_dir)
        self.explainer = XAIExplainer()

    def train_all(self, incident_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Trains both classification and risk models on the dataset.
        """
        print("[Sentinel-X AI] Training NLP Classification Model...")
        clf_metrics = self.classifier.train(incident_df)
        
        print("[Sentinel-X AI] Training Risk Scoring & Anomaly Models...")
        risk_metrics = self.risk_engine.train(incident_df)
        
        return {
            "classification_metrics": clf_metrics,
            "risk_metrics": risk_metrics
        }

    def process_single_report(self, title: str, description: str, lat: float, lon: float) -> Dict[str, Any]:
        """
        Processes a single incoming incident report (text/voice transcript).
        """
        # 1. Clean Text
        cleaned = self.preprocessor.process_report(title, description)
        
        # 2. Predict Category & Severity
        nlp_out = self.classifier.predict(cleaned['combined_text'])
        
        return {
            "title": cleaned['clean_title'],
            "description": cleaned['clean_description'],
            "category": nlp_out['category'],
            "category_confidence": nlp_out['category_confidence'],
            "severity": nlp_out['severity'],
            "severity_confidence": nlp_out['severity_confidence'],
            "flagged_for_review": nlp_out['flagged_for_review']
        }

    def analyze_incident_batch(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Runs correlation and duplicate clustering over a batch of reports.
        """
        return self.correlator.cluster_reports(df)

    def calculate_lga_risk_board(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts LGA features, calculates risk scores, detects anomalies, and attaches XAI explanations.
        """
        lga_df = self.risk_engine.extract_lga_features(df)
        risk_df = self.risk_engine.predict_lga_risk(lga_df)
        
        # Attach XAI explanations
        explanations = []
        for _, row in risk_df.iterrows():
            expl = self.explainer.explain_lga_risk(row.to_dict())
            explanations.append(expl)
            
        risk_df['contributing_factors'] = explanations
        return risk_df
