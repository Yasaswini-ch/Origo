"""Prediction helpers for trained ML models.

This module loads models trained by ``app.ml.ml_train`` and exposes
high-level helpers used by the API and services.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

import numpy as np
from joblib import load

from app.ml.ml_train import MODELS_DIR, _build_feature_matrix


def _load_model(name: str):
    path = MODELS_DIR / name
    if not path.exists():
        return None
    return load(path)


def _ensure_2d(v: np.ndarray) -> np.ndarray:
    if v.ndim == 1:
        return v.reshape(1, -1)
    return v


def predict_success(features_row: Dict[str, Any]) -> float:
    """Predict success probability for a single feature row.

    Returns a float in [0, 1]. If the model is missing, returns 0.5.
    """

    logreg = _load_model("logistic_success.joblib")
    scaler = _load_model("scaler.joblib")
    if logreg is None or scaler is None:
        return 0.5

    import pandas as pd

    df = pd.DataFrame([features_row])
    X, _, _ = _build_feature_matrix(df)
    if X.empty:
        return 0.5

    X_scaled = scaler.transform(X.values)
    probs = logreg.predict_proba(_ensure_2d(X_scaled))[0]
    # Assume positive class is at index 1
    return float(probs[1]) if len(probs) > 1 else float(probs[0])


def predict_project_type_and_quality(features_row: Dict[str, Any]) -> Dict[str, Any]:
    """Predict project_type and a pseudo quality score using RandomForest.

    Returns a dict with ``project_type`` and ``quality_score``.
    """

    rf = _load_model("rf_project_type.joblib")
    if rf is None:
        return {"project_type": "unknown", "quality_score": 0.0}

    import pandas as pd

    df = pd.DataFrame([features_row])
    X, _, y_type = _build_feature_matrix(df)
    if X.empty:
        return {"project_type": "unknown", "quality_score": 0.0}

    proba = rf.predict_proba(X.values)[0]
    classes = list(rf.classes_)
    best_idx = int(np.argmax(proba))
    project_type = str(classes[best_idx])
    quality_score = float(proba[best_idx])

    return {"project_type": project_type, "quality_score": quality_score}


def pca_projection(feature_rows: Iterable[Dict[str, Any]]) -> List[List[float]]:
    """Project a batch of feature rows into 2D via PCA model.

    Returns a list of [x, y] coordinates.
    """

    pca = _load_model("pca_2d.joblib")
    scaler = _load_model("scaler.joblib")
    if pca is None or scaler is None:
        return []

    import pandas as pd

    df = pd.DataFrame(list(feature_rows))
    X, _, _ = _build_feature_matrix(df)
    if X.empty:
        return []

    X_scaled = scaler.transform(X.values)
    coords = pca.transform(X_scaled)
    return coords.tolist()
