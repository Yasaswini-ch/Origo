# Origo Pipeline Overview

Project: **Origo — “Where Ideas Become Software.”**

This document explains how a request flows through Origo:

- From the **user in the browser**
- Through the **React frontend**
- Into the **FastAPI generator backend**
- Through the **LLM prompts**
- Back into the backend for **storage and packaging**
- And finally back to the **user as a downloadable ZIP**

Team roles:
- **Spark — ML Lead**
- **Frontend Lead**
- **Backend Lead**

---

## 1. High-Level Architecture

At a high level, Origo consists of three main layers:

1. **Frontend (React + Tailwind)**
   - Lives under `frontend/`.
   - Provides the Micro-SaaS Generator UI.
   - Talks to the generator backend via HTTP.

2. **Generator Backend (FastAPI)**
   - Lives under `generator_backend/app/`.
   - Exposes these key endpoints:
     - `POST /generate` — full project generation.
     - `POST /generate/component` — single React component generation.
     - `POST /generate/preview` — HTML preview.
     - `GET /projects/{project_id}/download` — ZIP download.
   - Uses `llm_service` to call an LLM or a stub.
   - Uses `file_service` and `zip_service` to persist and package projects.

3. **Storage & Packaging**
   - Under `generator_backend/app/storage/`.
   - Each project gets a directory: `storage/<project_id>/`.
   - ZIPs are created as `storage/<project_id>.zip`.

---

## 2. Detailed Request Flow

### 2.1 User → Frontend

1. The user opens `http://localhost:3000`.
2. The React app (`frontend/src/index.js` + `App.jsx`) renders `GeneratorPage`.
3. On **GeneratorPage**:
   - `GeneratorForm` collects:
     - `idea`
     - `target_users`
     - `features`
     - `stack`
   - On submit, it calls the `generate` function from the `useGenerator` hook.

### 2.2 Frontend → Backend

- The `useGenerator` hook (in `frontend/src/hooks/useGenerator.js`) calls `generateProject` from `frontend/src/services/api.js`:
  - `POST http://localhost:8000/generate`
  - JSON body: `{ idea, target_users, features, stack }`.

- The backend is a FastAPI app defined in `generator_backend/app/main.py`:
  - CORS is configured to allow requests from the frontend.
  - `app.include_router(generate_router)` wires `/generate`.

### 2.3 Backend → LLM

1. `app/routes/generate.py` defines `generate_project`:
   - Reads `prompt1_fullstack.txt` from `app/prompts/`.
   - Builds a composite prompt including the user `INPUT` section.

2. It calls `llm_service.run_prompt(prompt)`:
   - If `OPENAI_API_KEY` is set and the `openai` library is installed:
     - It calls a chat completion model and expects JSON back.
   - Otherwise:
     - It returns a **stub JSON project** so that local development still works.

### 2.4 LLM → Backend

- The LLM (or stub) returns JSON with:
  - `frontend_files`: `{ path: content }`.
  - `backend_files`: `{ path: content }`.
  - `README`: string.

- `generate_project` then:
  - Creates a `project_id` via `utils/ids.py`.
  - Calls `file_service.save_project(project_id, llm_output)` to persist files.
  - Returns a **response model**: `{ "project_id": ..., "status": "success" }`.

### 2.5 Backend → Storage

`file_service.save_project()`:

- Computes `project_dir = storage/<project_id>/`.
- Writes:
  - `frontend_files` into `project_dir/frontend/...`.
  - `backend_files` into `project_dir/backend/...`.
  - `README` into `project_dir/README.md`.

No ZIP is created at this stage; that happens on-demand.

### 2.6 Storage → ZIP

When the frontend requests `GET /projects/{project_id}/download`:

1. `routes/generate.py` or `routes/download.py` calls `zip_service.create_zip(project_id)`.
2. `zip_service`:
   - Verifies that `storage/<project_id>/` exists.
   - Creates `storage/<project_id>.zip`.
   - Recursively zips:
     - `frontend/` subtree.
     - `backend/` subtree.
     - Optional `README.md`.
3. Returns a `FileResponse` streaming the ZIP back to the caller.

### 2.7 Backend → Frontend → User

- The frontend `ProjectViewer` uses `downloadZip(projectId)` from `src/utils/download.js`:
  - Calls the backend download endpoint.
  - Forces a file download in the browser with `project-<id>.zip`.

- The user saves the ZIP locally and can install dependencies and run the generated project.

---

## 3. File & Directory Structure

### 3.1 Frontend (`frontend/`)

Key files:

