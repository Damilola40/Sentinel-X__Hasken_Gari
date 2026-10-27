"""
Module 2: Sentence Embedding & Cosine Similarity Engine
Encodes text reports into dense semantic vectors and computes pairwise similarities.
"""

import numpy as np
from typing import List
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    from sklearn.feature_extraction.text import TfidfVectorizer

from .ai_config import AIConfig

class SimilarityEngine:
    def __init__(self, model_name: str = AIConfig.NLP_EMBEDDING_MODEL):
        self.model_name = model_name
        if HAS_SENTENCE_TRANSFORMERS:
            self.model = SentenceTransformer(model_name)
        else:
            print("[SimilarityEngine Warning] sentence-transformers not installed. Falling back to TF-IDF Vectorizer.")
            self.model = TfidfVectorizer(max_features=2000)

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encodes a list of text strings into embedding vectors.
        """
        if not texts:
            return np.array([])
        
        if HAS_SENTENCE_TRANSFORMERS:
            return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        else:
            # Fallback vectorizer
            if hasattr(self.model, 'vocabulary_') and self.model.vocabulary_:
                return self.model.transform(texts).toarray()
            else:
                return self.model.fit_transform(texts).toarray()

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Computes cosine similarity between two text reports.
        """
        embeddings = self.encode([text1, text2])
        sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(sim)
