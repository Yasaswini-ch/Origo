"""Service layer for analytics endpoints.

Provides overview, model comparison, trends, and PCA projection.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.generation_attempt import GenerationAttempt
from app.models.project import Project
from app.models.project_performance import ProjectPerformance
from app.models.user_feedback import UserFeedback
from app.ml.predict import (
    pca_projection,
    predict_project_type_and_quality,
    predict_success,
)
from app.ml.ml_train import _build_feature_matrix


def _get_db() -> Session:
    return SessionLocal()


def _build_features_for_attempt(ga: GenerationAttempt, project: Project | None, feedback: UserFeedback | None) -> Dict[str, Any]:
    code = ga.code_snapshot or ""
    # Reuse numeric features built similarly to training, but without recomputing metrics
    # We rely on metrics already present in ga.metrics or the latest ProjectPerformance if available.
    metrics: Dict[str, Any] = {}
    if ga.metrics:
        metrics.update(ga.metrics)

    features: Dict[str, Any] = {
        "prompt_length": len(ga.prompt or ""),
        "feature_count": len((ga.prompt or "").split("\n")),
        "stack_complexity": (project.complexity if project else 0.0) or 0.0,
        "code_size": len(code),
        "generation_time_ms": ga.generation_time_ms or 0,
        "loc": metrics.get("loc", 0),
        "cyclomatic_complexity": metrics.get("cyclomatic_complexity", 0.0),
        "maintainability_index": metrics.get("maintainability_index", 0.0),
        "pylint_score": metrics.get("pylint_score", 0.0),
        "dependency_count": metrics.get("dependency_count", 0),
        "duplication_percentage": metrics.get("duplication_percentage", 0.0),
        "estimated_bug_probability": metrics.get("estimated_bug_probability", 0.0),
    }
    return features


def get_overview() -> Dict[str, Any]:
    db = _get_db()
    try:
        total_projects = db.query(func.count(Project.id)).scalar() or 0
        total_attempts = db.query(func.count(GenerationAttempt.id)).scalar() or 0

        # Average feedback rating
        feedback_q = db.query(
            func.avg(UserFeedback.user_rating),
        )
        avg_feedback_rating = feedback_q.scalar()

        # Average metrics from ProjectPerformance
        perf_rows = db.query(ProjectPerformance).all()
        metrics_accum: Dict[str, List[float]] = defaultdict(list)
        for perf in perf_rows:
            for k, v in (perf.metrics or {}).items():
                if isinstance(v, (int, float)):
                    metrics_accum[k].append(float(v))

        avg_metrics: Dict[str, float] = {}
        for k, values in metrics_accum.items():
            if values:
                avg_metrics[k] = sum(values) / len(values)

        # Success predictions per project (using last attempt)
        projects = db.query(Project).all()
        success_probs: List[float] = []
        for project in projects:
            ga = (
                db.query(GenerationAttempt)
                .filter(GenerationAttempt.project_id == project.id)
                .order_by(GenerationAttempt.created_at.desc())
                .first()
            )
            if not ga:
                continue

            feedback = (
                db.query(UserFeedback)
                .filter(UserFeedback.project_id == project.id)
                .order_by(UserFeedback.created_at.desc())
                .first()
            )
            features = _build_features_for_attempt(ga, project, feedback)
            prob = predict_success(features)
            success_probs.append(prob)

        avg_success_prob = sum(success_probs) / len(success_probs) if success_probs else None

        return {
            "total_projects": total_projects,
            "total_attempts": total_attempts,
            "avg_success_probability": avg_success_prob,
            "avg_feedback_rating": avg_feedback_rating,
            "avg_metrics": avg_metrics,
        }
    finally:
        db.close()


def get_model_comparison() -> Dict[str, Any]:
    """Return a very lightweight model-comparison summary.

    This reuses the existing predictors and reports confidences averaged
    over recent attempts. This is intentionally simple but structured.
    """

    db = _get_db()
    try:
        attempts = (
            db.query(GenerationAttempt)
            .order_by(GenerationAttempt.created_at.desc())
            .limit(50)
            .all()
        )
        if not attempts:
            return {"models": []}

        confidences: List[float] = []
        for ga in attempts:
            project = db.query(Project).filter(Project.id == ga.project_id).first()
            feedback = (
                db.query(UserFeedback)
                .filter(UserFeedback.generation_attempt_id == ga.id)
                .order_by(UserFeedback.created_at.desc())
                .first()
            )
            features = _build_features_for_attempt(ga, project, feedback)
            res = predict_project_type_and_quality(features)
            confidences.append(res.get("quality_score", 0.0))

        avg_conf = sum(confidences) / len(confidences) if confidences else None

        # We currently have one primary model pipeline; stub others for now.
        return {
            "models": [
                {
                    "model_name": "main_rf_pipeline",
                    "accuracy": None,  # could be filled from evaluation later
                    "avg_confidence": avg_conf,
                }
            ]
        }
    finally:
        db.close()


def get_trends(granularity: str = "day") -> Dict[str, Any]:
    """Build simple success-rate and quality trends over time."""

    db = _get_db()
    try:
        attempts = db.query(GenerationAttempt).all()
        feedback_rows = db.query(UserFeedback).all()

        buckets: Dict[str, Dict[str, Any]] = {}

        def bucket_key(dt: datetime) -> str:
            if granularity == "week":
                return f"{dt.isocalendar().year}-W{dt.isocalendar().week:02d}"
            else:
                return dt.date().isoformat()

        # Success rate per bucket
        for ga in attempts:
            if not ga.created_at:
                continue
            key = bucket_key(ga.created_at)
            b = buckets.setdefault(key, {"success": 0, "total": 0, "quality_scores": []})
            b["total"] += 1
            if ga.success:
                b["success"] += 1

        # Add quality scores from feedback
        for fb in feedback_rows:
            if not fb.created_at:
                continue
            key = bucket_key(fb.created_at)
            b = buckets.setdefault(key, {"success": 0, "total": 0, "quality_scores": []})
            if fb.user_rating is not None:
                b["quality_scores"].append(float(fb.user_rating))

        points: List[Dict[str, Any]] = []
        for key, b in sorted(buckets.items()):
            if "W" in key and granularity == "week":
                year, week = key.split("-W")
                period_start = datetime.fromisocalendar(int(year), int(week), 1)
            else:
                period_start = datetime.fromisoformat(key)

            success_rate = (b["success"] / b["total"]) if b["total"] else None
            avg_quality = (
                sum(b["quality_scores"]) / len(b["quality_scores"])
                if b["quality_scores"]
                else None
            )
            points.append(
                {
                    "period_start": period_start,
                    "success_rate": success_rate,
                    "avg_quality_score": avg_quality,
                }
            )

        return {"granularity": granularity, "points": points}
    finally:
        db.close()


def get_pca_projection() -> Dict[str, Any]:
    """Return PCA 2D projection of recent attempts using the trained PCA model."""

    db = _get_db()
    try:
        attempts = (
            db.query(GenerationAttempt)
            .order_by(GenerationAttempt.created_at.desc())
            .limit(100)
            .all()
        )
        if not attempts:
            return {"points": []}

        feature_rows: List[Dict[str, Any]] = []
        for ga in attempts:
            project = db.query(Project).filter(Project.id == ga.project_id).first()
            feedback = (
                db.query(UserFeedback)
                .filter(UserFeedback.generation_attempt_id == ga.id)
                .order_by(UserFeedback.created_at.desc())
                .first()
            )
            feature_rows.append(_build_features_for_attempt(ga, project, feedback))

        points = pca_projection(feature_rows)
        return {"points": points}
    finally:
        db.close()
