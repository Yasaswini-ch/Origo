# Origo Debugging Guide

Project: **Origo — “Where Ideas Become Software.”**

This guide helps the engineering team (Spark — ML Lead, Frontend Lead, Backend Lead) debug common issues in Origo’s generator stack.

---

## 1. Debugging Empty ZIP Files

### Symptoms

- User clicks **Download ZIP**, but:
  - The download fails with a 404.
  - The ZIP exists but is empty or missing expected files.

### Checklist

1. **Confirm `project_id` exists**
   - Check browser devtools → Network tab → request to `/projects/{id}/download`.
   - Verify `id` matches the `project_id` returned by `/generate`.

2. **Inspect storage directory**
   - On disk: `generator_backend/app/storage/<project_id>/`.
   - Expected contents:
     - `frontend/` directory with files.
     - `backend/` directory with files.
     - Optional `README.md`.
   - If the directory is missing:
     - The ML output may have been invalid or `file_service.save_project()` was not called.

3. **Check ZIP creation logic**
   - File: `generator_backend/app/services/zip_service.py`.
   - `create_zip(project_id)` should:
     - Raise `FileNotFoundError` if the project folder is missing.
     - Add `frontend`, `backend`, and `README.md` to the archive.
   - Add logging around:
     - Project directory path.
     - Number of files added.

4. **Validate ML output before saving**
   - Ensure `frontend_files` / `backend_files` are non-empty objects.
   - If they are empty, consider calling the **fallback generator** (Prompt U logic) to produce minimal stub files.

5. **Reproduce with stub mode**
   - Unset `OPENAI_API_KEY` to force stub responses.
   - Run `/generate` and inspect storage + ZIP.
   - If stub works but real model doesn’t, the issue is the ML output structure.

---

## 2. Fixing Broken JSON from the Model

### Symptoms

- `llm_service.run_prompt()` returns text that:
  - Is not valid JSON.
  - Contains markdown fences (```json ... ```).
  - Contains commentary around the JSON.

### Strategies

1. **Use Prompt G (JSON Healing) conceptually**
   - Wrap the raw text and ask an LLM: “Repair this into valid JSON matching schema X.”
   - In practice, we also implement deterministic Python-side healers.

2. **Tighten prompt instructions**
   - In templates (e.g., `prompt1_fullstack.txt`):
     - Add: “Respond with JSON only, no explanation, no markdown.”
     - Show 1–2 minimal examples of the expected object.

3. **Backend-side validators**
   - After `run_prompt()`, attempt `json.loads(text)`.
   - On failure:
     - Attempt simple string cleanups (strip fences, trim prose).
     - If still invalid, trigger **fallback (Prompt U logic)**.

4. **Log the raw output**
   - Log the raw model output to a secure location (never user-facing) for debugging.
   - Do not store API keys or sensitive user data.

---

## 3. Using Prompt G (Healing) and U/V (Fallbacks & Finalizer)

> **Note:** These prompts correspond to conceptual behaviors. Parts are already implemented as Python utilities.

### Prompt G — JSON Healing

- **When to use:**
  - Raw LLM output fails to parse as JSON.
  - Keys are incorrect or missing.
- **How to apply:**
  - Pass raw text and the expected schema.
  - Ask the model to output only the fixed JSON.
  - Alternatively, use deterministic backend repair functions.

### Prompt U — Fallback Generator

- **When to use:**
  - Even after healing, output is unusable.
  - Required keys `frontend_files`, `backend_files`, `README` are missing or empty.
- **Behavior:**
  - Returns minimal stub project:
    - `src/App.jsx` with a simple React component.
    - `app/main.py` with a simple FastAPI app.
    - Stub README.

### Prompt V — Final Merger & Normalizer

- **When to use:**
  - You have multiple partial outputs (raw, healed, fallback) and must produce a single final object.
- **Behavior:**
  - Picks primary over secondary values.
  - Ensures final schema:
    - `frontend_files: {}`
    - `backend_files: {}`
    - `README: string`

---

## 4. Common Backend Errors & Fixes

### 4.1 FastAPI Server Won’t Start

