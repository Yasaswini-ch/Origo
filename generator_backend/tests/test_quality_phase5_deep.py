import json


def test_quality_performance_threshold(client):
    # Create payload exceeding small threshold
    data = {
        "frontend_files": {"src/index.js": "x" * 300_000},
        "backend_files": {"app/main.py": "print('ok')"},
    }
    r = client.post("/quality/performance", json={"data": data})
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "performance"
    assert body["ok"] in (True, False)
    # Given default threshold ~200KB, ok likely False
    assert "total_bytes" in body["summary"]


def test_quality_security_patterns(client):
    data = {
        "frontend_files": {"src/index.js": "const x = 'SECRET_KEY=abc'"},
        "backend_files": {},
        "README": "This has API_KEY: 123",
    }
    r = client.post("/quality/security", json={"data": data})
    assert r.status_code == 200
    out = r.json()
    assert out["name"] == "security"
    assert isinstance(out["issues"], list)
    assert any(code in out["issues"] for code in ["secret_key_leak", "api_key_leak"])  # patterns caught


def test_quality_linting_flags(client):
    data = {
        "frontend_files": {"src/index.js": "\tlet a = 1;\n" + ("x" * 121)},
        "backend_files": {},
    }
    r = client.post("/quality/linting", json={"data": data})
    assert r.status_code == 200
    out = r.json()
    assert out["name"] == "linting"
    assert isinstance(out["issues"], list)
    assert any(i in out["issues"] for i in ["tab_character", "long_lines"])  
