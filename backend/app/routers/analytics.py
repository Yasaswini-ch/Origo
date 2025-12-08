"""Analytics router wired to analytics_service."""

from fastapi import APIRouter, Query

from app.routers.schemas import (
    AnalyticsOverviewResponse,
    ModelComparisonResponse,
    PCAProjectionResponse,
    TrendsResponse,
)
from app.services import analytics_service


router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_overview():
    data = analytics_service.get_overview()
    return AnalyticsOverviewResponse(**data)


@router.get("/model-comparison", response_model=ModelComparisonResponse)
async def model_comparison():
    data = analytics_service.get_model_comparison()
    return ModelComparisonResponse(**data)


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(granularity: str = Query("day", regex="^(day|week)$")):
    data = analytics_service.get_trends(granularity=granularity)
    return TrendsResponse(**data)


@router.get("/pca-projection", response_model=PCAProjectionResponse)
async def get_pca_projection():
    data = analytics_service.get_pca_projection()
    return PCAProjectionResponse(**data)
