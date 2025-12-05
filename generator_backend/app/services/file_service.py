from pathlib import Path
from typing import Any, Dict
import logging
import json
import shutil
from datetime import datetime, timedelta

from .validation import validate_project_output
from ..utils.errors import ValidationFailedError

BASE_STORAGE_DIR = Path(__file__).resolve().parent.parent / 'storage'


def _write_files(base_dir: Path, files: Dict[str, str]) -> None:
    for relative_path, content in files.items():
        try:
            if not isinstance(relative_path, str) or not isinstance(content, str) or content == "":
                logging.warning("Skipping invalid file entry: %s", relative_path)
                continue
            file_path = base_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            logging.info("Wrote file: %s", file_path)
        except Exception as exc:  # pragma: no cover
            logging.error("Failed writing file %s: %s", relative_path, exc)


def save_project(project_id: str, output: Dict[str, Any]) -> Dict[str, Any]:
    '''Save the generated project structure to storage/<project_id> and return saved structure.'''
    # Enforce validation at save-time
    is_valid, errors = validate_project_output(output)
    if not is_valid:
        logging.error("Validation failed for project %s: %s", project_id, errors)
        raise ValidationFailedError(details={"errors": errors})
    project_dir = BASE_STORAGE_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    logging.info("Ensured project directory exists: %s", project_dir)

    frontend_files = output.get('frontend_files') or {}
    backend_files = output.get('backend_files') or {}
    readme_content = output.get('README') or ''

    if isinstance(frontend_files, dict):
        logging.info("Saving %d frontend files", len(frontend_files))
        _write_files(project_dir / 'frontend', frontend_files)

    if isinstance(backend_files, dict):
        logging.info("Saving %d backend files", len(backend_files))
        _write_files(project_dir / 'backend', backend_files)

    if isinstance(readme_content, str) and readme_content:
        (project_dir / 'README.md').write_text(readme_content, encoding='utf-8')
        logging.info("Wrote README.md for project %s", project_id)

    # Return normalized structure actually intended to be saved
    result: Dict[str, Any] = {
        'project_id': project_id,
        'frontend_files': frontend_files if isinstance(frontend_files, dict) else {},
        'backend_files': backend_files if isinstance(backend_files, dict) else {},
        'README': readme_content if isinstance(readme_content, str) else '',
    }
    return result


def get_project_dir(project_id: str) -> Path:
    return BASE_STORAGE_DIR / project_id
