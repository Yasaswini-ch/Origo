from __future__ import annotations

import io
import os
import zipfile
import tempfile
from typing import Dict, Any, List, Tuple


def _list_files(zf: zipfile.ZipFile) -> List[str]:
    names: List[str] = []
    for name in zf.namelist():
        # Include only actual files, not directory entries
        if not name.endswith('/'):
            # Normalize to posix-style relative paths
            names.append(name)
    return names


def analyze_zip_bytes(data: bytes) -> Dict[str, Any]:
    issues: List[str] = []
    files: List[str] = []

    # Try open zip
    try:
        bio = io.BytesIO(data)
        with zipfile.ZipFile(bio) as zf:
            # Extract to temp dir as required
            with tempfile.TemporaryDirectory() as tmpdir:
                try:
                    zf.extractall(tmpdir)
                except Exception:
                    # If extraction fails, treat as invalid/corrupted
                    return {
                        "ok": False,
                        "issues": ["invalid_zip"],
                        "files": [],
                        "summary": {"has_frontend": False, "has_backend": False, "total_files": 0},
                    }
            files = _list_files(zf)
    except zipfile.BadZipFile:
        return {
            "ok": False,
            "issues": ["invalid_zip"],
            "files": [],
            "summary": {"has_frontend": False, "has_backend": False, "total_files": 0},
        }

    if len(files) == 0:
        issues.append("empty_zip")

    # Determine presence of frontend/backend by folder prefix
    def has_dir(prefix: str) -> bool:
        p = prefix.rstrip('/') + '/'
        return any(f.startswith(p) for f in files)

    has_frontend = has_dir('frontend')
    has_backend = has_dir('backend')

    # Validate basic files
    required = [
        'frontend/package.json',
        'backend/app/main.py',
    ]
    for req in required:
        if req not in files:
            issues.append(f"missing:{req}")

    summary = {
        "has_frontend": has_frontend,
        "has_backend": has_backend,
        "total_files": len(files),
    }

    ok = len(issues) == 0
    return {
        "ok": ok,
        "issues": issues,
        "files": files,
        "summary": summary,
    }
