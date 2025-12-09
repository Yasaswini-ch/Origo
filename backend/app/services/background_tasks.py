"""Background task helpers and DB logging for task status."""

from datetime import datetime

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.background_task import BackgroundTaskStatus
from app.ml.ml_train import train_models


def _log_task_status(task_type: str, status: str, detail: str | None = None) -> None:
    """Create or update a BackgroundTaskStatus row.

    This is a helper used by background tasks to persist their status.
    """

    db: Session = SessionLocal()
    try:
        entry = BackgroundTaskStatus(
            task_type=task_type,
            status=status,
            detail=detail,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(entry)
        db.commit()
    finally:
        db.close()


def _retrain_task() -> None:
    """Run the ML training pipeline and log its result as a background task."""

    result = train_models()
    detail = f"ML retrain finished: {result}"
    _log_task_status("retrain", "completed", detail=detail)


def schedule_retrain_placeholder(background_tasks: BackgroundTasks) -> None:
    """Schedule the real retrain task using FastAPI BackgroundTasks."""

    _log_task_status("retrain", "scheduled", detail="Retrain scheduled")
    background_tasks.add_task(_retrain_task)
