import io
import json
import os
from zipfile import ZipFile
import pytest

import app.services.llm_service as llm
import app.services.file_service as file_service
from app.services.zip_service import create_zip
from app.services.metadata_service import write_metadata, read_metadata
from app.services.storage_service import get_project_dir, cleanup_projects
from app.utils.errors import ValidationFailedError, JsonParsingError, ZipError, BadRequestError


def _generate(client, **kwargs):
    payload = {
        "idea": kwargs.get("idea", "Edge Cases"),
        "target_users": kwargs.get("target_users", "qa"),
        "features": kwargs.get("features", "a,b"),
        "stack": kwargs.get("stack", "react+fastapi"),
    }
    r = client.post("/generate", json=payload)
    assert r.status_code == 200
    return r.json()


def test_invalid_filenames_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)
    bad = {
        "frontend_files": {"../secret.txt": "oops"},
        "backend_files": {"app/main.py": "print('ok')"},
        "README": "hi",
    }
    with pytest.raises(ValidationFailedError):
        file_service.save_project("pid", bad)


def test_malformed_json_repair_and_error_paths():
    txt = """
    ```json
    {"frontend_files": {"src/index.js": "ok",}, "backend_files": {"app/main.py": "ok",}, "README": "x",}
    ``` trailing
    """
    repaired = llm._repair_json_text(txt)
    data = json.loads(repaired)
    norm = llm._normalize_output_dict(data)
    assert set(norm.keys()) >= {"frontend_files", "backend_files", "README"}


def test_zip_integrity_failure(tmp_path, monkeypatch):
    # Create project with no files and attempt zipping -> ZipError
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)
    from app.services.zip_service import BASE_STORAGE_DIR as ZIP_BASE
    # Patch zip BASE to our temp dir too
    import app.services.zip_service as zs
    monkeypatch.setattr(zs, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)

    pid = "p1"
    pdir = (tmp_path / "storage" / pid)
    pdir.mkdir(parents=True)
    with pytest.raises(ZipError):
        create_zip(pid)


def test_cleanup_env_var_and_dry_run(tmp_path, monkeypatch):
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)
    import app.services.zip_service as zs
    import app.services.storage_service as ss
    monkeypatch.setattr(zs, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)
    monkeypatch.setattr(ss, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)

    # Create a project and metadata 10 days old
    pid = "old"
    pdir = get_project_dir(pid)
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "project.json").write_text(json.dumps({"project_id": pid, "created_at": "2000-01-01T00:00:00Z"}))

    monkeypatch.setenv("ORIGO_CLEANUP_DAYS", "7")
    res = cleanup_projects(older_than_days=None, dry_run=True)
    assert res["dry_run"] is True
    assert pid in res["deleted"]

    # Now perform real deletion
    res2 = cleanup_projects(older_than_days=7, dry_run=False)
    assert pid in res2["deleted"]


def test_admin_cleanup_endpoint(client, monkeypatch):
    monkeypatch.setenv("ORIGO_CLEANUP_DAYS", "3")
    r = client.post("/admin/cleanup", params={"dry_run": True})
    assert r.status_code == 200
    body = r.json()
    assert "deleted" in body and "kept" in body


def test_search_and_get_project_endpoints(client):
    data = _generate(client, idea="Search Zeta", features="zeta,alpha")
    pid = data["project_id"]

    # GET /projects/{id}
    r = client.get(f"/projects/{pid}")
    assert r.status_code == 200
    md = r.json()
    assert md["project_id"] == pid

    # POST /projects/search
    r2 = client.post("/projects/search", json={"query": "zeta"})
    assert r2.status_code == 200
    arr = r2.json()
    assert any(item["project_id"] == pid for item in arr)


def test_update_endpoint_and_version_rules(client):
    data = _generate(client, idea="V1", features="a")
    pid = data["project_id"]

    old = read_metadata(pid)
    r = client.put(f"/projects/update/{pid}", json={"target_users": "ops"})
    assert r.status_code == 200
    new = r.json()
    assert new["target_users"] == "ops"
    assert new["version"] != old["version"]
    assert new["updated_at"] >= old["updated_at"]

    # invalid field
    bad = client.put(f"/projects/update/{pid}", json={"bad": 1})
    assert bad.status_code == 422
    assert bad.json()["error_code"] == "VALIDATION_FAILED"


def test_generate_branches_and_retry_mock(client, monkeypatch):
    # Force OpenAI path to raise JSON parsing error after repair to test error code
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    class DummyOpenAI:
        class ChatCompletion:
            @staticmethod
            def create(**kwargs):
                return type("Resp", (), {"choices": [type("C", (), {"message": {"content": "not-json"}})]})
    monkeypatch.setattr(llm, "openai", DummyOpenAI)

    r = client.post("/generate", json={
        "idea": "Bad JSON",
        "target_users": "qa",
        "features": "a",
        "stack": "s",
    })
    # Our global handler returns structured 502 JSON_PARSING_ERROR
    assert r.status_code == 502
    body = r.json()
    assert body["error_code"] == "JSON_PARSING_ERROR"


def test_zip_download_alias_and_integrity(client):
    data = _generate(client)
    pid = data["project_id"]
    r = client.get(f"/download/{pid}")
    assert r.status_code == 200
    buf = io.BytesIO(r.content)
    with ZipFile(buf) as z:
        assert any(n.startswith("frontend/") for n in z.namelist())
        assert any(n.startswith("backend/") for n in z.namelist())


def test_llm_retries_then_success(client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    monkeypatch.setenv("ORIGO_LLM_MAX_RETRIES", "3")
    monkeypatch.setenv("ORIGO_LLM_RETRY_BASE_SEC", "0.0")
    monkeypatch.setenv("ORIGO_LLM_TIMEOUT_SEC", "0.1")

    calls = {"n": 0}

    class DummyOpenAI2:
        class ChatCompletion:
            @staticmethod
            def create(**kwargs):
                calls["n"] += 1
                if calls["n"] < 3:
                    raise RuntimeError("transient")
                # On third attempt return valid JSON
                content = json.dumps({
                    "frontend_files": {"src/index.js": "console.log('x')"},
                    "backend_files": {"app/main.py": "print('x')"},
                    "README": "ok",
                })
                return type("Resp", (), {"choices": [type("C", (), {"message": {"content": content}})]})

    monkeypatch.setattr(llm, "openai", DummyOpenAI2)

    r = client.post("/generate", json={
        "idea": "Retry Works",
        "target_users": "qa",
        "features": "a",
        "stack": "s",
    })
    assert r.status_code == 200
    out = r.json()
    assert out["status"] == "success"
    assert calls["n"] == 3

