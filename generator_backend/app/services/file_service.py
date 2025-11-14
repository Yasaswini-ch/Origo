from pathlib import Path
from typing import Any, Dict

BASE_STORAGE_DIR = Path(__file__).resolve().parent.parent / 'storage'


def _write_files(base_dir: Path, files: Dict[str, str]) -> None:
    for relative_path, content in files.items():
        file_path = base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')


def save_project(project_id: str, output: Dict[str, Any]) -> None:
    '''Save the generated project structure to storage/<project_id>.'''
    project_dir = BASE_STORAGE_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    frontend_files = output.get('frontend_files') or {}
    backend_files = output.get('backend_files') or {}
    readme_content = output.get('README') or ''

    if isinstance(frontend_files, dict):
        _write_files(project_dir / 'frontend', frontend_files)

    if isinstance(backend_files, dict):
        _write_files(project_dir / 'backend', backend_files)

    if isinstance(readme_content, str) and readme_content:
        (project_dir / 'README.md').write_text(readme_content, encoding='utf-8')
