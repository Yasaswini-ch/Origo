import json
from pathlib import Path
from time import sleep

from app.services.metadata_service import read_metadata
from app.services.storage_service import get_project_dir
import app.services.file_service as file_service


def _generate(client, idea="Idea A", target_users="devs", features="auth,db", stack="react+fastapi"):
    resp = client.post(
        "/generate",
        json={
            "idea": idea,
            "target_users": target_users,
            "features": features,
            "stack": stack,
        },
    )
    assert resp.status_code == 200
    return resp.json()


def test_metadata_expanded_and_version_defaults(client):
    data = _generate(client, idea="Searchable Project", features="auth, billing")
    pid = data["project_id"]

    # Response contains metadata with required fields
    meta = data["metadata"]
    assert meta["project_id"] == pid
    assert isinstance(meta["created_at"], str)
    assert meta["idea"] == "Searchable Project"
    assert meta["target_users"] == "devs"
    assert meta["features"] == ["auth", "billing"]
    assert meta["stack"] == "react+fastapi"
    assert isinstance(meta["frontend_files"], list)
    assert isinstance(meta["backend_files"], list)
    assert meta["version"] == "1.0.0"

    # Read metadata from disk and ensure parity
    disk_meta = read_metadata(pid)
    for k in [
        "project_id",
        "idea",
        "target_users",
        "features",
        "stack",
        "version",
    ]:
        assert disk_meta[k] == meta[k]


def test_details_endpoint_and_structure(client):
    data = _generate(client, idea="Details Test", features="a,b")
    pid = data["project_id"]

    r = client.get(f"/projects/details/{pid}")
    assert r.status_code == 200
    body = r.json()
    md = body["metadata"]
    st = body["structure"]

    assert md["project_id"] == pid
    assert isinstance(st["frontend"], list)
    assert isinstance(st["backend"], list)
    assert st["README.md"] is True
    assert st["project.zip"] is True

    nf = client.get("/projects/details/does-not-exist")
    assert nf.status_code == 404
    err = nf.json()
    assert err.get("error_code") == "NOT_FOUND"


def test_update_patching_and_version_bump(client):
    data = _generate(client, idea="Initial Idea", features="x,y")
    pid = data["project_id"]

    old_meta = read_metadata(pid)

    patch = {
        "idea": "Updated Idea",
        "features": ["x", "y", "z"],
    }
    r = client.put(f"/projects/update/{pid}", json=patch)
    assert r.status_code == 200
    new_meta = r.json()

    assert new_meta["idea"] == "Updated Idea"
    assert new_meta["features"] == ["x", "y", "z"]
    assert new_meta["target_users"] == old_meta["target_users"]
    assert new_meta["stack"] == old_meta["stack"]
    assert new_meta["created_at"] == old_meta["created_at"]
    assert new_meta["version"] != old_meta["version"]

    # Invalid field should 422
    bad = client.put(f"/projects/update/{pid}", json={"unknown": "x"})
    assert bad.status_code == 422
    body = bad.json()
    assert body.get("error_code") == "VALIDATION_FAILED"


def test_duplication_endpoint(client):
    data = _generate(client, idea="To Duplicate", features="one,two")
    pid = data["project_id"]

    r = client.post(f"/projects/{pid}/duplicate")
    assert r.status_code == 200
    meta = r.json()

    new_id = meta["project_id"]
    assert new_id != pid
    assert meta["idea"].endswith("(copy)")
    assert meta["version"] == "1.0.0"

    # Check files exist
    new_dir = get_project_dir(new_id)
    assert (new_dir / "project.json").exists()
    assert (file_service.BASE_STORAGE_DIR / f"{new_id}.zip").exists()

    # Original intact
    orig_dir = get_project_dir(pid)
    assert (orig_dir / "project.json").exists()


def test_search_endpoint(client):
    # Ensure projects exist
    _ = _generate(client, idea="Search Billing", features="alpha,billing", stack="react")
    _ = _generate(client, idea="Analytics", features="metrics,charts", stack="nextjs")

    # idea match
    r1 = client.get("/projects/search", params={"query": "Billing"})
    assert r1.status_code == 200
    arr1 = r1.json()
    assert any("Billing" in (x.get("idea") or "") for x in arr1)

    # features match
    r2 = client.get("/projects/search", params={"query": "metrics"})
    assert r2.status_code == 200
    arr2 = r2.json()
    assert any(x for x in arr2)

    # stack match
    r3 = client.get("/projects/search", params={"query": "nextjs"})
    assert r3.status_code == 200
    arr3 = r3.json()
    assert any(x for x in arr3)

    # empty results
    r4 = client.get("/projects/search", params={"query": "zzz-not-found"})
    assert r4.status_code == 200
    assert r4.json() == []