- **Symptom:** `uvicorn app.main:app --reload` crashes.
- **Checklist:**
  - Python not found → install Python and ensure it’s on PATH.
  - Missing dependencies → run `pip install fastapi uvicorn pydantic openai`.
  - Import errors (e.g., `ModuleNotFoundError: app.routes.generate`) →
    - Confirm `__init__.py` files exist in packages.
    - Confirm `PYTHONPATH` is correct (or run from `generator_backend/`).

### 4.2 500 Errors on `/generate`

- **Symptom:** Frontend shows “Failed to generate project”.
- **Checklist:**
  - Inspect backend logs for stack trace.
  - Common causes:
    - LLM API errors (rate limit, invalid key).
    - JSON decoding failures in `llm_service.run_prompt()`.
    - Exceptions during `file_service.save_project()`.
  - Quick mitigation:
    - Use stub mode by unsetting `OPENAI_API_KEY`.

### 4.3 404 on `/projects/{id}/download`

- **Cause:**
  - `zip_service.create_zip()` raised `FileNotFoundError`.
  - `id` does not correspond to any folder under `storage/`.
- **Fix:**
  - Ensure you create the project in the same server session.
  - Confirm that `/generate` succeeded and returned the same `project_id`.

---

## 5. Common Frontend Integration Issues

### 5.1 CORS Problems

- **Symptom:** Browser console shows CORS errors when calling `http://localhost:8000`.
- **Fix:**
  - Ensure `CORSMiddleware` in `app/main.py` allows `http://localhost:3000` (currently `'*'` for development).
  - Use correct backend base URL in `frontend/src/services/api.js`.

### 5.2 Shape Mismatch Between Frontend and Backend

- **Symptoms:**
  - `ProjectViewer` shows `(none)` for `frontend_files`.
  - Errors like `Cannot read properties of undefined`.
- **Checklist:**
  - Verify `/generate` response body shape.
  - If backend returns only `{ project_id, status }`, ensure the frontend knows to fetch details or show stub.
  - Keep the field names (`frontend_files`, `backend_files`, `README`) consistent.

### 5.3 Download Button Does Nothing

- **Checklist:**
  - Confirm `project_id` is present in the response and passed to `downloadZip`.
  - Check Network tab for `/projects/{id}/download` request.
  - Confirm backend server is running on `localhost:8000`.

---

## 6. If the LLM Gives No Output

### Symptoms

- Timeout or error from `run_prompt()`.
- Empty string or `null` content.

### Steps

1. **Backend timeouts and retries**
   - Implement reasonable timeouts in `llm_service`.
   - Retry once on transient errors.

2. **Fallback to stub mode**
   - If `openai` is unavailable or `OPENAI_API_KEY` is missing, the service already returns a stub project.
   - For provider-specific failures, add logic:
     - On error, call fallback generator (Prompt U behavior) instead of failing the request.

3. **Frontend messaging**
   - Show a clear error message and indicate whether a stub was used.

---

## 7. If `project_id` Is Missing

### Symptoms

- `/generate` returns a body without `project_id`.
- Frontend cannot download ZIP.

### Diagnosis

- Check `GenerateResponse` model in `models/schemas.py`.
- Confirm `generate_project()` returns an instance of that model.
- Ensure `project_id = generate_project_id()` is called before saving.

### Fixes

1. **Backend:**
   - Always return a `project_id` even when using a fallback.
2. **Frontend:**
   - Handle the case where `project_id` is absent by:
     - Showing a clear error.
     - Disabling the **Download ZIP** button.

---

## 8. Role-Based Debugging Responsibilities

### Spark — ML Lead

- Oversees prompt quality and JSON correctness.
- Investigates drift in model behavior.
- Updates `app/prompts/*.txt` and internal test suites.

### Backend Lead

- Monitors backend logs and uptime.
- Maintains robustness in `llm_service`, `file_service`, `zip_service`.
- Owns fallback and finalization logic.

### Frontend Lead

- Monitors frontend console and network errors.
- Ensures error states are clearly communicated to users.
- Coordinates schema changes with backend.

---

## 9. Quick Debugging Recipes

- **ZIP is empty:**
  - Check `storage/<project_id>/` content → fix ML output or `file_service`.
- **JSON parse error:**
  - Log raw model output → tighten prompt or enable healing logic.
- **Download fails with 404:**
  - Confirm `project_id` and project folder exist.
- **UI shows nothing:**
  - Check React state in `useGenerator` and inspect `output` object.
