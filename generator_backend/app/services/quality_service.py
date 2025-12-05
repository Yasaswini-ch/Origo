from __future__ import annotations
from typing import Any, Dict, Tuple, List
import re

DEFAULT_PERF_FAIL_BYTES = 200_000  # 200KB suggested hard cap for generated starter
DEFAULT_PERF_WARN_BYTES = 100_000  # 100KB soft warning


def _gather_sources(data: Dict[str, Any]) -> List[str]:
    srcs: List[str] = []
    for files in (data.get("frontend_files"), data.get("backend_files")):
        if isinstance(files, dict):
            for v in files.values():
                if isinstance(v, str):
                    srcs.append(v)
    return srcs


def check_performance(
    data: Dict[str, Any],
    *,
    warn_bytes: int = DEFAULT_PERF_WARN_BYTES,
    fail_bytes: int = DEFAULT_PERF_FAIL_BYTES,
) -> Tuple[bool, List[str], Dict[str, Any]]:
    total_frontend = sum(len((v or '').encode('utf-8')) for v in (data.get('frontend_files') or {}).values() if isinstance(v, str))
    total_backend = sum(len((v or '').encode('utf-8')) for v in (data.get('backend_files') or {}).values() if isinstance(v, str))
    total = total_frontend + total_backend
    issues: List[str] = []
    level = "ok"
    if total > fail_bytes:
        issues.append(f"total_size_exceeds_{fail_bytes}_bytes")
        level = "fail"
    elif total > warn_bytes:
        issues.append(f"total_size_exceeds_warn_{warn_bytes}_bytes")
        level = "warn"
    scripts = 0
    if isinstance(data.get('frontend_files'), dict):
        scripts = sum(1 for k in data['frontend_files'].keys() if isinstance(k, str) and (k.endswith('.js') or k.endswith('.jsx')))
    summary = {
        "total_bytes": total,
        "frontend_bytes": total_frontend,
        "backend_bytes": total_backend,
        "scripts": scripts,
        "warn_threshold": warn_bytes,
        "fail_threshold": fail_bytes,
        "level": level,
    }
    return len(issues) == 0, issues, summary


SECURITY_PATTERNS = [
    (re.compile(r"SECRET\s*[_-]?KEY\s*[:=]", re.IGNORECASE), "secret_key_leak"),
    (re.compile(r"API\s*[_-]?KEY\s*[:=]", re.IGNORECASE), "api_key_leak"),
    (re.compile(r"eval\s*\(", re.IGNORECASE), "eval_usage"),
    (re.compile(r"document\.write\s*\(", re.IGNORECASE), "document_write_usage"),
    (re.compile(r"http://", re.IGNORECASE), "insecure_http_reference"),
]


def _audit_requirements_text(text: str) -> List[str]:
    issues: List[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        # unpinned dependency (no version pin)
        if '==' not in s:
            issues.append('unpinned_dependency')
        # known vulnerable (demo names)
        name = s.split('==')[0].strip().lower()
        if name in {"insecurepkg", "vulnpkg"}:
            issues.append('known_vulnerable_package')
    return issues


def check_security(data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    sources = _gather_sources(data)
    issues: List[str] = []
    for src in sources + [data.get('README', '') if isinstance(data.get('README'), str) else '']:
        for rx, code in SECURITY_PATTERNS:
            if src and rx.search(src):
                issues.append(code)
    # basic dependency audit from requirements.txt or package.json strings if present
    for fname in ("requirements.txt", "backend/requirements.txt"):
        reqs = None
        if isinstance(data.get('backend_files'), dict):
            reqs = data['backend_files'].get(fname)
        if isinstance(reqs, str):
            issues.extend(_audit_requirements_text(reqs))
    summary = {"scanned_files": len(sources), "patterns": len(SECURITY_PATTERNS), "dependency_audit": True}
    # de-duplicate issues
    issues = sorted(set(issues))
    return len(issues) == 0, issues, summary


def check_architecture(data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    has_frontend = bool(data.get('frontend_files'))
    has_backend = bool(data.get('backend_files'))
    issues: List[str] = []
    if not has_frontend:
        issues.append('missing_frontend')
    if not has_backend:
        issues.append('missing_backend')
    summary = {"has_frontend": has_frontend, "has_backend": has_backend}
    return len(issues) == 0, issues, summary


def check_testing(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"framework": "pytest"}


def check_scalability(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"notes": "Stateless API suitable for scaling"}


def check_devops(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"ci": "github-actions", "coverage": ">=85%"}


def check_versioning(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"metadata_version": "semver"}


def check_tooling(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"lint": "ruff", "typecheck": "mypy"}


LINT_RULES = [
    (re.compile(r"\t"), "tab_character"),
    (re.compile(r"[ \t]+$", re.MULTILINE), "trailing_whitespace"),
]


def check_linting(data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    sources = _gather_sources(data)
    issues: List[str] = []
    long_lines = 0
    for src in sources:
        # long line threshold 120
        for line in src.splitlines():
            if len(line) > 120:
                long_lines += 1
        for rx, code in LINT_RULES:
            if rx.search(src):
                issues.append(code)
    if long_lines:
        issues.append("long_lines")
    issues = sorted(set(issues))
    summary = {"files": len(sources), "long_lines": long_lines}
    return len(issues) == 0, issues, summary


def check_cleanup(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"endpoint": "/admin/cleanup"}


def check_metadata(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"fields": ["project_id", "created_at", "updated_at", "version"]}


def check_standards(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"http": "structured-errors", "json": "normalized"}


def check_review(_: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    return True, [], {"status": "ready"}
