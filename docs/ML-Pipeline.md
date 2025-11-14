# Origo ML Pipeline (Prompts A–V)

Project: **Origo — “Where Ideas Become Software.”**

This document describes the multi-prompt ML pipeline that powers Origo. It assumes a real engineering team:

- **Spark — ML Lead**
- **Frontend Lead**
- **Backend Lead**

Even if not all prompts are implemented yet in code, this serves as the canonical design spec.

---

## 1. High-Level Concept

Origo uses a *22-prompt chain* (A–V) to convert a short SaaS idea into a production-ready project description:

1. Normalize and enrich the idea.
2. Design product, UX, and data model.
3. Plan frontend and backend architecture.
4. Generate code file manifests.
5. Generate individual file contents.
6. Validate and repair JSON.
7. Produce fallbacks and final project JSON for packaging.

Only a subset of these prompts is currently wired into the `generator_backend` (notably the full-stack, component, and preview prompts). The rest describe the intended evolution.

---

## 2. Prompt Index (A–V)

> **Note:** Letters map to conceptual stages. Actual prompt files (e.g. `prompt1_fullstack.txt`) may aggregate several steps.

### A. Idea Capture & Normalization
- **Layer:** ML
- **Input:** Raw user text: idea, target users, features, stack.
- **Output:** Normalized JSON:
  - `idea`, `target_users`, `features[]`, `stack.frontend`, `stack.backend`.
- **Purpose:** Remove ambiguity; coerce into a standard schema for downstream prompts.

### B. Market & Persona Expansion
- **Layer:** ML
- **Input:** Normalized idea JSON from A.
- **Output:**
  - `personas`, `use_cases`, `value_props`, `risks`.
- **Purpose:** Clarify who the product serves and why it should exist.

### C. Feature Decomposition
- **Layer:** ML
- **Input:** Idea + features from A/B.
- **Output:**
  - `feature_list[]` with priorities, user stories, acceptance criteria.
- **Purpose:** Turn vague features into implementable slices.

### D. Domain & Data Model Design
- **Layer:** ML
- **Input:** Feature list.
- **Output:**
  - Entities, relationships, example records, constraints.
- **Purpose:** Define DB schema / core domain objects.

### E. System Architecture Draft
- **Layer:** ML
- **Input:** Stack + domain model.
- **Output:**
  - High-level architecture: services, modules, boundaries, external deps.
- **Purpose:** Decide overall technical shape (e.g., React + FastAPI + SQLite).

### F. API Surface & Contracts
- **Layer:** ML
- **Input:** Features + domain model.
- **Output:**
  - List of REST endpoints: method, path, request/response JSON schemas, error modes.
- **Purpose:** Define backend contract used by the frontend and generator.

### G. JSON Healing & Normalization (Repair Prompt)
- **Layer:** ML
- **Input:** Potentially broken JSON from earlier prompts.
- **Output:**
  - Validated, repaired JSON that matches required schemas.
- **Purpose:** Ensure structural correctness (used conceptually alongside our Python-side healers).

### H. Frontend Architecture & Routing
- **Layer:** ML
- **Input:** Features + API contracts.
- **Output:**
  - Frontend routes, pages, components, state management plan.
- **Purpose:** Decide how React app is structured.

### I. UI Components & State Plan
- **Layer:** ML
- **Input:** Frontend architecture.
- **Output:**
  - Component list, props, state responsibilities, interactions.
- **Purpose:** Bridge UX and implementation details.

### J. Styling & Design System
- **Layer:** ML
- **Input:** Brand tone + UX guidelines.
- **Output:**
  - Tailwind utility strategy, color palette suggestions, reusable classes.
- **Purpose:** Keep generated UI consistent and usable.

### K. Backend Module Decomposition
- **Layer:** ML
- **Input:** System architecture + API contracts.
- **Output:**
  - Modules (`routes`, `models`, `services`, `utils`), their responsibilities, dependencies.
- **Purpose:** Organize backend into coherent layers.

### L. Database & Persistence Details
- **Layer:** ML
- **Input:** Domain model + persistence requirements.
- **Output:**
  - Concrete SQLAlchemy models or equivalent, migrations strategy, indexing suggestions.
- **Purpose:** Implement the data model.

### M. Error Handling & Logging
- **Layer:** ML
- **Input:** API contracts and non-functional requirements.
- **Output:**
  - Error taxonomy, standard response structure, logging strategy.
- **Purpose:** Make generated systems debuggable.

### N. Security & Auth Baseline
- **Layer:** ML
- **Input:** Threat model, user roles.
- **Output:**
  - Basic security controls, auth routes, token strategy (conceptual baseline).
- **Purpose:** Introduce minimum security hygiene.

### O. Full-Stack Generation (Current Prompt 1)
- **Layer:** ML → implemented as `prompt1_fullstack.txt`.
- **Input (from backend):**
  - Structured `idea`, `target_users`, `features`, `stack`.
- **Output (JSON):**
  - `frontend_files: {path: content}`
  - `backend_files: {path: content}`
  - `README: string`
- **Purpose:** Produce a minimal but runnable project. This is the **main prompt currently wired into `generator_backend`**.

### P. Component Generator (Current Prompt 2)
- **Layer:** ML → implemented as `prompt2_component.txt`.
- **Input:**
  - `component_name`, `feature_description`, `props`.
- **Output (JSON):**
  - `component_name`, `component_code`.
- **Purpose:** Generate one React component at a time.

### Q. Preview Generator (Current Prompt 3)
- **Layer:** ML → implemented as `prompt3_preview.txt`.
- **Input:**
  - `frontend_files` JSON.
- **Output (JSON):**
  - `html`, `instructions`.
