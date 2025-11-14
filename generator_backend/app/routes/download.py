from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.zip_service import create_zip

router = APIRouter(tags=["download"])


@router.get("/projects/{project_id}/download")
async def download_project(project_id: str) -> FileResponse:
    try:
        zip_path = create_zip(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"{project_id}.zip",
    )
