from typing import Any, Dict, List, Tuple

REQUIRED_FRONTEND_FILES = [
    "src/App.jsx",
    # allow either classic CRA-style index.js or Vite-style main.jsx
    "src/index.js",
    "public/index.html",
]

REQUIRED_BACKEND_FILES = [
    "app/main.py",
    "app/routes/__init__.py",
    "app/routes/api.py",
    "app/schemas/__init__.py",
    "app/models/__init__.py",
    "app/services/__init__.py",
]


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_valid_rel_file(path: str) -> bool:
    if not isinstance(path, str) or not path:
        return False
    if path.startswith("/"):
        return False
    if ".." in path.split("/"):
        return False
    if path.endswith("/"):
        return False
    # Require an extension to avoid directory-like entries
    return "." in path.split("/")[-1]


def validate_project_output(output: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not isinstance(output, dict):
        return False, ["Output is not a dict"]

    frontend = output.get("frontend_files")
    backend = output.get("backend_files")
    readme = output.get("README")

    if not isinstance(frontend, dict) or not frontend:
        errors.append("frontend_files must be a non-empty dict")
    if not isinstance(backend, dict) or not backend:
        errors.append("backend_files must be a non-empty dict")
    if not _is_non_empty_string(readme):
        errors.append("README must be a non-empty string")

    if isinstance(frontend, dict):
        for req in REQUIRED_FRONTEND_FILES:
            if req not in frontend or not _is_non_empty_string(frontend.get(req)):
                errors.append(f"Missing required frontend file: {req}")
        for k, v in frontend.items():
            if not _is_valid_rel_file(k):
                errors.append(f"Invalid frontend filename: {k}")
            if not _is_non_empty_string(v):
                errors.append(f"Empty or invalid content for frontend file: {k}")

    if isinstance(backend, dict):
        # All required backend files must be present and non-empty
        for req in REQUIRED_BACKEND_FILES:
            if not _is_non_empty_string(backend.get(req)):
                errors.append(f"Missing required backend file: {req}")
        for k, v in backend.items():
            if not _is_valid_rel_file(k):
                errors.append(f"Invalid backend filename: {k}")
            if not _is_non_empty_string(v):
                errors.append(f"Empty or invalid content for backend file: {k}")

    return len(errors) == 0, errors
