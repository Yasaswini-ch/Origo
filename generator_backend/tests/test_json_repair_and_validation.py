import json
import pytest

import app.services.llm_service as llm
from app.services.file_service import save_project
from app.utils.errors import ValidationFailedError


def test_repair_malformed_json_and_normalize():
    # Malformed JSON with code fences, trailing commas, and extra text
    bad = """
    ```json
    {
      "frontend_files": {
        "src/index.js": "console.log('x')",
      },
      "backend_files": {
        "app/main.py": "print('y')",
      },
      "README": "# Title",
    }
    ``` some trailing text
    """
    repaired = llm._repair_json_text(bad)
    data = json.loads(repaired)
    norm = llm._normalize_output_dict(data)

    assert isinstance(norm, dict)
    assert isinstance(norm.get("frontend_files"), dict)
    assert isinstance(norm.get("backend_files"), dict)
    assert isinstance(norm.get("README"), str)


def test_save_project_validation_blocks(tmp_path, monkeypatch):
    # Point storage to a temp dir
    from app import services
    monkeypatch.setattr(services.file_service, "BASE_STORAGE_DIR", tmp_path / "storage", raising=True)

    bad_output = {
        # Missing required minimal files
        "frontend_files": {},
        "backend_files": {},
        "README": "",
    }

    with pytest.raises(ValidationFailedError):
        save_project("pid123", bad_output)
