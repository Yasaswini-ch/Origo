import pytest

names = [
    "performance",
    "security",
    "architecture",
    "testing",
    "scalability",
    "devops",
    "versioning",
    "tooling",
    "linting",
    "cleanup",
    "metadata",
    "standards",
    "review",
]


def test_quality_phase5_endpoints(client):
    payload = {"data": {"frontend_files": {"src/index.js": "x"}, "backend_files": {"app/main.py": "y"}, "README": "z"}}
    for n in names:
        r = client.post(f"/quality/{n}", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == n
        assert isinstance(body["ok"], bool)
        assert isinstance(body["issues"], list)
        assert isinstance(body["summary"], dict)
