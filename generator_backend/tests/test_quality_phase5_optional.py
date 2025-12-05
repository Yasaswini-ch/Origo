def test_quality_security_dep_audit(client):
    data = {
        "backend_files": {
            "requirements.txt": "fastapi\nuvicorn==0.23\ninsecurepkg==1.0\n"
        }
    }
    r = client.post("/quality/security", json={"data": data})
    assert r.status_code == 200
    out = r.json()
    assert out["name"] == "security"
    # unpinned 'fastapi' and known vulnerable 'insecurepkg'
    assert any(i in out["issues"] for i in ["unpinned_dependency", "known_vulnerable_package"]) 


def test_quality_performance_levels(client):
    # Under warn
    small = {"frontend_files": {"src/index.js": "x" * 1000}}
    r1 = client.post("/quality/performance", json={"data": small})
    assert r1.status_code == 200
    assert r1.json()["summary"]["level"] in ("ok", "warn", "fail")

    # Over warn (100KB)
    mid = {"frontend_files": {"src/index.js": "x" * 120_000}}
    r2 = client.post("/quality/performance", json={"data": mid})
    assert r2.status_code == 200
    assert r2.json()["summary"]["level"] in ("warn", "fail")

    # Over fail (200KB)
    big = {"frontend_files": {"src/index.js": "x" * 220_000}}
    r3 = client.post("/quality/performance", json={"data": big})
    assert r3.status_code == 200
    assert r3.json()["summary"]["level"] == "fail"
