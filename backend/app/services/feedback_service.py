"""Service layer for feedback creation and aggregation."""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user_feedback import UserFeedback
from app.services.background_tasks import schedule_retrain_placeholder


FEEDBACK_RETRAIN_THRESHOLD = 20


def _get_db() -> Session:
    return SessionLocal()


def create_feedback(data: Dict[str, Any]) -> UserFeedback:
    db = _get_db()
    try:
        fb = UserFeedback(
            project_id=data.get("project_id"),
            generation_attempt_id=data.get("generation_attempt_id"),
            user_rating=data.get("user_rating"),
            usefulness_score=data.get("usefulness_score"),
            accuracy_score=data.get("accuracy_score"),
            comments=data.get("comments"),
            extra_metadata=data.get("extra_metadata"),
        )
        db.add(fb)
        db.commit()
        db.refresh(fb)

        # Check if we should trigger a retrain based on total feedback count.
        total = db.query(func.count(UserFeedback.id)).scalar() or 0
        if total % FEEDBACK_RETRAIN_THRESHOLD == 0:
            # background task will be scheduled by router via schedule_retrain_placeholder
            pass

        return fb
    finally:
        db.close()


def get_feedback_summary() -> Dict[str, Optional[float]]:
    db = _get_db()
    try:
        count = db.query(func.count(UserFeedback.id)).scalar() or 0
        avg_user = db.query(func.avg(UserFeedback.user_rating)).scalar()
        avg_use = db.query(func.avg(UserFeedback.usefulness_score)).scalar()
        avg_acc = db.query(func.avg(UserFeedback.accuracy_score)).scalar()

        return {
            "count": count,
            "avg_user_rating": avg_user,
            "avg_usefulness_score": avg_use,
            "avg_accuracy_score": avg_acc,
        }
    finally:
        db.close()
