from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


BASE_STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"


def create_zip(project_id: str) -> Path:
    project_dir = BASE_STORAGE_DIR / project_id
    if not project_dir.exists() or not project_dir.is_dir():
        raise FileNotFoundError(f"Project folder not found for id: {project_id}")

    BASE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = BASE_STORAGE_DIR / f"{project_id}.zip"

    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zipf:
        frontend_dir = project_dir / "frontend"
        if frontend_dir.exists() and frontend_dir.is_dir():
            for path in frontend_dir.rglob("*"):
                if path.is_file():
                    arcname = Path("frontend") / path.relative_to(frontend_dir)
                    zipf.write(path, arcname)

        backend_dir = project_dir / "backend"
        if backend_dir.exists() and backend_dir.is_dir():
            for path in backend_dir.rglob("*"):
                if path.is_file():
                    arcname = Path("backend") / path.relative_to(backend_dir)
                    zipf.write(path, arcname)

        readme_file = project_dir / "README.md"
        if readme_file.exists() and readme_file.is_file():
            zipf.write(readme_file, "README.md")

    return zip_path
