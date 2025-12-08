from pathlib import Path
from typing import Dict

import joblib
import numpy as np

from .feature_extraction import FeatureExtractor


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

SUCCESS_MODEL_PATH = MODELS_DIR / "success_predictor.pkl"
TIME_MODEL_PATH = MODELS_DIR / "time_predictor.pkl"


class GenerationPredictor:
    """Simple interface for backend to predict success and time.

    Usage:
        predictor = GenerationPredictor()
        result = predictor.predict(idea, features, stack)
    """

    def __init__(self):
        if not SUCCESS_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Success model not found at {SUCCESS_MODEL_PATH}. "
                f"Train it with: python -m generator_backend.app.ml.train_success_predictor"
            )
        if not TIME_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Time model not found at {TIME_MODEL_PATH}. "
                f"Train it with: python -m generator_backend.app.ml.train_time_predictor"
            )

        self.success_model = joblib.load(SUCCESS_MODEL_PATH)
        self.time_model = joblib.load(TIME_MODEL_PATH)
        self.feature_extractor = FeatureExtractor()

    def _compute_confidence(self, success_probability: float) -> str:
        if success_probability >= 0.8:
            return "high"
        if success_probability >= 0.6:
            return "medium"
        return "low"

    def predict(self, idea: str, features: str, stack: str) -> Dict[str, float | str]:
        feature_vector = np.array(
            [self.feature_extractor.transform_to_list(idea, features, stack)],
            dtype=float,
        )

        # Success probability: try predict_proba if available, else fallback
        if hasattr(self.success_model, "predict_proba"):
            proba = self.success_model.predict_proba(feature_vector)[0, 1]
        else:
            # Some SVM configurations may not expose predict_proba.
            pred = self.success_model.predict(feature_vector)[0]
            proba = float(pred)

        success_probability = float(proba)

        # Time prediction
        estimated_time_seconds = float(self.time_model.predict(feature_vector)[0])

        confidence = self._compute_confidence(success_probability)

        return {
            "success_probability": success_probability,
            "estimated_time_seconds": estimated_time_seconds,
            "confidence": confidence,
        }
