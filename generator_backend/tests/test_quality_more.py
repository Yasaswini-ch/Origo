import json

def test_normalizer_from_text(client):
    raw = """
    ```json
    {"frontend_files": {"src/index.js": "ok",}, "backend_files": {"app/main.py": "ok",}, "README": "hi",}
    ```
    """
    r = client.post("/normalizer", json={"text": raw})
    assert r.status_code == 200
    out = r.json()["normalized"]
    assert set(out.keys()) >= {"frontend_files", "backend_files", "README"}


def test_consistency_check(client):
    payload = {"frontend_files": {"src/index.js": "x"}, "backend_files": {"app/main.py": "y"}, "README": "z"}
    r = client.post("/consistency-check", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] in (True, False)
    assert "required" in body


def test_performance_check(client):
    payload = {
        "frontend_files": {"src/index.js": "console.log('a')", "src/App.jsx": "export default 1"},
        "backend_files": {"app/main.py": "print('b')"},
        "README": "r",
    }
    r = client.post("/performance-check", json=payload)
    assert r.status_code == 200
    rep = r.json()["report"]
    assert rep["frontend_files"] >= 2
    assert rep["backend_files"] >= 1
    assert rep["frontend_bytes"] > 0
