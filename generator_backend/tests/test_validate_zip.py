import io
import zipfile


def make_zip(files):
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            if content is None:
                # directory entry
                zf.writestr(path.rstrip('/') + '/', '')
            else:
                zf.writestr(path, content)
    bio.seek(0)
    return bio


def test_valid_zip(client):
    files = {
        'frontend/package.json': '{"name":"app"}',
        'backend/app/main.py': 'print("ok")',
        'README.md': '# Test',
    }
    bio = make_zip(files)
    r = client.post('/validate/zip', files={'file': ('proj.zip', bio.getvalue(), 'application/zip')})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["summary"]["has_frontend"] is True
    assert data["summary"]["has_backend"] is True
    assert 'frontend/package.json' in data["files"]
    assert 'backend/app/main.py' in data["files"]


def test_empty_zip(client):
    bio = make_zip({})
    r = client.post('/validate/zip', files={'file': ('empty.zip', bio.getvalue(), 'application/zip')})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert 'empty_zip' in data["issues"]
    assert data["summary"]["total_files"] == 0


def test_corrupted_zip(client):
    r = client.post('/validate/zip', files={'file': ('bad.zip', b'not-a-zip', 'application/zip')})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert 'invalid_zip' in data["issues"]


def test_missing_frontend_backend(client):
    files = {
        'frontend/package.json': '{"name":"app"}',
        # missing backend/app/main.py
    }
    bio = make_zip(files)
    r = client.post('/validate/zip', files={'file': ('proj.zip', bio.getvalue(), 'application/zip')})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert any(i.startswith('missing:') for i in data["issues"])  # missing backend file
    assert data["summary"]["has_frontend"] is True
    assert data["summary"]["has_backend"] is False


def test_response_schema_keys(client):
    files = {
        'frontend/package.json': '{}',
        'backend/app/main.py': 'print(1)',
    }
    bio = make_zip(files)
    r = client.post('/validate/zip', files={'file': ('proj.zip', bio.getvalue(), 'application/zip')})
    assert r.status_code == 200
    data = r.json()
    for k in ["ok", "issues", "files", "summary"]:
        assert k in data
    assert isinstance(data["issues"], list)
    assert isinstance(data["files"], list)
    assert set(["has_frontend", "has_backend", "total_files"]).issubset(set(data["summary"].keys()))
