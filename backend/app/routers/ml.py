"""ML-specific router for prediction and retraining.

This router complements the admin retrain endpoint with a more ML-focused
API surface.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.routers.schemas import MLPredictionResponse, RetrainResponse
from app.database import SessionLocal
from app.models.generation_attempt import GenerationAttempt
from app.models.project import Project
from app.ml.predict import (
    predict_project_type_and_quality,
    predict_success,
)
from app.services.background_tasks import schedule_retrain_placeholder
from app.services.analytics_service import _build_features_for_attempt


router = APIRouter()


@router.get("/predict/{project_id}", response_model=MLPredictionResponse)
async def predict_for_project(project_id: int):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        ga = (
            db.query(GenerationAttempt)
            .filter(GenerationAttempt.project_id == project_id)
            .order_by(GenerationAttempt.created_at.desc())
            .first()
        )
        if ga is None:
            raise HTTPException(status_code=404, detail="No generation attempts for project")

        features = _build_features_for_attempt(ga, project, None)
        success_prob = predict_success(features)
        type_res = predict_project_type_and_quality(features)

        return MLPredictionResponse(
            project_id=project_id,
            success_probability=success_prob,
            project_type=type_res.get("project_type", "unknown"),
            quality_score=type_res.get("quality_score", 0.0),
        )
    finally:
        db.close()


@router.post("/retrain", response_model=RetrainResponse)
async def retrain_models(background_tasks: BackgroundTasks):
    schedule_retrain_placeholder(background_tasks)
    return RetrainResponse(status="scheduled", detail="Retrain scheduled via background task")
