from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, UTC
import json
import logging
import shutil

from .file_service import BASE_STORAGE_DIR
from .zip_service import create_zip
from ..utils.errors import NotFoundError, ValidationFailedError

logger = logging.getLogger(__name__)

def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def bump_patch_version(meta: Dict[str, Any]) -> str:
    raw = str(meta.get("version", "1.0.0"))
    try:
        parts = [int(x) for x in raw.split(".")]
        while len(parts) < 3:
            parts.append(0)
        parts[2] += 1
        new = f"{parts[0]}.{parts[1]}.{parts[2]}"
    except Exception:
        new = "1.0.0"
    meta["version"] = new
    return new




def write_metadata(*, project_id: str, idea: str, target_users: str, features: str, stack: str, saved: Dict[str, Any]) -> Dict[str, Any]:
    project_dir = BASE_STORAGE_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    # Normalize features list (comma/semicolon separated tolerated)
    features_list: List[str] = []
    if isinstance(features, list):
        features_list = [str(x).strip() for x in features if str(x).strip()]
    elif isinstance(features, str):
        raw = features.replace(";", ",")
        features_list = [x.strip() for x in raw.split(",") if x.strip()]

    frontend_paths = sorted(list(saved.get("frontend_files", {}).keys()))
    backend_paths = sorted(list(saved.get("backend_files", {}).keys()))

    now = _now_iso()
    meta: Dict[str, Any] = {
        "project_id": project_id,
        "created_at": now,
        "updated_at": now,
        "idea": idea,
        "target_users": target_users,
        "features": features_list,
        "stack": stack,
        "frontend_files": frontend_paths,
        "backend_files": backend_paths,
        "version": "1.0.0",
    }

    meta_path = project_dir / "project.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Wrote expanded metadata for project %s", project_id)
    return meta


def list_folder_structure(project_id: str) -> Dict[str, Any]:
    project_dir = BASE_STORAGE_DIR / project_id
    if not project_dir.exists():
        raise NotFoundError(message="Project not found", details={"project_id": project_id})

    frontend_dir = project_dir / "frontend"
    backend_dir = project_dir / "backend"
    readme_file = project_dir / "README.md"
    zip_file = BASE_STORAGE_DIR / f"{project_id}.zip"

    def list_rel(dir_path: Path) -> List[str]:
        if not dir_path.exists():
            return []
        return sorted([str(p.relative_to(dir_path)) for p in dir_path.rglob("*") if p.is_file()])

    return {
        "frontend": list_rel(frontend_dir),
        "backend": list_rel(backend_dir),
        "README.md": readme_file.exists(),
        "project.zip": zip_file.exists(),
    }


def update_metadata_fields(project_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    meta = read_metadata(project_id)

    allowed = {"idea", "target_users", "features", "stack"}
    if any(k not in allowed for k in patch.keys()):
        raise ValidationFailedError(details={"invalid_fields": [k for k in patch.keys() if k not in allowed]})

    if "features" in patch:
        feats = patch["features"]
        if isinstance(feats, str):
            feats = [x.strip() for x in feats.replace(";", ",").split(",") if x.strip()]
        if not isinstance(feats, list):
            raise ValidationFailedError(details={"features": "must be list[str] or comma-separated string"})
        patch["features"] = feats

    meta.update({k: v for k, v in patch.items() if k in allowed})
    meta["updated_at"] = _now_iso()
    bump_patch_version(meta)

    meta_path = BASE_STORAGE_DIR / project_id / "project.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Updated metadata for %s; version bumped to %s", project_id, meta["version"])
    return meta


def duplicate_project(project_id: str) -> Dict[str, Any]:
    # 1. Validate source exists
    src_dir = BASE_STORAGE_DIR / project_id
    if not src_dir.exists():
        raise NotFoundError(details={"project_id": project_id})

    src_meta = read_metadata(project_id)

    # 2. Create new project_id
    from ..utils.ids import generate_project_id
    new_id = generate_project_id()

    # 3. Copy folder
    dst_dir = BASE_STORAGE_DIR / new_id
    shutil.copytree(src_dir, dst_dir)

    # 4. Rewrite metadata
    new_meta = dict(src_meta)
    new_meta["project_id"] = new_id
    new_meta["created_at"] = _now_iso()
    new_meta["version"] = "1.0.0"
    new_meta["idea"] = f"{src_meta.get('idea','')} (copy)".strip()
    (dst_dir / "project.json").write_text(json.dumps(new_meta, indent=2), encoding="utf-8")

    # 5. Rebuild ZIP for duplicate
    create_zip(new_id)
    logger.info("Duplicated project %s -> %s", project_id, new_id)

    return new_meta


def add_frontend_file_to_metadata(project_id: str, rel_path: str) -> Dict[str, Any]:
    meta = read_metadata(project_id)
    files = meta.get("frontend_files")
    if not isinstance(files, list):
        files = []
    if rel_path not in files:
        files.append(rel_path)
        files.sort()
    meta["frontend_files"] = files
    meta["updated_at"] = _now_iso()
    bump_patch_version(meta)
    meta_path = BASE_STORAGE_DIR / project_id / "project.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Registered frontend file %s for %s", rel_path, project_id)
    return meta


def search_projects(query: str) -> List[Dict[str, Any]]:
    q = (query or "").strip().lower()
    results: List[Dict[str, Any]] = []
    if not BASE_STORAGE_DIR.exists() or not q:
        return results
    for entry in BASE_STORAGE_DIR.iterdir():
        if not entry.is_dir():
            continue
        meta_path = entry / "project.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        haystacks = [
            str(meta.get("idea", "")),
            " ".join(meta.get("features", [])) if isinstance(meta.get("features"), list) else str(meta.get("features", "")),
            str(meta.get("stack", "")),
            str(meta.get("target_users", "")),
        ]
        joined = "\n".join(haystacks).lower()
        if q in joined:
            results.append({
                "project_id": meta.get("project_id"),
                "idea": meta.get("idea"),
                "stack": meta.get("stack"),
                "created_at": meta.get("created_at"),
                "version": meta.get("version", "1.0.0"),
            })
    return results


# Auto-fix metadata when reading
def _default_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
    changed = False
    if "version" not in meta or not isinstance(meta.get("version"), str):
        meta["version"] = "1.0.0"
        changed = True
    if "created_at" not in meta:
        meta["created_at"] = _now_iso()
        changed = True
    if "updated_at" not in meta:
        meta["updated_at"] = meta.get("created_at", _now_iso())
        changed = True
    for k in ("idea", "target_users", "stack"):
        if k not in meta:
            meta[k] = ""
            changed = True
    if not isinstance(meta.get("features"), list):
        meta["features"] = []
        changed = True
    if not isinstance(meta.get("frontend_files"), list):
        meta["frontend_files"] = []
        changed = True
    if not isinstance(meta.get("backend_files"), list):
        meta["backend_files"] = []
        changed = True
    return meta, changed


def read_metadata(project_id: str) -> Dict[str, Any]:
    meta_path = BASE_STORAGE_DIR / project_id / "project.json"
    if not meta_path.exists():
        raise NotFoundError(message="Project metadata not found", details={"project_id": project_id})
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationFailedError(message="Invalid metadata file", details={"error": str(exc)})
    meta, changed = _default_metadata(meta)
    if changed:
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        logger.info("Auto-fixed metadata for %s", project_id)
    return meta
