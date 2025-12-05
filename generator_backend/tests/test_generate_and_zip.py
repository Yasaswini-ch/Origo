from pathlib import Path
import io
import json
from zipfile import ZipFile

import app.services.file_service as file_service


def test_generate_creates_files_and_metadata_and_zip(client):
    payload = {
        "idea": "Todo SaaS",
        "target_users": "teams",
        "features": "auth,todos,sharing",
        "stack": "react+fastapi",
    }

    # Generate project
    resp = client.post("/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    project_id = data["project_id"]

    # Storage paths
    project_dir = file_service.BASE_STORAGE_DIR / project_id
    assert project_dir.exists()
    assert (project_dir / "frontend").exists()
    assert (project_dir / "backend").exists()

    # Metadata exists
    meta_file = project_dir / "project.json"
    assert meta_file.exists()
    meta = json.loads(meta_file.read_text())
    assert meta["project_id"] == project_id
    assert meta["idea"] == payload["idea"]

    # Download ZIP and verify not empty
    dl = client.get(f"/projects/{project_id}/download")
    assert dl.status_code == 200
    content = io.BytesIO(dl.content)
    with ZipFile(content) as z:
        names = z.namelist()
        assert len(names) > 0
        assert any(n.startswith("frontend/") for n in names)
        assert any(n.startswith("backend/") for n in names)
        assert any(n == "README.md" for n in names)
