# ORIGO — The Origin of Every SaaS.

**Origo — The Origin of Every SaaS.**

[![Python Tests](https://github.com/Yasaswini-ch/Origo/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Yasaswini-ch/Origo/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/Yasaswini-ch/Origo/branch/main/graph/badge.svg)](https://codecov.io/gh/Yasaswini-ch/Origo)

Origo is an AI-powered Micro-SaaS generator that transforms high-level product ideas into running software. It takes user input (idea, target users, features, and tech stack) and, via machine learning prompts, generates a complete frontend, backend, and README.

---

## Quickstart

The fastest way to see Origo in action:

1. Open a terminal in the project root and activate the Python venv:
   ```bash
   cd C:\Users\<you>\CascadeProjects\windsurf-project-2
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Start the generator backend on port 8000:
   ```bash
   cd generator_backend
   pip install fastapi uvicorn pydantic openai sqlalchemy
   uvicorn app.main:app --reload --port 8000
   ```
3. In a second terminal, start the frontend on port 3000:
   ```bash
   cd C:\Users\<you>\CascadeProjects\windsurf-project-2\frontend
   npm install
   npm start
   ```
4. Open `http://localhost:3000` and use the Micro-SaaS Generator form to generate a project, then click **Download ZIP** in the viewer.

---

## Screenshots

Place screenshots in a `screenshots/` folder at the project root, for example:

- `screenshots/origo-generator-form.png` — the main Origo generator form (idea, target users, features, stack).
- `screenshots/origo-project-viewer.png` — the ProjectViewer showing generated structure and README.
- `screenshots/origo-api-docs.png` — FastAPI `/docs` page for the generator backend.

When adding screenshots to this README, you can reference them like:

```markdown
![Origo Generator Form](./screenshots/origo-generator-form.png)
![Origo Project Viewer](./screenshots/origo-project-viewer.png)
```

Under the hood, Origo uses:
- Machine Learning (LLM prompts) to synthesize code and documentation
- FastAPI for the backend generator APIs
- React + Tailwind CSS for the frontend and integration UI
- A packaging layer that saves files to disk and prepares ZIP archives

Origo is built by a trio team:
- **Spark — ML Lead**
- **Frontend Lead**
- **Backend Lead**

---

## 1. PROJECT OVERVIEW

Origo is a Micro-SaaS generator platform. A user describes a SaaS (idea, target audience, features, stack), and Origo:

1. Sends this description to an LLM with a structured prompt.
2. Receives a JSON payload containing:
   - `frontend_files`: all React/Tailwind source files
   - `backend_files`: a FastAPI or Node backend
   - `README`: documentation for the generated project
3. Saves these files into a per-project folder.
4. Optionally generates a ZIP archive for download.
5. Exposes a frontend UI so humans can drive and inspect the generation process.

### How ML → Backend → Frontend connect

- **ML layer**: A set of prompts (Prompt 1, 2, 3, etc.) instructs the LLM how to output structured JSON. For example:
  - Prompt 1: full-stack SaaS generator (frontend + backend + README)
  - Prompt 2: single React component generator
  - Prompt 3: HTML preview bundler

- **Generator backend (FastAPI)**:
  - Exposes `/generate`, `/generate/component`, `/generate/preview`, and `/projects/{id}/download`.
  - Uses `llm_service` to call the LLM (or a stub in local mode) with the appropriate prompt.
  - Uses `file_service` to persist generated files under `app/storage/{project_id}`.
  - Uses `zip_service` to package projects into `{project_id}.zip`.

- **Frontend integration (React)**:
  - Provides a **GeneratorPage** UI with a form and result viewer.
  - Calls the backend via `fetch()` using the integration layer in `src/services/api.js`.
  - Displays returned JSON (project metadata, file structure, README) and allows ZIP download.

### What the generator produces

Given a user idea, Origo can output:
- A minimal React/Tailwind frontend (package.json, App.jsx, components, utilities).
- A minimal FastAPI backend with CRUD routes and CORS configured.
- A README describing the generated micro-SaaS.
- A ready-to-download ZIP archive containing the generated project files.

### What problem it solves

Origo dramatically reduces the time from idea to working prototype. Instead of manually scaffolding frontend and backend code, a product person or developer can:
- Enter a short description of their SaaS.
- Immediately obtain a skeleton implementation.
- Download, run, and extend the generated code locally.

---

## 2. INSTALLATION & SETUP (EXTREMELY DETAILED)

This section documents how to set up Origo from scratch on a typical Windows machine using Python and Node.js.

### 2.1 Prerequisites

- **Python 3.11+** installed and available as `python` in your terminal.
- **Node.js + npm** installed.
- Git (optional, for version control).

### 2.2 Clone or open the project

Place the Origo project at:

- `C:\Users\<you>\CascadeProjects\windsurf-project-2`

Project structure (core pieces):

- `frontend/` — React + Tailwind UI, including the Origo generator page.
- `backend/` — Example FastAPI todo/SQLite backend (can be ignored for Origo).
- `generator_backend/` — Origo’s Micro-SaaS generator backend.

### 2.3 Create and activate Python virtual environment

From the project root:

```bash
cd C:\Users\<you>\CascadeProjects\windsurf-project-2
python -m venv venv
# PowerShell activation
.\venv\Scripts\Activate.ps1
```

If `python` is not recognized, ensure Python is properly installed and added to PATH.

### 2.4 Install backend dependencies (generator_backend)

From the project root, with the venv activated:

```bash
cd generator_backend
pip install fastapi uvicorn pydantic openai sqlalchemy
```

Notes:
- `fastapi` and `uvicorn` power the HTTP API.
- `pydantic` models request/response schemas.
- `openai` is optional; when not configured, Origo uses a stub response.
- `sqlalchemy` may be used by other parts of the system or in future extensions.

### 2.5 Run the generator backend (port 8000)

From inside `generator_backend`:

```bash
uvicorn app.main:app --reload --port 8000
```

This will:
- Start FastAPI on `http://127.0.0.1:8000`.
- Watch files in `generator_backend/app` and auto-reload on changes.

You can verify by visiting:
- `http://127.0.0.1:8000/docs` — interactive API docs.

### 2.6 Install frontend dependencies

In a new terminal (still within the same project, venv optional for Node):

```bash
cd C:\Users\<you>\CascadeProjects\windsurf-project-2\frontend
npm install
```

This installs React, ReactDOM, react-scripts, Tailwind-related dev dependencies, and other supporting packages.

### 2.7 Run the frontend (port 3000)

From `frontend/`:

```bash
npm start
```

Create React App will start a dev server, typically at:

- `http://localhost:3000` (or another port if 3000 is busy).

You should see the Origo **Micro-SaaS Generator** page.

### 2.8 Folder structure overview

Simplified tree:

- `frontend/`
  - `package.json`
  - `public/index.html`
  - `src/`
    - `App.jsx` (renders `GeneratorPage`)
    - `index.js`, `index.css`
    - `components/`
      - `GeneratorForm.jsx`
      - `ProjectViewer.jsx`
      - `NavBar.jsx`, `CreateItem.jsx`, `ListItems.jsx` (example/todo UI)
    - `pages/`
      - `GeneratorPage.jsx`
    - `hooks/`
      - `useGenerator.js`
    - `services/`
      - `api.js`
    - `utils/`
      - `api.js` (for todo app)
      - `download.js`

- `generator_backend/`
  - `app/main.py`
  - `app/routes/`
    - `generate.py`
    - `component.py`
    - `preview.py`
    - `download.py`
  - `app/services/`
    - `llm_service.py`
    - `file_service.py`
    - `zip_service.py`
  - `app/models/schemas.py`
  - `app/utils/ids.py`
  - `app/prompts/` (prompt templates)
  - `app/storage/` (generated projects and ZIPs)

- `backend/` (separate todo API, not required for Origo itself)

---

## 3. RUNNING THE PROJECT

### 3.1 Start the generator backend (port 8000)

In one terminal:

```bash
cd generator_backend
uvicorn app.main:app --reload --port 8000
```

Keep this terminal open.

- API base: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

### 3.2 Start the frontend (port 3000)

In another terminal:

```bash
cd frontend
npm start
```

Open:
- `http://localhost:3000`

### 3.3 API base URL and communication

The frontend uses:
- `http://localhost:8000` as the API base.

Defined calls in `src/services/api.js`:
- `POST /generate` — generate a full SaaS project.
- `POST /generate/component` — generate a single React component.
- `POST /generate/preview` — generate an HTML preview artifact.
- `GET /projects/{project_id}/download` — download a ZIP of the generated project.

CORS is enabled in `generator_backend/app/main.py` via `CORSMiddleware`, allowing the frontend on port 3000 to call the backend on port 8000 without browser CORS issues.

---

## 4. ARCHITECTURE

### 4.1 ML pipeline

Conceptual ML pipeline (prompts A → B → C → D → E → F → G → ...):

- **Prompt A (Full-stack generator)**
  - Input: idea, target_users, features, stack.
  - Output: JSON with `frontend_files`, `backend_files`, `README`.

- **Prompt B (Component generator)**
  - Input: component_name, feature_description, props.
  - Output: `component_name`, `component_code`.

- **Prompt C (Preview generator)**
  - Input: `frontend_files` JSON.
  - Output: `html` and `instructions` to preview the frontend in a single HTML file.

- **Prompt D..G (Conceptual extensions)**
  - Could handle: test generation, deployment config, environment files, documentation sections, etc.

Currently, core implemented prompts correspond to Prompt A, B, and C.

### 4.2 Generator backend routes/services

In `generator_backend/app`:

- **Routes**
  - `app/routes/generate.py`
    - `POST /generate` — accepts `GenerateRequest` and returns `GenerateResponse`.
    - `GET /projects/{project_id}/download` — serves ZIP archives (also mirrored in `download.py`).
  - `app/routes/component.py`
    - `POST /generate/component` — generates a single React component.
  - `app/routes/preview.py`
    - `POST /generate/preview` — generates preview HTML and instructions.
  - `app/routes/download.py`
    - `GET /projects/{project_id}/download` — a dedicated download route.

- **Services**
  - `llm_service.py`
    - `run_prompt(prompt)` — calls OpenAI if configured or returns stub JSON if `OPENAI_API_KEY` is missing.
  - `file_service.py`
    - `save_project(project_id, output)` — writes `frontend_files`, `backend_files`, and README into `app/storage/{project_id}`.
  - `zip_service.py`
    - `create_zip(project_id)` — zips up `frontend/`, `backend/`, `README.md` into `app/storage/{project_id}.zip`.

- **Models & utils**
  - `models/schemas.py` — Pydantic models for requests/responses.
  - `utils/ids.py` — generates unique project IDs.

### 4.3 Frontend integration layer (Prompt B)

In `frontend/src`:

- `services/api.js`
  - `generateProject(payload)` → `POST /generate`.
  - `generateComponent(payload)` → `POST /generate/component`.
  - `generatePreview(payload)` → `POST /generate/preview`.
  - `downloadProjectZip(projectId)` → `GET /projects/{projectId}/download`.

- `hooks/useGenerator.js`
  - Manages `loading`, `error`, `output` state.
  - Exposes `generate`, `generateComponent`, `generatePreview` as hook functions.

- `pages/GeneratorPage.jsx`
  - Renders the generator UI.
  - Uses `useGenerator` and passes values to `GeneratorForm` and `ProjectViewer`.

### 4.4 ZIP packaging system (Prompt C)

- Backend uses `zip_service.create_zip(project_id)` to:
  - Traverse `app/storage/{project_id}/frontend`.
  - Traverse `app/storage/{project_id}/backend`.
  - Include `README.md`.
  - Package into `app/storage/{project_id}.zip`.

- The frontend’s `downloadZip` utility triggers a file download for that ZIP.

### 4.5 Preview HTML bundler (Prompt E)

- A conceptual HTML bundler (based on `preview_html` output) can:
  - Load React via CDN.
  - Inline the generated React components and mount them to `#root`.
  - Include Tailwind via CDN for styling.

This is used for quick in-browser previews without a build pipeline.

### 4.6 README generator itself (Prompt F)

- This README is generated/updated automatically based on:
  - `frontend_files` and `backend_files` structure.
  - `previous_readme` content.
  - `latest_action` log entry.

### 4.7 JSON healer (Prompt G)

- The system can apply “self-healing” logic to:
  - Fix malformed JSON from LLM outputs.
  - Fill in missing fields with defaults.
  - Ensure responses conform to schemas expected by the frontend/backend.

---

## 5. FEATURE SUMMARY

From the current `frontend_files` and `backend_files`:

### Frontend components

- `App.jsx`
  - Renders `GeneratorPage` as the main application view.

- `pages/GeneratorPage.jsx`
  - Top-level page for the Micro-SaaS generator UI.

- `components/GeneratorForm.jsx`
  - Collects `idea`, `target_users`, `features`, and `stack` from the user.
  - Calls `onGenerate()` with the payload.

- `components/ProjectViewer.jsx`
  - Displays `project_id`.
  - Shows serialized `frontend_files`, `backend_files`, and README (when available).
  - Offers a “Download ZIP” button.

- `components/NavBar.jsx`, `components/CreateItem.jsx`, `components/ListItems.jsx`
  - Example/todo UI demonstrating React + Tailwind patterns.

### Frontend utilities and hooks

- `hooks/useGenerator.js`
  - Handles API calls and state for generation.

- `services/api.js`
  - Abstracts fetch calls to the generator backend.

- `utils/api.js`
  - Original todo API helper (for the sample app).

- `utils/download.js`
  - Handles browser ZIP downloads.

### Backend routes

Located under `generator_backend/app/routes`:

- `POST /generate` — create new project, return `project_id`, `status`.
- `POST /generate/component` — return component JSON.
- `POST /generate/preview` — return preview HTML + instructions.
- `GET /projects/{project_id}/download` — return project ZIP.

### Backend services

- `llm_service.run_prompt(prompt)`
- `file_service.save_project(project_id, output)`
- `zip_service.create_zip(project_id)`

These provide the core generation, persistence, and packaging workflows.

---

## 6. PROGRESS HISTORY (THIS MUST AUTO-UPDATE)

- 2025-11-14 — Initial Origo Micro-SaaS generator backend and frontend wiring created.
- 2025-11-14 — Added SQLite-backed todo backend and integrated CORS.
- 2025-11-14 — Implemented generator_backend with /generate, /generate/component, /generate/preview routes.
- 2025-11-14 — Created React-based GeneratorPage, GeneratorForm, ProjectViewer, and integration API layer.
- 2025-11-14 — Implemented ZIP packaging and /projects/{project_id}/download endpoint.
- 2025-11-14 — Added stubbed LLM behavior to run without OPENAI_API_KEY and verified end-to-end flow (project generation + ZIP download).

---

## 7. TEAM USAGE NOTES

### Spark — ML Lead

Spark is responsible for:
- Designing and refining the LLM prompts (Prompt A, B, C, etc.).
- Ensuring JSON outputs are consistent and schema-compliant.
- Integrating new ML capabilities (test generation, docs, deployment config).

Spark typically:
- Edits `app/prompts/*.txt`.
- Adjusts `llm_service.run_prompt` behavior.
- Defines new Pydantic schemas for richer outputs.

### Frontend teammate

The Frontend lead focuses on:
- Improving the UX of `GeneratorPage`.
- Adding new views/components to visualize generated code.
- Integrating routing, theming, and state management as Origo grows.

Common tasks:
- Update `GeneratorForm` to support additional fields (e.g. auth, payments, multi-tenant options).
- Enhance `ProjectViewer` to show folder trees, code previews, and diff views.
- Implement additional pages (e.g. history of generated projects).

### Backend teammate

The Backend lead owns:
- Extending the FastAPI routes to support more generation modes.
- Hardening persistence (e.g. SQLite/PostgreSQL-based metadata for projects).
- Securing endpoints, adding auth, rate limiting, and logging.

Common tasks:
- Introduce a persistent project registry instead of only using disk.
- Expand `/generate` to return more metadata.
- Add background tasks for long-running generations.

### How to test Origo with example SaaS ideas

1. Start backend (`uvicorn ...`) and frontend (`npm start`).
2. Open `http://localhost:3000`.
3. Enter:
   - Idea: "tiny CRM for freelancers"
   - Target Users: "freelance designers, developers"
   - Features: "create contacts, track deals, send proposals"
   - Stack: "react+tailwind | fastapi"
4. Click **Generate Project**.
5. Inspect the output in `ProjectViewer` and click **Download ZIP**.
6. Unzip the project ZIP and run the generated app independently if desired.

---

## 8. TROUBLESHOOTING

### Backend fails to start (port 8000)

- Symptom: `ModuleNotFoundError` (e.g., `No module named 'sqlalchemy'`) or immediate shutdown.
- Fix:
  - Ensure venv is active: `.\venv\Scripts\Activate.ps1`.
  - Reinstall deps in `generator_backend`:
    - `pip install fastapi uvicorn pydantic openai sqlalchemy`.
  - Run backend with:
    - `uvicorn app.main:app --reload --port 8000`.

### Frontend shows “Failed to generate project”

- Symptom: Error from `generateProject()` in the browser.
- Likely causes:
  - Backend not running or running on a different port.
  - Backend returning HTTP 500 (e.g. due to missing OpenAI config before stubbing).
- Fix:
  - Confirm `http://127.0.0.1:8000/docs` loads.
  - Check browser DevTools → Network for `/generate` status and response.
  - Ensure `API_BASE` in `src/services/api.js` matches `http://localhost:8000`.

### ZIP download fails

- Symptom: Clicking “Download ZIP” shows an error or does nothing.
- Possible causes:
  - `/projects/{project_id}/download` route missing or not imported.
  - Project folder not saved under `app/storage/{project_id}`.
- Fix:
  - Ensure `create_zip(project_id)` is implemented in `zip_service.py`.
  - Confirm one (and only one) route is defined for `/projects/{project_id}/download`.
  - Check that `save_project()` is writing to `app/storage/{project_id}`.

### Preview fails or looks incorrect

- Symptom: HTML preview doesn’t render React UI as expected.
- Possible causes:
  - ES module imports not correctly inlined in the preview HTML.
  - Missing Tailwind or React CDN script.
- Fix:
  - Ensure `preview_html` contains:
    - React + ReactDOM UMD scripts.
    - Babel standalone script.
    - `type="text/babel"` scripts declaring components.
    - Tailwind CDN script.

### API mismatches

- Symptom: Frontend calls a route that does not exist or expects different JSON.
- Fix:
  - Compare frontend `fetch()` calls and backend route definitions.
  - Align HTTP methods and paths.
  - Update Pydantic schemas or frontend expectations for response shape (e.g. ensure `/generate` returns enough data for `ProjectViewer`).

### JSON overflow and malformed responses

- Symptom: LLM returns invalid JSON or overly large payloads.
- Fix:
  - Add validation and try/except in `llm_service.run_prompt`.
  - Use stub responses locally when OpenAI is not configured.
  - Apply “JSON healer” logic to coerce the response into a valid shape.

---

## 9. APPENDIX

### Future roadmap

- Add persistent project registry with metadata (owner, timestamps, tags).
- Support multiple stacks (e.g. Next.js, Express, Django, Remix).
- Implement live code preview, linting, and test generation.
- Integrate deployment providers (Netlify, Vercel, Render) via additional prompts.

### Example workloads

- SaaS idea: "Micro analytics dashboard for small Shopify stores".
- Origo can generate a starter frontend + backend for metrics, charts, and reporting.

### Closing

**Origo — The Origin of Every SaaS.**

This README is updated automatically to reflect new capabilities, prompts, and integration layers as the platform evolves.
