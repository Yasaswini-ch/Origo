"""Projects router implementing CRUD and metrics endpoints."""

from fastapi import APIRouter, HTTPException

from app.routers.schemas import (
    ProjectCreate,
    ProjectMetricsResponse,
    ProjectRead,
    ProjectUpdate,
)
from app.services import projects_service


router = APIRouter()


@router.post("", response_model=ProjectRead)
async def create_project(payload: ProjectCreate):
    project = projects_service.create_project(payload.dict())
    return project


@router.get("/history", response_model=list[ProjectRead])
async def get_project_history():
    projects = projects_service.list_projects()
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int):
    project = projects_service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: int, payload: ProjectUpdate):
    project = projects_service.update_project(project_id, payload.dict(exclude_unset=True))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: int):
    ok = projects_service.delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted", "project_id": project_id}


@router.post("/{project_id}/metrics", response_model=ProjectMetricsResponse)
async def compute_project_metrics(project_id: int):
    metrics = projects_service.compute_project_metrics(project_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail="No code snapshot available for project")
    return ProjectMetricsResponse(project_id=project_id, metrics=metrics)
