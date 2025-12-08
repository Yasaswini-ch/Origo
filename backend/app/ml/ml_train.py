"""ML training pipeline for generation analytics.

This module trains three scikit-learn models using data from the database:

* LogisticRegression for generation success probability
* RandomForestClassifier for project type / quality classification
* PCA for 2D projection of feature vectors

Trained models are stored under ``app/ml/models`` using joblib.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.generation_attempt import GenerationAttempt
from app.models.project import Project
from app.models.user_feedback import UserFeedback
from app.services.metrics_service import compute_code_metrics

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def _load_raw_data(db: Session) -> pd.DataFrame:
    """Load projects, generation attempts and feedback into a flat DataFrame.

    Each row corresponds to a GenerationAttempt joined with its Project and
    optional UserFeedback.
    """

    attempts = db.query(GenerationAttempt).all()
    rows: List[Dict] = []

    for ga in attempts:
        project: Project | None = ga.project
        feedback: UserFeedback | None = None
        if ga.id is not None:
            feedback = (
                db.query(UserFeedback)
                .filter(UserFeedback.generation_attempt_id == ga.id)
                .order_by(UserFeedback.created_at.desc())
                .first()
            )

        code = ga.code_snapshot or ""
        metrics = compute_code_metrics(code) if code else {
            "loc": 0,
            "cyclomatic_complexity": 0.0,
            "maintainability_index": 0.0,
            "pylint_score": 0.0,
            "dependency_count": 0,
            "duplication_percentage": 0.0,
            "estimated_bug_probability": 0.0,
        }

        row: Dict = {
            "generation_id": ga.id,
            "project_id": ga.project_id,
            "success": bool(ga.success),
            "generation_time_ms": ga.generation_time_ms or 0,
            "prompt_length": len(ga.prompt or ""),
            "feature_count": len((ga.prompt or "").split("\n")),
            "stack_complexity": (project.complexity if project else 0.0) or 0.0,
            "code_size": len(code),
            "project_type": (ga.project_type or (project.project_type if project else None))
            or "unknown",
            "quality_rating": (feedback.user_rating if feedback else None) or 0,
            # Metrics
            "loc": metrics["loc"],
            "cyclomatic_complexity": metrics["cyclomatic_complexity"],
            "maintainability_index": metrics["maintainability_index"],
            "pylint_score": metrics["pylint_score"],
            "dependency_count": metrics["dependency_count"],
            "duplication_percentage": metrics["duplication_percentage"],
            "estimated_bug_probability": metrics["estimated_bug_probability"],
        }

        rows.append(row)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def _build_feature_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Construct feature matrix X and targets y_success, y_type.

    - y_success: binary success flag for LogisticRegression
    - y_type: project_type label for RandomForest
    """

    if df.empty:
        return df, pd.Series(dtype=float), pd.Series(dtype=str)

    feature_cols = [
        "prompt_length",
        "feature_count",
        "stack_complexity",
        "code_size",
        "generation_time_ms",
        "loc",
        "cyclomatic_complexity",
        "maintainability_index",
        "pylint_score",
        "dependency_count",
        "duplication_percentage",
        "estimated_bug_probability",
    ]

    X = df[feature_cols].fillna(0.0)
    y_success = df["success"].astype(int)
    y_type = df["project_type"].astype(str)

    return X, y_success, y_type


def train_models() -> Dict[str, str]:
    """Train LogisticRegression, RandomForest, and PCA and persist them.

    Returns a small summary dict of what was trained.
    """

    db: Session = SessionLocal()
    try:
        df = _load_raw_data(db)
    finally:
        db.close()

    if df.empty:
        return {"status": "no-data", "detail": "No generation attempts to train on"}

    X, y_success, y_type = _build_feature_matrix(df)

    if X.empty:
        return {"status": "no-features", "detail": "Feature matrix is empty"}

    # Standardize features for models that benefit from scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.values)

    # Train LogisticRegression for success probability
    logreg = LogisticRegression(max_iter=1000)
    if y_success.nunique() > 1:
        logreg.fit(X_scaled, y_success.values)
        dump(logreg, MODELS_DIR / "logistic_success.joblib")
    else:
        logreg = None

    # Train RandomForest for project_type classification
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    if y_type.nunique() > 1:
        rf.fit(X.values, y_type.values)
        dump(rf, MODELS_DIR / "rf_project_type.joblib")
    else:
        rf = None

    # Train PCA for 2D projection
    pca = PCA(n_components=2, random_state=42)
    pca.fit(X_scaled)
    dump(pca, MODELS_DIR / "pca_2d.joblib")

    # Persist scaler as well for consistent feature scaling
    dump(scaler, MODELS_DIR / "scaler.joblib")

    return {
        "status": "ok",
        "rows": str(len(df)),
        "features": str(X.shape[1]),
        "logreg_trained": str(logreg is not None),
        "rf_trained": str(rf is not None),
        "pca_components": str(pca.n_components_),
    }
