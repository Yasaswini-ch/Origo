import logging
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from ..services.preview_service import generate_preview as do_generate_preview
from ..services.file_service import BASE_STORAGE_DIR
from ..utils.errors import OrigoError, PreviewNotFoundError

router = APIRouter(tags=['preview'])


@router.post('/preview/{project_id}')
async def upload_preview(project_id: str, zip: UploadFile = File(...)):
    try:
        # Read bytes
        data = await zip.read()
        html = do_generate_preview(project_id, data)
        # Return location and html snippet
        rel_path = f"previews/{project_id}.html"
        return {"project_id": project_id, "preview_path": rel_path, "html": html}
    except OrigoError as exc:
        # Let global handler manage, but returning here makes FastAPI call our exception handler
        raise exc
