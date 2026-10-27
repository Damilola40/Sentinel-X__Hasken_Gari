from pathlib import Path

from .preprocessing import TextPreprocessor
from .classification import IncidentClassifier

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"

_preprocessor = TextPreprocessor()
_classifier = IncidentClassifier(model_dir=str(ARTIFACTS_DIR))
_classifier.load_models()  # fails at startup if the .joblib files are missing


def classify_report(title: str, description: str) -> dict:
    cleaned = _preprocessor.process_report(title, description)
    result = _classifier.predict(cleaned["combined_text"])
    return {
        "title": cleaned["clean_title"],
        "description": cleaned["clean_description"],
        **result,
    }