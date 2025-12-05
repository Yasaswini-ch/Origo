import json
import pytest

def test_validate_endpoint(client):
    bad = {"frontend_files": {}, "backend_files": {}, "README": ""}
    resp = client.post("/validate", json=bad)
    assert resp.status_code == 200
    out = resp.json()
    assert out["valid"] is False
    assert any("frontend_files" in e or "backend_files" in e for e in out["errors"]) or out["errors"]


def test_heal_endpoint_from_text(client):
    raw = """
    ```json
    {"frontend_files": {"src/index.js": "ok",}, "backend_files": {"app/main.py": "ok",}, "README": "hi",}
    ```
    """
    resp = client.post("/heal", json={"text": raw})
    assert resp.status_code == 200
    body = resp.json()
    healed = body["healed"]
    assert set(healed.keys()) >= {"frontend_files", "backend_files", "README"}


def test_heal_endpoint_from_dict(client):
    data = {"frontend_files": {"src/index.js": "x"}, "backend_files": {"app/main.py": "y"}, "README": "z"}
    resp = client.post("/heal", json={"data": data})
    assert resp.status_code == 200
    healed = resp.json()["healed"]
    assert healed["frontend_files"]["src/index.js"] == "x"
