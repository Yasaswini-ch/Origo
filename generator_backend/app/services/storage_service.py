from __future__ import annotations
from typing import Any, Dict
from pathlib import Path
import json
import shutil
import logging
from datetime import datetime, timedelta, UTC, timezone
import os

from app.services.file_service import BASE_STORAGE_DIR
from app.utils.errors import BadRequestError


def get_project_dir(project_id: str) -> Path:
    return BASE_STORAGE_DIR / project_id


def list_projects() -> Dict[str, Dict[str, Any]]:
    results: Dict[str, Dict[str, Any]] = {}
    if not BASE_STORAGE_DIR.exists():
        return results
    for entry in BASE_STORAGE_DIR.iterdir():
        if entry.is_dir():
            meta_file = entry / 'project.json'
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding='utf-8'))
                    results[entry.name] = meta
                except Exception as exc:  # pragma: no cover
                    logging.warning("Failed reading metadata for %s: %s", entry.name, exc)
    return results


def delete_project(project_id: str) -> None:
    project_dir = get_project_dir(project_id)
    if project_dir.exists():
        shutil.rmtree(project_dir)
        logging.info("Deleted project dir %s", project_id)
    zip_path = BASE_STORAGE_DIR / f"{project_id}.zip"
    if zip_path.exists():
        try:
            zip_path.unlink()
            logging.info("Deleted project zip %s", zip_path.name)
        except Exception as exc:  # pragma: no cover
            logging.warning("Failed deleting zip %s: %s", zip_path, exc)


def _parse_created_at(val: Any) -> datetime | None:
    if not isinstance(val, str):
        return None
    had_z = val.endswith('Z')
    txt = val.rstrip('Z')
    try:
        dt = datetime.fromisoformat(txt)
        # If input had trailing Z or dt is naive, coerce to UTC-aware
        if dt.tzinfo is None:
            if had_z:
                return dt.replace(tzinfo=UTC)
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except Exception:
        return None


def cleanup_projects(older_than_days: int | None = None, dry_run: bool = False) -> Dict[str, Any]:
    # Resolve days: env overrides default if not provided
    if older_than_days is None:
        env_val = os.getenv("ORIGO_CLEANUP_DAYS")
        try:
            older_than_days = int(env_val) if env_val else 7
        except Exception:
            older_than_days = 7
    if older_than_days < 0:
        raise BadRequestError(details={"older_than_days": older_than_days})

    now = datetime.now(UTC)
    threshold = now - timedelta(days=older_than_days)
    projects = list_projects()
    deleted: list[str] = []
    kept: list[str] = []
    errors: list[Dict[str, Any]] = []
    for pid, meta in projects.items():
        created_at = _parse_created_at(meta.get('created_at'))
        if created_at is None:
            kept.append(pid)
            continue
        if created_at < threshold:
            try:
                if dry_run:
                    deleted.append(pid)
                else:
                    delete_project(pid)
                    deleted.append(pid)
            except Exception as exc:  # pragma: no cover
                logging.warning("Failed deleting old project %s: %s", pid, exc)
                errors.append({"project_id": pid, "error": str(exc)})
                kept.append(pid)
        else:
            kept.append(pid)
    return {
        'deleted': deleted,
        'kept': kept,
        'threshold': threshold.isoformat().replace('+00:00', 'Z'),
        'dry_run': dry_run,
        'errors': errors,
    }
