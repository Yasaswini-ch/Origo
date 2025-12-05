from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.services.zip_validator import analyze_zip_bytes

router = APIRouter(tags=["validation"], prefix="/validate")


@router.post("/zip")
async def validate_zip(file: UploadFile = File(...)):
    data = await file.read()
    result = analyze_zip_bytes(data)
    return result
