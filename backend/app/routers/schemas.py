"""Pydantic schemas used by the API routers."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Project schemas


class ProjectBase(BaseModel):
    name: str
    project_type: Optional[str] = None
    tech_stack: Optional[str] = None
    complexity: Optional[float] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    code: Optional[str] = Field(
        default=None,
        description="Optional initial code snapshot for the project.",
    )


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    project_type: Optional[str] = None
    tech_stack: Optional[str] = None
    complexity: Optional[float] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    code: Optional[str] = None


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProjectMetricsResponse(BaseModel):
    project_id: int
    metrics: Dict[str, Any]


# Feedback schemas


class FeedbackCreate(BaseModel):
    project_id: Optional[int] = None
    generation_attempt_id: Optional[int] = None
    user_rating: Optional[int] = Field(default=None, ge=1, le=5)
    usefulness_score: Optional[float] = None
    accuracy_score: Optional[float] = None
    comments: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class FeedbackSummaryResponse(BaseModel):
    count: int
    avg_user_rating: Optional[float]
    avg_usefulness_score: Optional[float]
    avg_accuracy_score: Optional[float]


# Analytics schemas


class AnalyticsOverviewResponse(BaseModel):
    total_projects: int
    total_attempts: int
    avg_success_probability: Optional[float]
    avg_feedback_rating: Optional[float]
    avg_metrics: Dict[str, Any]


class ModelComparisonEntry(BaseModel):
    model_name: str
    accuracy: Optional[float]
    avg_confidence: Optional[float]


class ModelComparisonResponse(BaseModel):
    models: List[ModelComparisonEntry]


class TrendPoint(BaseModel):
    period_start: datetime
    success_rate: Optional[float]
    avg_quality_score: Optional[float]


class TrendsResponse(BaseModel):
    granularity: str
    points: List[TrendPoint]


class PCAProjectionResponse(BaseModel):
    points: List[List[float]]


# ML schemas


class MLPredictionResponse(BaseModel):
    project_id: int
    success_probability: float
    project_type: str
    quality_score: float


class RetrainResponse(BaseModel):
    status: str
    detail: Optional[str] = None
