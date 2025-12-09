"""Admin router with placeholder retraining endpoint and background task wiring."""
from fastapi import APIRouter, BackgroundTasks

from app.services.background_tasks import schedule_retrain_placeholder

router = APIRouter()


@router.post("/retrain")
async def retrain_models(background_tasks: BackgroundTasks):
    """Trigger background retraining placeholder task."""
    schedule_retrain_placeholder(background_tasks)
    return {"status": "scheduled", "task": "retrain"}
