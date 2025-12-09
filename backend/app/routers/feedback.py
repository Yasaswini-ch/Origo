"""Feedback router with create and summary endpoints."""

from fastapi import APIRouter, BackgroundTasks

from app.routers.schemas import FeedbackCreate, FeedbackSummaryResponse
from app.services import feedback_service
from app.services.background_tasks import schedule_retrain_placeholder


router = APIRouter()


@router.post("")
async def submit_feedback(payload: FeedbackCreate, background_tasks: BackgroundTasks):
    fb = feedback_service.create_feedback(payload.dict())

    # Trigger retrain when threshold reached (simple heuristic based on total count).
    # We re-query summary to get latest count.
    summary = feedback_service.get_feedback_summary()
    if summary["count"] % feedback_service.FEEDBACK_RETRAIN_THRESHOLD == 0:
        schedule_retrain_placeholder(background_tasks)

    return {"status": "ok", "feedback_id": fb.id}


@router.get("", response_model=FeedbackSummaryResponse)
async def get_feedback_summary():
    summary = feedback_service.get_feedback_summary()
    return FeedbackSummaryResponse(**summary)
