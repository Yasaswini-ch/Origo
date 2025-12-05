import os
import sys
from pathlib import Path
import shutil
import pytest
from fastapi.testclient import TestClient

# Ensure app package is importable when tests run from repo root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402
import app.services.file_service as file_service  # noqa: E402
import app.services.zip_service as zip_service  # noqa: E402
import app.services.metadata_service as metadata_service  # noqa: E402
import app.services.storage_service as storage_service  # noqa: E402


@pytest.fixture(autouse=True)
def temp_storage_dir(tmp_path, monkeypatch):
    """Redirect storage to a temporary folder for each test."""
    temp_dir = tmp_path / "storage"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Patch BASE_STORAGE_DIR in both services
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", temp_dir, raising=True)
    monkeypatch.setattr(zip_service, "BASE_STORAGE_DIR", temp_dir, raising=True)
    monkeypatch.setattr(metadata_service, "BASE_STORAGE_DIR", temp_dir, raising=True)
    monkeypatch.setattr(storage_service, "BASE_STORAGE_DIR", temp_dir, raising=True)

    yield temp_dir

    # Cleanup is automatic by tmp_path; explicit remove in case anything leaked
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture()
def client():
    return TestClient(app)
