import io
from zipfile import ZipFile
import pytest

import app.services.file_service as file_service
import app.services.preview_service as preview_service
from app.utils.errors import PreviewMissingFieldsError, PreviewInputInvalidError, PreviewTransformFailedError


def _zip_bytes(files):
    buf = io.BytesIO()
    with ZipFile(buf, 'w') as z:
        for path, content in files.items():
            z.writestr(path, content)
    return buf.getvalue()


def test_preview_success_js_css(tmp_path, monkeypatch):
    # Redirect storage
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)

    # Mock esbuild bundling
    def fake_check_output(cmd, stderr=None, text=None):
        # Return small ESM bundle
        return "console.log('ok');"
    monkeypatch.setattr(preview_service.subprocess, "check_output", fake_check_output)

    files = {
        "index.html": """
        <html><head><link href=\"styles.css\"></head>
        <body>
            <img src=\"img/logo.png\">
            <script src=\"main.js\"></script>
        </body></html>
        """,
        "styles.css": "body{color:#333}",
        "main.js": "import './dep.js'; console.log('hi')",
        "dep.js": "export default 1;",
        "img/logo.png": b"PNGDATA",
    }
    # Allow bytes for binary
    buf = io.BytesIO()
    with ZipFile(buf, 'w') as z:
        for p, c in files.items():
            if isinstance(c, bytes):
                z.writestr(p, c)
            else:
                z.writestr(p, c)
    data = buf.getvalue()

    html = preview_service.generate_preview("pid1", data)
    # Saved file exists
    out = (file_service.BASE_STORAGE_DIR / "previews" / "pid1.html")
    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert "console.log('ok');" in txt
    assert "<style>body{color:#333}</style>" in txt
    assert "data:" in txt  # inlined image


def test_missing_index_html_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)
    files = {"main.js": "console.log(1)"}
    data = _zip_bytes(files)
    with pytest.raises(PreviewMissingFieldsError):
        preview_service.generate_preview("pid2", data)


def test_zip_corrupted_error(tmp_path, monkeypatch):
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)
    bad = b"not-a-zip"
    with pytest.raises(PreviewInputInvalidError):
        preview_service.generate_preview("pid3", bad)


def test_esbuild_failure_maps_to_502(tmp_path, monkeypatch):
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)

    def failing_check_output(cmd, stderr=None, text=None):
        raise preview_service.subprocess.CalledProcessError(returncode=1, cmd=cmd, output="boom")
    monkeypatch.setattr(preview_service.subprocess, "check_output", failing_check_output)

    files = {
        "index.html": "<script src=\"main.js\"></script>",
        "main.js": "import 'missing.js'",
    }
    data = _zip_bytes(files)
    with pytest.raises(PreviewTransformFailedError):
        preview_service.generate_preview("pid4", data)


def test_route_upload_preview(client, tmp_path, monkeypatch):
    # Use storage in tmp
    monkeypatch.setattr(file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)
    # Stub esbuild
    monkeypatch.setattr(preview_service.subprocess, "check_output", lambda *a, **k: "console.log('ok')")
    # Ensure project exists
    (file_service.BASE_STORAGE_DIR / "demo").mkdir(parents=True, exist_ok=True)

    # Prepare zip
    files = {
        "index.html": "<script src=\"main.js\"></script>",
        "main.js": "console.log('x')",
    }
    data = _zip_bytes(files)

    # POST multipart
    resp = client.post("/preview/demo", files={"zip": ("project.zip", data, "application/zip")})
    assert resp.status_code == 200
    body = resp.json()
    assert body["project_id"] == "demo"
    assert body["preview_path"] == "previews/demo.html"
    assert isinstance(body["html"], str) and body["html"]
