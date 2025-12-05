from fastapi import APIRouter, HTTPException, Query
from ..services.storage_service import list_projects, delete_project, cleanup_projects
from ..services.metadata_service import (
    read_metadata,
    list_folder_structure,
    update_metadata_fields,
    duplicate_project,
    search_projects,
)
from ..utils.errors import OrigoError, NotFoundError

router = APIRouter(tags=["projects"])


@router.get("/projects")
async def get_projects():
    return list_projects()


@router.delete("/projects/{project_id}")
async def remove_project(project_id: str):
    projects = list_projects()
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        delete_project(project_id)
        return {"status": "deleted", "project_id": project_id}
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/projects/cleanup")
async def cleanup(older_than_days: int = 7, dry_run: bool = False):
    try:
        return cleanup_projects(older_than_days=older_than_days, dry_run=dry_run)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/projects/details/{project_id}")
async def project_details(project_id: str):
    try:
        meta = read_metadata(project_id)
        structure = list_folder_structure(project_id)
        return {"metadata": meta, "structure": structure}
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/projects/update/{project_id}")
async def update_project(project_id: str, payload: dict):
    try:
        meta = update_metadata_fields(project_id, payload)
        return meta
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/projects/{project_id}/duplicate")
async def duplicate(project_id: str):
    try:
        new_meta = duplicate_project(project_id)
        return new_meta
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/projects/search")
async def search(query: str = Query("")):
    try:
        return search_projects(query)
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    try:
        return read_metadata(project_id)
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/projects/search")
async def search_post(payload: dict):
    try:
        return search_projects(payload.get("query", ""))
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/admin/cleanup")
async def admin_cleanup(older_than_days: int | None = None, dry_run: bool = True):
    try:
        return cleanup_projects(older_than_days=older_than_days, dry_run=dry_run)
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
