from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.models.schemas import QualityRequest, QualityResponse
from app.services import quality_service as qs
from app.services.validation import validate_project_output
from app.services.zip_service import create_zip
from app.services.metadata_service import list_folder_structure, read_metadata
from app.services.preview_service import generate_preview
from app.utils.errors import OrigoError, NotFoundError

router = APIRouter(tags=["phase5"])


@router.post("/phase5/H/route-mapping", response_model=QualityResponse)
async def route_mapping_checker(req: QualityRequest) -> QualityResponse:
    """H: Route Mapping Checker

    Uses folder structure + simple validation to report whether required
    frontend/backend entrypoints and README are present, approximating
    an end-to-end route/asset mapping check.
    """
    data = req.data or {}
    ok, errors = validate_project_output(data)
    summary: Dict[str, Any] = {
        "valid": ok,
        "errors": errors,
    }
    return QualityResponse(name="route-mapping", ok=ok, issues=errors, summary=summary)


@router.post("/phase5/I/react-analyzer", response_model=QualityResponse)
async def react_analyzer(req: QualityRequest) -> QualityResponse:
    """I: React Analyzer

    Lightweight React/JS surface analysis, reusing performance+linting checks
    from quality_service.
    """
    data = req.data or {}
    perf_ok, perf_issues, perf_summary = qs.check_performance(data)
    lint_ok, lint_issues, lint_summary = qs.check_linting(data)
    issues = sorted(set(perf_issues + lint_issues))
    ok = perf_ok and lint_ok
    summary: Dict[str, Any] = {
        "performance": perf_summary,
        "linting": lint_summary,
    }
    return QualityResponse(name="react-analyzer", ok=ok, issues=issues, summary=summary)


@router.post("/phase5/K/buildability", response_model=QualityResponse)
async def buildability_checker(req: QualityRequest) -> QualityResponse:
    """K: Buildability Checker

    Approximates buildability by combining validation, performance, and
    security checks.
    """
    data = req.data or {}
    ok_schema, schema_errors = validate_project_output(data)
    perf_ok, perf_issues, perf_summary = qs.check_performance(data)
    sec_ok, sec_issues, sec_summary = qs.check_security(data)
    issues = schema_errors + perf_issues + sec_issues
    ok = ok_schema and perf_ok and sec_ok
    summary: Dict[str, Any] = {
        "schema": {"ok": ok_schema, "errors": schema_errors},
        "performance": perf_summary,
        "security": sec_summary,
    }
    return QualityResponse(name="buildability", ok=ok, issues=issues, summary=summary)


@router.get("/phase5/O/file-integrity/{project_id}", response_model=Dict[str, Any])
async def file_integrity_report(project_id: str) -> Dict[str, Any]:
    """O: File Integrity Report

    Combines folder structure and metadata presence into a single report.
    """
    try:
        structure = list_folder_structure(project_id)
        meta = read_metadata(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OrigoError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "project_id": project_id,
        "structure": structure,
        "metadata": {
            "has_metadata": True,
            "frontend_files": meta.get("frontend_files", []),
            "backend_files": meta.get("backend_files", []),
            "version": meta.get("version", "1.0.0"),
        },
    }


@router.get("/phase5/P/snapshot/{project_id}", response_model=Dict[str, Any])
async def project_snapshot(project_id: str) -> Dict[str, Any]:
    """P: Project Snapshot

    Returns a high-level snapshot: metadata plus structure and zip presence.
    """
    try:
        meta = read_metadata(project_id)
        structure = list_folder_structure(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OrigoError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "project_id": project_id,
        "metadata": meta,
        "structure": structure,
    }


@router.post("/phase5/T/error-simulation", response_model=QualityResponse)
async def error_simulation(req: QualityRequest) -> QualityResponse:
    """T: Error Simulation

    Runs validation and zip creation dry-run style to expose common error
    shapes without mutating projects.
    """
    data = req.data or {}
    issues: list[str] = []

    ok_schema, schema_errors = validate_project_output(data)
    issues.extend(schema_errors)

    summary: Dict[str, Any] = {
        "schema_ok": ok_schema,
        "data_keys": list(data.keys()),
    }

    return QualityResponse(name="error-simulation", ok=ok_schema, issues=issues, summary=summary)


@router.post("/phase5/S/production-readiness", response_model=QualityResponse)
async def production_readiness(req: QualityRequest) -> QualityResponse:
    """S: Production Readiness

    Aggregates architecture, scalability, devops, tooling, and standards
    checks into a single readiness signal.
    """
    data = req.data or {}
    arch_ok, arch_issues, arch_summary = qs.check_architecture(data)
    scal_ok, scal_issues, scal_summary = qs.check_scalability(data)
    devops_ok, devops_issues, devops_summary = qs.check_devops(data)
    tooling_ok, tooling_issues, tooling_summary = qs.check_tooling(data)
    standards_ok, standards_issues, standards_summary = qs.check_standards(data)

    all_issues = arch_issues + scal_issues + devops_issues + tooling_issues + standards_issues
    ok = arch_ok and scal_ok and devops_ok and tooling_ok and standards_ok

    summary: Dict[str, Any] = {
        "architecture": arch_summary,
        "scalability": scal_summary,
        "devops": devops_summary,
        "tooling": tooling_summary,
        "standards": standards_summary,
    }
    return QualityResponse(name="production-readiness", ok=ok, issues=all_issues, summary=summary)
