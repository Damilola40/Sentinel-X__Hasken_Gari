"""
Module 2: Spatio-Temporal-Semantic Clustering & Duplicate Correlation Engine
Calculates composite distance (Haversine + Temporal + Semantic) and clusters reports.
Dynamically re-normalizes weights when temporal timestamps are not available.
"""

import math
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score

from .ai_config import AIConfig
from .similarity import SimilarityEngine

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the Haversine distance in kilometers between two lat/lon pairs.
    """
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class ReportCorrelator:
    def __init__(self):
        self.similarity_engine = SimilarityEngine()

    def cluster_reports(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Clusters reports in a dataframe and assigns cluster_id / duplicate status.
        Dynamically re-normalizes weights if temporal information is missing.
        """
        n = len(df)
        if n == 0:
            return df, {}
            
        texts = (df['title'].fillna('') + '. ' + df['description'].fillna('')).tolist()
        lats = df['latitude'].values
        lons = df['longitude'].values
        
        has_temporal = 'timestamp' in df.columns and df['timestamp'].notna().any()
        
        # Dynamically normalize weights so they always sum to 1.0
        if has_temporal:
            w_sem = AIConfig.WEIGHT_SEMANTIC
            w_geo = AIConfig.WEIGHT_GEOSPATIAL
            w_temp = AIConfig.WEIGHT_TEMPORAL
        else:
            sum_w = AIConfig.WEIGHT_SEMANTIC + AIConfig.WEIGHT_GEOSPATIAL
            w_sem = AIConfig.WEIGHT_SEMANTIC / sum_w
            w_geo = AIConfig.WEIGHT_GEOSPATIAL / sum_w
            w_temp = 0.0

        # Build composite similarity matrix
        embeddings = self.similarity_engine.encode(texts)
        sem_mat = np.dot(embeddings, embeddings.T)
        norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norm[norm == 0] = 1.0
        sem_mat = sem_mat / np.dot(norm, norm.T)
        
        dist_mat = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                d_geo = haversine_distance(lats[i], lons[i], lats[j], lons[j])
                if d_geo > AIConfig.CORRELATION_SPATIAL_RADIUS_KM:
                    geo_sim = 0.0
                else:
                    geo_sim = math.exp(-d_geo / AIConfig.CORRELATION_SPATIAL_RADIUS_KM)
                    
                comp_sim = w_sem * sem_mat[i, j] + w_geo * geo_sim
                comp_dist = max(0.0, 1.0 - comp_sim)
                dist_mat[i, j] = comp_dist
                dist_mat[j, i] = comp_dist

        # Distance threshold for Agglomerative Clustering
        threshold = 1.0 - AIConfig.COMPOSITE_SCORE_THRESHOLD
        clustering = AgglomerativeClustering(
            metric='precomputed',
            linkage='average',
            distance_threshold=threshold,
            n_clusters=None
        )
        labels = clustering.fit_predict(dist_mat)
        
        result_df = df.copy()
        result_df['cluster_id'] = [f"cluster_{lbl:04d}" for lbl in labels]
        
        # Calculate cluster sizes to mark duplicates
        cluster_counts = result_df['cluster_id'].value_counts()
        result_df['is_duplicate'] = result_df['cluster_id'].map(lambda cid: cluster_counts[cid] > 1)
        
        metrics = {}
        if 'group_id' in df.columns:
            ari = adjusted_rand_score(df['group_id'], labels)
            metrics['adjusted_rand_index'] = float(ari)
            metrics['total_clusters_found'] = int(len(set(labels)))
            metrics['ground_truth_clusters'] = int(df['group_id'].nunique())

        return result_df, metrics
