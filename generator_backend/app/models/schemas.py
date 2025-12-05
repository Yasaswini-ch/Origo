'''Pydantic models used by the FastAPI application.'''

from typing import Any, Dict, Optional

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    idea: str
    target_users: str
    features: str
    stack: str


class GenerateResponse(BaseModel):
    project_id: str
    status: str
    frontend_files: Dict[str, str]
    backend_files: Dict[str, str]
    README: str
    metadata: Dict[str, Any]


class ComponentRequest(BaseModel):
    component_name: Optional[str] = None
    feature_description: Optional[str] = None
    props: Optional[str] = None


class ComponentResponse(BaseModel):
    component_name: str
    component_code: str


class PreviewRequest(BaseModel):
    frontend_files: Dict[str, str]


class PreviewResponse(BaseModel):
    html: str
    instructions: str


class QualityRequest(BaseModel):
    project_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class QualityResponse(BaseModel):
    name: str
    ok: bool
    issues: list[str]
    summary: Dict[str, Any]
