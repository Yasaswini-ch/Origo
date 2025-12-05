from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import logging
from ..utils.errors import ZipError


BASE_STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"
logger = logging.getLogger(__name__)


def create_zip(project_id: str) -> Path:
    project_dir = BASE_STORAGE_DIR / project_id
    if not project_dir.exists() or not project_dir.is_dir():
        raise FileNotFoundError(f"Project folder not found for id: {project_id}")

    BASE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = BASE_STORAGE_DIR / f"{project_id}.zip"

    try:
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as zipf:
            frontend_dir = project_dir / "frontend"
            if frontend_dir.exists() and frontend_dir.is_dir():
                for path in frontend_dir.rglob("*"):
                    if path.is_file():
                        arcname = Path("frontend") / path.relative_to(frontend_dir)
                        zipf.write(path, arcname)
                        logger.info("Added to zip: %s", arcname)

            backend_dir = project_dir / "backend"
            if backend_dir.exists() and backend_dir.is_dir():
                for path in backend_dir.rglob("*"):
                    if path.is_file():
                        arcname = Path("backend") / path.relative_to(backend_dir)
                        zipf.write(path, arcname)
                        logger.info("Added to zip: %s", arcname)

            readme_file = project_dir / "README.md"
            if readme_file.exists() and readme_file.is_file():
                zipf.write(readme_file, "README.md")
                logger.info("Added to zip: README.md")

            # Integrity check
            names = zipf.namelist()
            if not names:
                logger.error("Created empty zip for project %s", project_id)
                raise ZipError(message="Zip archive is empty", details={"project_id": project_id})
    except ZipError:
        raise
    except Exception as exc:
        logger.error("Zip creation failed for %s: %s", project_id, exc)
        raise ZipError(details={"project_id": project_id, "error": str(exc)})

    return zip_path