- **Purpose:** Provide a static HTML preview for the generated frontend.

### R. Test Data & Seed Generation
- **Layer:** ML
- **Input:** Domain + features.
- **Output:**
  - Example seed data, fixtures, test users.
- **Purpose:** Make generated projects demo-able.

### S. Documentation Drafting
- **Layer:** ML
- **Input:** Final architecture + API + UX.
- **Output:**
  - README sections, architecture docs, usage examples.
- **Purpose:** Auto-generate docs (conceptually similar to this file but not identical).

### T. JSON Integrity & Drift Detection
- **Layer:** ML + backend logic
- **Input:** Raw ML JSON.
- **Output:**
  - Drift reports (missing keys, extra keys, type mismatches).
- **Purpose:** Detect when models deviate from schema (mirrors Origo’s drift-detector utilities).

### U. Fallback Generator (Stub / Safe Defaults)
- **Layer:** ML + backend logic
- **Input:** Missing/invalid JSON.
- **Output:**
  - Minimal stub project (frontend, backend, README) to keep flow alive.
- **Purpose:** Ensure Origo always returns a usable project.

### V. Final Merger & Normalizer
- **Layer:** ML + backend logic
- **Input:** Partial/cleaned/merged outputs from multiple stages.
- **Output:**
  - Final project JSON matching `{ frontend_files, backend_files, README }`.
- **Purpose:** Produce **one** canonical object consumed by the packaging layer.

---

## 3. Where Prompts Run (Frontend / Backend / ML Layer)

- **ML Layer (LLM):**
  - Actual prompts A–V are issued from the backend to the LLM.
  - Today, only O (full-stack), P (component), Q (preview) are implemented as `.txt` prompt templates.

- **Backend (FastAPI, `generator_backend`):**
  - Owns prompt loading (`app/prompts/*.txt`).
  - Builds input payloads and calls `run_prompt()`.
  - Performs JSON repair / validation / fallback logic.
  - Saves outputs via `file_service` and packages via `zip_service`.

- **Frontend (React):**
  - Does **not** host prompts.
  - Sends user input to backend and displays results.
  - Responsible for UX, not LLM behavior.

---

## 4. Data Flow Diagram (Text)

```text
User
  │
  ├─(1) Enters idea, target_users, features, stack in React UI
  │
  ▼
Frontend (GeneratorPage + GeneratorForm)
  │  POST /generate
  ▼
Backend (FastAPI /generate)
  │  - Load Prompt O template (prompt1_fullstack.txt)
  │  - Build structured prompt string
  ▼
ML Layer (LLM)
  │  - Execute Prompt O
  │  - Return JSON: { frontend_files, backend_files, README }
  ▼
Backend
  │  - Validate & repair JSON (conceptual prompts G, T, U, V)
  │  - Persist to storage/<project_id> (file_service)
  │  - Optionally create ZIP (zip_service)
  ▼
Frontend
  │  - Display JSON + README
  │  - Trigger ZIP download via /projects/{id}/download
  ▼
User downloads project zip and runs code locally
```

Component and preview flows are similar but use Prompts P and Q and do not always persist to disk.

---

## 5. End-to-End: Idea → Project

1. **Idea submission:** User describes the SaaS in the Origo UI.
2. **Backend request:** Frontend calls `/generate` with the raw fields.
3. **Prompt assembly:** Backend reads `prompt1_fullstack.txt` and appends the structured `INPUT` block.
4. **LLM call:** `llm_service.run_prompt()` sends the prompt to the model (or returns a local stub).
5. **ML output:** Model returns JSON with `frontend_files`, `backend_files`, `README`.
6. **Validation & repair:** Backend heals the JSON and ensures schema compatibility.
7. **Persistence:** `file_service.save_project()` writes files under `storage/<project_id>/`.
8. **Packaging:** `zip_service.create_zip()` builds a ZIP for download when requested.
9. **Delivery:** Frontend lets user inspect JSON and download the ZIP.

---

## 6. Team Responsibilities

### Spark — ML Lead
- Owns all prompts A–V.
- Defines schemas for ML inputs/outputs.
- Tunes instructions to maximize JSON correctness.
- Collaborates with Backend Lead on error handling and fallbacks.
- Maintains a library of example conversations, tests, and regression suites.

### Backend Lead
- Owns `generator_backend` (FastAPI app).
- Integrates prompts into routes:
  - `/generate` ↔ Prompt O
  - `/generate/component` ↔ Prompt P
  - `/generate/preview` ↔ Prompt Q
- Implements:
  - `llm_service` for calling models and stubs.
  - `file_service` for saving projects.
  - `zip_service` for ZIP creation.
  - JSON repair, drift detection, and fallback logic.
- Ensures security (CORS, input validation) and performance.

### Frontend Lead
- Owns React app and UX.
- Implements:
  - `GeneratorPage`, `GeneratorForm`, `ProjectViewer`.
  - `useGenerator` hook and `/generate` / `/generate/component` / `/generate/preview` integrations.
- Ensures the UX clearly communicates states:
  - Loading, success, error, stub/fallback usage.
- Builds tooling views to inspect `frontend_files`, `backend_files`, and `README` as pretty JSON.

---

## 7. Evolution Roadmap

- **Short term:**
  - Add implementation for prompts G (JSON healing), U (fallback), V (finalizer) as explicit prompt templates and/or deterministic backend utilities.
  - Expand Prompt O to generate richer project structures.

- **Medium term:**
  - Implement prompts A–F and H–N explicitly, enabling multi-step planning before generation.
  - Add test harness calling each prompt with golden inputs.

- **Long term:**
  - Support multiple model providers.
  - Introduce prompt versioning and A/B testing.
  - Formalize schema contracts via JSON Schema files.
