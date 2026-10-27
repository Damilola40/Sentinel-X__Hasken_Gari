"""
Module 1: Incident Category & Severity Classification Model
Trains TF-IDF + Logistic Regression / XGBoost models on nigeria_incident_dataset.csv.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

from .ai_config import AIConfig

class IncidentClassifier:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.category_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=2000, ngram_range=(1, 2))),
            ('clf', LogisticRegression(max_iter=1000, C=1.0, class_weight='balanced'))
        ])
        
        self.severity_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=2000, ngram_range=(1, 2))),
            ('clf', LogisticRegression(max_iter=1000, C=1.0, class_weight='balanced'))
        ])
        self.is_trained = False

    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Trains category and severity classification pipelines.
        """
        df = df.copy()
        df['combined_text'] = df['title'].fillna('') + '. ' + df['description'].fillna('')
        
        X = df['combined_text']
        y_cat = df['category']
        y_sev = df['severity']
        
        # Train pipelines
        self.category_pipeline.fit(X, y_cat)
        self.severity_pipeline.fit(X, y_sev)
        
        # Evaluate CV F1 scores
        cat_scores = cross_val_score(self.category_pipeline, X, y_cat, cv=5, scoring='f1_macro')
        sev_scores = cross_val_score(self.severity_pipeline, X, y_sev, cv=5, scoring='f1_macro')
        
        self.is_trained = True
        self.save_models()
        
        return {
            "category_cv_f1_macro": float(np.mean(cat_scores)),
            "severity_cv_f1_macro": float(np.mean(sev_scores))
        }

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predicts incident category and severity along with confidence scores.
        """
        if not self.is_trained:
            self.load_models()
            
        cat_probs = self.category_pipeline.predict_proba([text])[0]
        cat_idx = np.argmax(cat_probs)
        category = self.category_pipeline.classes_[cat_idx]
        cat_conf = float(cat_probs[cat_idx])
        
        sev_probs = self.severity_pipeline.predict_proba([text])[0]
        sev_idx = np.argmax(sev_probs)
        severity = self.severity_pipeline.classes_[sev_idx]
        sev_conf = float(sev_probs[sev_idx])
        
        # Flag for human review if low confidence or high severity
        flagged = (sev_conf < AIConfig.HUMAN_REVIEW_CONFIDENCE_MIN) or (severity in AIConfig.HUMAN_REVIEW_SEVERITY_LEVELS)
        
        return {
            "category": category,
            "category_confidence": round(cat_conf, 3),
            "severity": severity,
            "severity_confidence": round(sev_conf, 3),
            "flagged_for_review": flagged
        }

    def save_models(self):
        joblib.dump(self.category_pipeline, os.path.join(self.model_dir, "category_model.joblib"))
        joblib.dump(self.severity_pipeline, os.path.join(self.model_dir, "severity_model.joblib"))

    def load_models(self):
        cat_path = os.path.join(self.model_dir, "category_model.joblib")
        sev_path = os.path.join(self.model_dir, "severity_model.joblib")
        if os.path.exists(cat_path) and os.path.exists(sev_path):
            self.category_pipeline = joblib.load(cat_path)
            self.severity_pipeline = joblib.load(sev_path)
            self.is_trained = True
        else:
            raise FileNotFoundError("Classifier models not found. Please train first.")