- **`package.json`** — React + Tailwind setup.
- **`src/index.js`** — entry point; mounts React app.
- **`src/App.jsx`** — top-level component, renders `GeneratorPage`.
- **`src/pages/GeneratorPage.jsx`** — orchestrates form and viewer.
- **`src/components/GeneratorForm.jsx`** — user input form.
- **`src/components/ProjectViewer.jsx`** — displays project output and offers download.
- **`src/hooks/useGenerator.js`** — encapsulates API calls and loading/error state.
- **`src/services/api.js`** — frontend HTTP client for generator backend.
- **`src/utils/download.js`** — helper to trigger ZIP downloads.

### 3.2 Generator Backend (`generator_backend/app/`)

Core modules:

- **`main.py`**
  - Creates FastAPI app.
  - Configures CORS.
  - Includes routers: `generate`, `component`, `preview`.

- **`routes/generate.py`**
  - `POST /generate`: full stack project generation.
  - `GET /projects/{project_id}/download`: ZIP download.

- **`routes/component.py`**
  - `POST /generate/component`: generates a single React component.

- **`routes/preview.py`**
  - `POST /generate/preview`: generates an HTML preview.

- **`routes/download.py`** (optional/dedicated)
  - Alternative implementation of `GET /projects/{project_id}/download`.

- **`models/schemas.py`**
  - Pydantic models for request/response schemas.

- **`services/llm_service.py`**
  - Wrapper to call OpenAI or fallback stub.

- **`services/file_service.py`**
  - Saves `frontend_files`, `backend_files`, `README` to disk.

- **`services/zip_service.py`**
  - Creates ZIP archives for a given `project_id`.

- **`utils/ids.py`**
  - Generates unique `project_id` values.

- **`prompts/*.txt`**
  - Prompt templates used by `llm_service`.

- **`storage/`**
  - Contains one directory per project (`storage/<project_id>/`).
  - Contains ZIP files (`storage/<project_id>.zip`).

---

## 4. How generator_backend Works Internally

### 4.1 Route Lifecycle: `/generate`

1. **Request parsing**
   - FastAPI validates body against `GenerateRequest` model.

2. **Prompt preparation**
   - Reads `prompt1_fullstack.txt`.
   - Concatenates with structured `INPUT` block.

3. **LLM call**
   - Uses `llm_service.run_prompt()`.
   - If `OPENAI_API_KEY` is missing, a deterministic stub is returned.

4. **Project persistence**
   - Allocates `project_id`.
   - Calls `file_service.save_project()`.

5. **Response**
   - Returns `GenerateResponse` with `project_id` and `status`.

### 4.2 Route Lifecycle: `/generate/component`

1. Parses body as `ComponentRequest`.
2. Loads `prompt2_component.txt`.
3. Calls LLM via `llm_service.run_prompt()`.
4. Extracts `component_name` and `component_code` from JSON.
5. Returns `ComponentResponse` to the frontend.

### 4.3 Route Lifecycle: `/generate/preview`

1. Parses body as `PreviewRequest` (contains `frontend_files`).
2. Loads `prompt3_preview.txt`.
3. Calls LLM via `llm_service.run_prompt()`.
4. Extracts `html` and `instructions` from JSON.
5. Returns `PreviewResponse` to the frontend.

### 4.4 Route Lifecycle: `/projects/{project_id}/download`

1. Validates `project_id`.
2. Calls `zip_service.create_zip(project_id)`.
3. Streams the resulting ZIP as `FileResponse`.

---

## 5. Responsibilities by Role

### Spark — ML Lead

- Designs and maintains prompt templates (`app/prompts/*.txt`).
- Defines schemas for all ML outputs.
- Collaborates with Backend Lead on JSON healing and fallbacks.
- Ensures outputs are deterministic enough for automated tests.

### Backend Lead

- Owns `generator_backend` codebase.
- Integrates prompts with FastAPI routes.
- Maintains `llm_service`, `file_service`, `zip_service`.
- Implements and tunes retry, timeout, and error-handling logic.

### Frontend Lead

- Owns `frontend` codebase and UX.
- Ensures request/response shapes match backend contracts.
- Provides tools to visualize ML outputs and ZIP download.

---

## 6. Extension Points

- **Additional routes:** e.g., `/analyze`, `/refine`, `/tests`.
- **Multi-step workflows:** splitting planning (prompts A–F) and generation (O–Q) across multiple API calls.
- **Multiple model providers:** `llm_service` can be adapted to use other APIs.
- **Configurable stacks:** letting users pick between different frontend/backend templates.
