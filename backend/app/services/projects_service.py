"""Service layer for Project CRUD and metrics computation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.generation_attempt import GenerationAttempt
from app.models.project import Project
from app.models.project_performance import ProjectPerformance
from app.services.metrics_service import compute_code_metrics


# DB helpers


def _get_db() -> Session:
    return SessionLocal()


# CRUD operations


def create_project(data: Dict[str, Any]) -> Project:
    db = _get_db()
    try:
        project = Project(
            name=data["name"],
            project_type=data.get("project_type"),
            tech_stack=data.get("tech_stack"),
            complexity=data.get("complexity"),
            extra_metadata=data.get("extra_metadata"),
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        # Optionally create an initial GenerationAttempt with code snapshot
        code = data.get("code")
        if code is not None:
            attempt = GenerationAttempt(
                project_id=project.id,
                model_used="unknown",
                success=False,
                prompt="",
                code_snapshot=code,
            )
            db.add(attempt)
            db.commit()

        return project
    finally:
        db.close()


def get_project(project_id: int) -> Optional[Project]:
    db = _get_db()
    try:
        return db.query(Project).filter(Project.id == project_id).first()
    finally:
        db.close()


def list_projects() -> List[Project]:
    db = _get_db()
    try:
        return db.query(Project).order_by(Project.created_at.desc()).all()
    finally:
        db.close()


def update_project(project_id: int, data: Dict[str, Any]) -> Optional[Project]:
    db = _get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return None

        for field in ["name", "project_type", "tech_stack", "complexity", "extra_metadata"]:
            if field in data and data[field] is not None:
                setattr(project, field, data[field])

        db.add(project)
        db.commit()
        db.refresh(project)

        code = data.get("code")
        if code is not None:
            attempt = GenerationAttempt(
                project_id=project.id,
                model_used="unknown",
                success=False,
                prompt="",
                code_snapshot=code,
            )
            db.add(attempt)
            db.commit()

        return project
    finally:
        db.close()


def delete_project(project_id: int) -> bool:
    db = _get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return False
        db.delete(project)
        db.commit()
        return True
    finally:
        db.close()


# Metrics computation


def compute_project_metrics(project_id: int) -> Optional[Dict[str, Any]]:
    """Compute metrics for the latest code snapshot of a project.

    This will look at the most recent GenerationAttempt with a non-empty
    code_snapshot, compute metrics, persist them in ProjectPerformance, and
    return the metrics dict.
    """

    db = _get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            return None

        attempt = (
            db.query(GenerationAttempt)
            .filter(GenerationAttempt.project_id == project_id)
            .filter(GenerationAttempt.code_snapshot.isnot(None))
            .order_by(GenerationAttempt.created_at.desc())
            .first()
        )
        if attempt is None or not attempt.code_snapshot:
            return None

        metrics = compute_code_metrics(attempt.code_snapshot)

        perf = ProjectPerformance(
            project_id=project.id,
            generation_attempt_id=attempt.id,
            metrics=metrics,
            quality_score=1.0 - float(metrics.get("estimated_bug_probability", 0.0)),
        )
        db.add(perf)
        db.commit()

        return metrics
    finally:
        db.close()
