from fastapi import APIRouter, HTTPException
from typing import Any, Dict
import logging
import json

from ..services.validation import validate_project_output, REQUIRED_FRONTEND_FILES, REQUIRED_BACKEND_FILES
from ..services import llm_service as llm, quality_service as qs
from ..utils.errors import OrigoError, JsonParsingError
from ..models.schemas import QualityRequest, QualityResponse

router = APIRouter(tags=["quality"])


@router.post("/validate")
async def validate_payload(payload: Dict[str, Any]):
    try:
        ok, errors = validate_project_output(payload)
        return {"valid": ok, "errors": errors}
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/heal")
async def heal_payload(payload: Dict[str, Any]):
    try:
        # Accept either raw text under 'text' or a dict under 'data'
        if isinstance(payload.get("data"), dict):
            obj = payload["data"]
        else:
            raw = str(payload.get("text", ""))
            if not raw:
                # also allow entire payload to be treated as raw text if string
                if isinstance(payload, str):
                    raw = payload
            if not raw:
                raise JsonParsingError(message="No content to heal", details={"payload": payload})
            repaired = llm._repair_json_text(raw)
            try:
                obj = json.loads(repaired)
            except Exception as exc:
                raise JsonParsingError(details={"raw": raw, "repaired": repaired, "error": str(exc)})
        normalized = llm._normalize_output_dict(obj)
        return {"healed": normalized}
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/normalizer")
async def normalizer(payload: Dict[str, Any]):
    try:
        if isinstance(payload.get("data"), dict):
            obj = payload["data"]
        else:
            raw = str(payload.get("text", ""))
            if not raw:
                return {"normalized": llm._normalize_output_dict({})}
            repaired = llm._repair_json_text(raw)
            try:
                obj = json.loads(repaired)
            except Exception:
                obj = {}
        return {"normalized": llm._normalize_output_dict(obj)}
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/consistency-check")
async def consistency_check(payload: Dict[str, Any]):
    try:
        ok, errors = validate_project_output(payload)
        # Summarize required presence
        frontend = payload.get("frontend_files") or {}
        backend = payload.get("backend_files") or {}
        required = {
            "frontend_required_missing": [p for p in REQUIRED_FRONTEND_FILES if p not in frontend],
            "backend_required_present": [p for p in REQUIRED_BACKEND_FILES if p in backend and isinstance(backend.get(p), str) and backend.get(p)],
        }
        return {"ok": ok, "errors": errors, "required": required}
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/performance-check")
async def performance_check(payload: Dict[str, Any]):
    try:
        frontend = payload.get("frontend_files") or {}
        backend = payload.get("backend_files") or {}
        def _total_bytes(d: Dict[str, Any]) -> int:
            total = 0
            for v in d.values():
                if isinstance(v, str):
                    total += len(v.encode("utf-8"))
            return total
        report = {
            "frontend_files": len(frontend) if isinstance(frontend, dict) else 0,
            "backend_files": len(backend) if isinstance(backend, dict) else 0,
            "frontend_bytes": _total_bytes(frontend) if isinstance(frontend, dict) else 0,
            "backend_bytes": _total_bytes(backend) if isinstance(backend, dict) else 0,
            "scripts": sum(1 for k in (frontend.keys() if isinstance(frontend, dict) else []) if k.endswith(".js") or k.endswith(".jsx")),
        }
        return {"report": report}
    except OrigoError:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Phase 5 named endpoints (H–T): structured stubs

def _mk_response(name: str, ok: bool, issues: list[str], summary: Dict[str, Any]) -> QualityResponse:
    logging.info("quality.%s", name)
    return QualityResponse(name=name, ok=ok, issues=issues, summary=summary)


@router.post("/quality/performance", response_model=QualityResponse)
async def quality_performance(req: QualityRequest) -> QualityResponse:
    data = req.data or {}
    ok, issues, summary = qs.check_performance(data)
    return _mk_response("performance", ok, issues, summary)


@router.post("/quality/security", response_model=QualityResponse)
async def quality_security(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_security(req.data or {})
    return _mk_response("security", ok, issues, summary)


@router.post("/quality/architecture", response_model=QualityResponse)
async def quality_architecture(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_architecture(req.data or {})
    return _mk_response("architecture", ok, issues, summary)


@router.post("/quality/testing", response_model=QualityResponse)
async def quality_testing(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_testing(req.data or {})
    return _mk_response("testing", ok, issues, summary)


@router.post("/quality/scalability", response_model=QualityResponse)
async def quality_scalability(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_scalability(req.data or {})
    return _mk_response("scalability", ok, issues, summary)


@router.post("/quality/devops", response_model=QualityResponse)
async def quality_devops(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_devops(req.data or {})
    return _mk_response("devops", ok, issues, summary)


@router.post("/quality/versioning", response_model=QualityResponse)
async def quality_versioning(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_versioning(req.data or {})
    return _mk_response("versioning", ok, issues, summary)


@router.post("/quality/tooling", response_model=QualityResponse)
async def quality_tooling(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_tooling(req.data or {})
    return _mk_response("tooling", ok, issues, summary)


@router.post("/quality/linting", response_model=QualityResponse)
async def quality_linting(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_linting(req.data or {})
    return _mk_response("linting", ok, issues, summary)


@router.post("/quality/cleanup", response_model=QualityResponse)
async def quality_cleanup(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_cleanup(req.data or {})
    return _mk_response("cleanup", ok, issues, summary)


@router.post("/quality/metadata", response_model=QualityResponse)
async def quality_metadata(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_metadata(req.data or {})
    return _mk_response("metadata", ok, issues, summary)


@router.post("/quality/standards", response_model=QualityResponse)
async def quality_standards(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_standards(req.data or {})
    return _mk_response("standards", ok, issues, summary)


@router.post("/quality/review", response_model=QualityResponse)
async def quality_review(req: QualityRequest) -> QualityResponse:
    ok, issues, summary = qs.check_review(req.data or {})
    return _mk_response("review", ok, issues, summary)
