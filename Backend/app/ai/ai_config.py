"""
Sentinel-X AI Engine Configuration File
Contains all configurable hyperparameters, correlation thresholds, and model settings.
"""

class AIConfig:
    # -------------------------------------------------------------
    # Module 1: STT & NLP Classification Settings
    # -------------------------------------------------------------
    STT_MODEL_SIZE = "small"  # options: tiny, base, small, medium (faster-whisper)
    STT_DEVICE = "auto"        # cuda / cpu
    NLP_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Category and Severity Labels (derived from nigeria_incident_dataset.csv)
    CATEGORIES = [
        "banditry", "kidnapping", "armed_robbery", "communal_clash",
        "terrorism_insurgency", "cattle_rustling", "arson", "ambush_roadblock",
        "accident", "fire", "flood", "other"
    ]
    
    SEVERITY_LEVELS = ["low", "medium", "high", "critical"]
    SEVERITY_WEIGHTS = {"low": 1.0, "medium": 2.0, "high": 3.0, "critical": 4.0}

    # -------------------------------------------------------------
    # Module 2: Report Correlation & Duplicate Detection Thresholds
    # -------------------------------------------------------------
    CORRELATION_SPATIAL_RADIUS_KM = 5.0     # Max spatial distance (Haversine) in kilometers
    CORRELATION_TIME_WINDOW_HOURS = 12.0    # Max temporal delta in hours
    SEMANTIC_SIMILARITY_THRESHOLD = 0.78    # Minimum Cosine Similarity (0.0 to 1.0)
    COMPOSITE_SCORE_THRESHOLD = 0.75        # Combined score threshold to declare a duplicate/correlation
    
    # Weights for Composite Similarity calculation
    WEIGHT_SEMANTIC = 0.45
    WEIGHT_GEOSPATIAL = 0.35
    WEIGHT_TEMPORAL = 0.20

    # -------------------------------------------------------------
    # Module 3: AI Risk Scoring & Anomaly Engine
    # -------------------------------------------------------------
    RISK_WINDOW_SHORT_DAYS = 7
    RISK_WINDOW_LONG_DAYS = 30
    ISOLATION_FOREST_CONTAMINATION = 0.05   # Flag top 5% unexpected spikes as anomalies
    
    # Thresholds for Human Verification Alert Flagging
    HUMAN_REVIEW_SEVERITY_LEVELS = ["high", "critical"]
    HUMAN_REVIEW_CONFIDENCE_MIN = 0.70
