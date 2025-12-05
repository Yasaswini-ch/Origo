from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import io
import logging
import re
import base64
import mimetypes
import shutil
import subprocess
import tempfile
from zipfile import ZipFile, BadZipFile

import app.services.file_service as file_service
from app.utils.errors import (
    PreviewInputInvalidError,
    PreviewMissingFieldsError,
    PreviewNotFoundError,
    PreviewTransformFailedError,
    PreviewUnexpectedError,
    OrigoError,
)

logger = logging.getLogger(__name__)

SCRIPT_SRC_RE = re.compile(r"<script[^>]+src=\"([^\"]+)\"[^>]*></script>", re.IGNORECASE)
LINK_HREF_RE = re.compile(r"<link[^>]+href=\"([^\"]+)\"[^>]*>", re.IGNORECASE)
IMG_SRC_RE = re.compile(r"<img[^>]+src=\"([^\"]+)\"[^>]*>", re.IGNORECASE)


def _read_zip_to_temp(zip_bytes: bytes) -> Path:
    logger.info("preview.extract.zip")
    try:
        tmpdir = Path(tempfile.mkdtemp(prefix="preview_"))
        with ZipFile(io.BytesIO(zip_bytes)) as z:
            z.extractall(tmpdir)
        return tmpdir
    except BadZipFile as exc:
        logger.error("preview error during zip extract", extra={"error": str(exc), "phase": "preview"})
        raise PreviewInputInvalidError(message="zip-error")
    except Exception as exc:
        logger.error("preview unexpected error during zip extract", extra={"error": str(exc), "phase": "preview"})
        raise PreviewInputInvalidError(message="zip-error")


def _ensure_entry(tmpdir: Path) -> Path:
    # Look for index.html anywhere at root
    index_path = tmpdir / "index.html"
    if not index_path.exists():
        # also try common frontend folders
        for cand in [tmpdir / "public" / "index.html", tmpdir / "dist" / "index.html", tmpdir / "frontend" / "index.html"]:
            if cand.exists():
                index_path = cand
                break
    if not index_path.exists():
        logger.error("preview missing index.html", extra={"error": "missing-index", "phase": "preview"})
        raise PreviewMissingFieldsError(message="index.html required")
    return index_path


def _read_file_text(base: Path, href: str) -> Tuple[str, Path]:
    p = (base.parent / href).resolve()
    # Ensure p is within tmpdir for safety
    if not str(p).startswith(str(base.parent.resolve())):
        raise PreviewInputInvalidError(message="path-traversal")
    if not p.exists():
        raise PreviewInputInvalidError(message="missing-asset")
    return p.read_text(encoding="utf-8"), p


def _read_file_bytes(base: Path, href: str) -> Tuple[bytes, Path]:
    p = (base.parent / href).resolve()
    if not str(p).startswith(str(base.parent.resolve())):
        raise PreviewInputInvalidError(message="path-traversal")
    if not p.exists():
        raise PreviewInputInvalidError(message="missing-asset")
    return p.read_bytes(), p


def _inline_asset(html: str, base: Path) -> str:
    def repl_img(m):
        href = m.group(1)
        try:
            data, p = _read_file_bytes(base, href)
            mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            b64 = base64.b64encode(data).decode("ascii")
            return m.group(0).replace(href, f"data:{mime};base64,{b64}")
        except OrigoError:
            return m.group(0)
        except Exception:
            return m.group(0)

    return IMG_SRC_RE.sub(repl_img, html)


def _run_esbuild(entry_path: Path) -> str:
    logger.info("preview.esbuild.start", extra={"entry": str(entry_path)})
    # Use npx esbuild if available; bundle to stdout
    cmd = ["npx", "esbuild", str(entry_path), "--bundle", "--minify", "--format=esm"]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        logger.info("preview.esbuild.bundle.ok")
        return out
    except subprocess.CalledProcessError as exc:
        logger.error("preview esbuild failed", extra={"error": exc.output, "phase": "preview"})
        raise PreviewTransformFailedError(message="transform-failed", details={"log": exc.output})
    except FileNotFoundError as exc:
        logger.error("preview esbuild not found", extra={"error": str(exc), "phase": "preview"})
        raise PreviewTransformFailedError(message="transform-failed", details={"log": "esbuild-not-found"})


def _rewrite_with_bundles(index_html_path: Path) -> str:
    html = index_html_path.read_text(encoding="utf-8")

    # Bundle JS
    scripts: List[Tuple[str, str]] = []  # (original src, bundled code)
    for m in list(SCRIPT_SRC_RE.finditer(html)):
        src = m.group(1)
        try:
            _, p = _read_file_text(index_html_path, src)
            bundled = _run_esbuild(p)
            scripts.append((src, bundled))
        except OrigoError:
            raise
        except Exception as exc:
            logger.error("preview bundle unexpected", extra={"error": str(exc), "phase": "preview"})
            raise PreviewTransformFailedError(message="transform-failed")

    for src, bundled in scripts:
        html = html.replace(f'src="{src}"', "")
        # replace closing script tag for that reference with inline bundle
        html = html.replace("</script>", f"{bundled}</script>", 1)

    # Inline CSS links
    for m in list(LINK_HREF_RE.finditer(html)):
        href = m.group(1)
        try:
            content, _ = _read_file_text(index_html_path, href)
            style_tag = f"<style>{content}</style>"
            html = html.replace(m.group(0), style_tag)
        except OrigoError:
            continue
        except Exception:
            continue

    # Inline assets (img src)
    html = _inline_asset(html, index_html_path)

    # Add iframe-safe CSP meta
    csp = (
        "default-src 'self'; "
        "script-src 'unsafe-inline' 'self'; "
        "style-src 'unsafe-inline' 'self'; "
        "img-src data: 'self'; "
        "connect-src 'none'; object-src 'none'"
    )
    if "<head" in html:
        html = html.replace("<head", f"<head\n<meta http-equiv=\"Content-Security-Policy\" content=\"{csp}\">", 1)
    else:
        html = f"<head><meta http-equiv=\"Content-Security-Policy\" content=\"{csp}\"></head>" + html

    return html


def generate_preview(project_id: str, zip_bytes: bytes) -> str:
    logger.info("preview.start", extra={"project_id": project_id})
    if not project_id or not isinstance(zip_bytes, (bytes, bytearray)):
        logger.error("preview invalid input", extra={"error": "invalid-input", "phase": "preview"})
        raise PreviewInputInvalidError(details={"project_id": project_id})

    # Allow ad-hoc previews without requiring an existing saved project directory

    tmpdir: Path | None = None
    try:
        tmpdir = _read_zip_to_temp(zip_bytes)
        index_path = _ensure_entry(tmpdir)
        html = _rewrite_with_bundles(index_path)

        # Save to storage
        previews_dir = file_service.BASE_STORAGE_DIR / "previews"
        previews_dir.mkdir(parents=True, exist_ok=True)
        out_path = previews_dir / f"{project_id}.html"
        out_path.write_text(html, encoding="utf-8")
        logger.info("preview.write.storage.ok", extra={"path": str(out_path)})
        logger.info("preview.complete", extra={"project_id": project_id})
        return html
    except OrigoError:
        raise
    except Exception as exc:
        logger.error("preview unexpected", extra={"error": str(exc), "phase": "preview"})
        raise PreviewUnexpectedError(details={"project_id": project_id})
    finally:
        if tmpdir and tmpdir.exists():
            try:
                shutil.rmtree(tmpdir)
            except Exception:
                pass
