# Origo Prompt Test Suite (A–V)

Project: **Origo — “Where Ideas Become Software.”**

This document describes how to manually and programmatically test each prompt in the Origo ML pipeline (A–V). It is owned by **Spark — ML Lead**, with close collaboration from Backend and Frontend leads.

---

## 1. General Testing Principles

- **All prompts must return valid JSON** (unless explicitly designed to output plain text).
- **Schema-first:** each prompt has a contract. Tests assert structure before semantics.
- **Deterministic examples:** use fixed inputs with clear expected patterns.
- **Drift detection:** tests should catch when the model starts adding explanations or changing formats.
- **Automation-ready:** while you can run tests manually in the playground, design them so they can be automated.

For each prompt A–V we define:

- Purpose
- Example input
- Expected output shape
- Pass/fail criteria
- Debugging notes

---

## 2. Prompt A — Idea Capture & Normalization

- **Purpose:** Coerce raw idea text into a normalized JSON schema.
- **Example Input (user → model):**
  ```text
  Build a tiny CRM for solo freelancers to track leads and invoices. Use React + Tailwind + FastAPI.
  ```
- **Expected Model Output (shape):**
  ```json
  {
    "idea": "tiny CRM for solo freelancers",
    "target_users": "solo freelancers",
    "features": ["lead tracking", "invoices"],
    "stack": {
      "frontend": "react+tailwind",
      "backend": "fastapi"
    }
  }
  ```
- **Pass Criteria:**
  - Valid JSON only.
  - All four keys present: `idea`, `target_users`, `features`, `stack`.
  - `features` is an array.
- **Fail Patterns:**
  - Raw English paragraphs.
  - Markdown headings.
  - Missing `stack` or non-JSON formats.
- **Debugging Notes:**
  - Emphasize: “Respond with JSON only, no explanation.”
  - Add examples in the system prompt.

---

## 3. Prompt B — Market & Persona Expansion

- **Purpose:** Generate personas, use cases, and value props.
- **Example Input:** normalized JSON from Prompt A.
- **Expected Output (shape):**
  ```json
  {
    "personas": [ ... ],
    "use_cases": [ ... ],
    "value_props": [ ... ],
    "risks": [ ... ]
  }
  ```
- **Pass:** All four arrays exist, each with at least 1 entry.
- **Fail:** Missing keys, prose outside JSON.
- **Debugging:** Add explicit keys and minimal but clear definitions.

---

## 4. Prompt C — Feature Decomposition

- **Purpose:** Turn features into prioritized, testable items.
- **Input:** Features list from A/B.
- **Expected Shape:**
  ```json
  {
    "feature_list": [
      {
        "id": "F1",
        "title": "",
        "priority": "must-have",
        "user_story": "As a ...",
        "acceptance_criteria": ["..."]
      }
    ]
  }
  ```
- **Pass:** `feature_list` is non-empty array of objects with all keys.
- **Fail:** Freeform bullets, missing `acceptance_criteria`.

---

## 5. Prompt D — Domain & Data Model Design

- **Purpose:** Define entities and relationships.
- **Input:** Feature list.
- **Expected Shape:**
  ```json
  {
    "entities": [
      {
        "name": "Lead",
        "fields": [
          {"name": "id", "type": "string"},
          {"name": "email", "type": "string"}
        ]
      }
    ],
    "relationships": [
      {"from": "Lead", "to": "Invoice", "type": "one-to-many"}
    ]
  }
  ```
- **Pass:** At least one entity; each entity has `fields`.
- **Fail:** SQL DDL with no JSON.

---

## 6. Prompt E — System Architecture Draft

- **Purpose:** Propose service/module layout.
- **Input:** Domain + stack.
- **Expected Shape:**
  ```json
  {
    "services": [ ... ],
    "modules": [ ... ],
    "external_dependencies": [ ... ]
  }
  ```
- **Pass:** All arrays present.

---

## 7. Prompt F — API Surface & Contracts

- **Purpose:** Define REST endpoints.
- **Expected Shape:**
  ```json
  {
    "endpoints": [
      {
        "method": "GET",
        "path": "/leads",
        "request": {"query": {}},
        "response": {"200": {"type": "array", "items": "Lead"}}
      }
    ]
  }
  ```
- **Pass:** `endpoints` array; each element has `method`, `path`, `request`, `response`.

---

## 8. Prompt G — JSON Healing & Normalization

- **Purpose:** Repair malformed JSON from earlier prompts.
- **Input:** Arbitrary malformed JSON-as-text.
- **Expected Output:** Valid JSON that conforms to a supplied schema.
- **Pass:**
  - Output parses as JSON.
  - Keys match the provided schema.
- **Fail:** Explanations like “Here is the fixed JSON: ...”.
- **Debugging:** Reinforce: “Output only the repaired JSON object, no extra text.”

---

## 9. Prompt H — Frontend Architecture & Routing

- **Purpose:** Plan React routing and layout.
- **Expected Shape:**
  ```json
  {
    "routes": [
      {"path": "/", "component": "HomePage"}
    ],
    "layout": {
      "shell": "AppLayout",
      "navigation": ["Sidebar", "TopBar"]
    }
  }
  ```

---

## 10. Prompt I — UI Components & State Plan

- **Purpose:** List components and their props/state.
- **Expected Shape:**
  ```json
  {
    "components": [
      {
        "name": "LeadTable",
        "props": ["leads"],
        "state": ["selectedLeadId"]
      }
    ]
  }
  ```

---

## 11. Prompt J — Styling & Design System

- **Purpose:** Tailwind utility guidance.
- **Expected Shape:**
  ```json
  {
    "colors": {"primary": "blue-600"},
    "components": {"button": "px-3 py-1 rounded bg-primary text-white"}
  }
  ```

---

## 12. Prompt K — Backend Module Decomposition

- **Purpose:** Map routes/models/services/utils.
- **Expected Shape:**
  ```json
  {
    "modules": [
      {"name": "routes.leads", "responsibility": "CRUD for leads"}
    ]
  }
  ```

---

## 13. Prompt L — Database & Persistence Details

- **Purpose:** SQLAlchemy or equivalent models.
- **Expected Shape:**
  ```json
  {
    "models": [
      {
        "name": "Lead",
        "fields": [
          {"name": "id", "type": "Integer", "primary_key": true}
        ]
      }
    ]
  }
  ```

---

## 14. Prompt M — Error Handling & Logging

- **Purpose:** Define error taxonomy.
- **Expected Shape:**
  ```json
  {
    "errors": [ ... ],
    "logging": {"level": "INFO", "sinks": ["stdout"]}
  }
  ```

---

## 15. Prompt N — Security & Auth Baseline

- **Purpose:** Auth & authorization.
- **Expected Shape:**
  ```json
  {
    "auth": {"strategy": "token"},
    "roles": [ ... ],
    "permissions": [ ... ]
  }
  ```

---

## 16. Prompt O — Full-Stack Generation (Implemented)

- **Purpose:** Generate full project: frontend, backend, README.
- **Backend Integration:** `prompt1_fullstack.txt` → `/generate`.
- **Example Input (in prompt):**
  ```text
  You are a backend LLM that generates full micro-SaaS projects.
  Always respond with JSON containing frontend_files, backend_files, and README fields.
  Use the INPUT section provided after this prompt.

  INPUT:
  idea: tiny CRM for solo freelancers
  target_users: solo freelancers
  features: leads, invoices
  stack: react+tailwind | fastapi
  ```
- **Expected Output (shape):**
  ```json
  {
    "frontend_files": {
      "package.json": "...",
      "src/App.jsx": "..."
    },
    "backend_files": {
      "app/main.py": "..."
    },
    "README": "# Tiny CRM..."
  }
  ```
- **Pass Criteria:**
  - Exactly three top-level keys.
  - Both `frontend_files` and `backend_files` are objects.
  - `README` is a string.
- **Fail Patterns:**
  - Additional keys like `notes`, `explanation`.
  - Markdown outside JSON.
- **Debugging Notes:**
  - Add explicit negative examples to the prompt.

---

## 17. Prompt P — Component Generator (Implemented)

- **Purpose:** Generate a single React component.
- **Backend Integration:** `prompt2_component.txt` → `/generate/component`.
- **Example Input Block:**
  ```text
  component_name: LeadTable
  feature_description: Show a table of leads with name, email, and status.
  props: leads (array)
  ```
- **Expected JSON:**
  ```json
  {
    "component_name": "LeadTable.jsx",
    "component_code": "import React from 'react'; ..."
  }
  ```
- **Pass:** Both keys present, `component_code` is non-empty string.
- **Fail:** Returns JSX only or wraps JSON in markdown fences.

---

## 18. Prompt Q — Preview Generator (Implemented)

- **Purpose:** Create a static HTML preview.
- **Backend Integration:** `prompt3_preview.txt` → `/generate/preview`.
- **Example Input Block:**
  ```text
  FRONTEND_FILES_JSON:
  {"src/App.jsx": "export default function App(){ return <div>Hi</div> }"}
  ```
- **Expected JSON:**
  ```json
  {
    "html": "<html>...",
    "instructions": "Open in a browser..."
  }
  ```

---

## 19. Prompt R — Test Data & Seed Generation

- **Purpose:** Produce demo data.
- **Expected Shape:**
  ```json
  {
    "seed_data": {
      "leads": [ ... ],
      "invoices": [ ... ]
    }
  }
  ```

---

## 20. Prompt S — Documentation Drafting

- **Purpose:** Draft READMEs and docs.
- **Expected Shape:**
  ```json
  {
    "readme": "# ...",
    "changelog": "..."
  }
  ```

---

## 21. Prompt T — JSON Integrity & Drift Detection

- **Purpose:** Report schema drift.
- **Expected Shape:**
  ```json
  {
    "missing_keys": [],
    "extra_keys": [],
    "type_mismatches": [],
    "drift_patterns": [],
    "severity": "low"
  }
  ```

---

## 22. Prompt U — Fallback Generator

- **Purpose:** Produce a safe stub project when upstream output is unusable.
- **Expected JSON:**
  ```json
  {
    "frontend_files": {"src/App.jsx": "export default function App(){ return <div>stub</div> }"},
    "backend_files": {"app/main.py": "from fastapi import FastAPI ..."},
    "README": "# Stub Project..."
  }
  ```

---

## 23. Prompt V — Final Merger & Normalizer

- **Purpose:** Take partial/cleaned outputs and return the final project object.
- **Expected JSON:**
  ```json
  {
    "frontend_files": { ... },
    "backend_files": { ... },
    "README": "..."
  }
  ```

---

## 24. Pass/Fail Summary Table

| Prompt | Main Goal                           | Must Return JSON? | Core Keys / Shape                           |
|--------|-------------------------------------|-------------------|----------------------------------------------|
| A      | Normalize idea                      | Yes               | idea, target_users, features, stack          |
| B      | Personas & market                   | Yes               | personas, use_cases, value_props, risks      |
| C      | Feature list                        | Yes               | feature_list[]                               |
| D      | Domain model                        | Yes               | entities[], relationships[]                  |
| E      | Architecture                        | Yes               | services[], modules[], external_dependencies |
| F      | API contracts                       | Yes               | endpoints[]                                  |
| G      | JSON healing                        | Yes               | schema-dependent                             |
| H      | Frontend architecture               | Yes               | routes[], layout                             |
| I      | Components & state                  | Yes               | components[]                                 |
| J      | Styling                             | Yes               | colors, components                           |
| K      | Backend modules                     | Yes               | modules[]                                    |
| L      | DB models                           | Yes               | models[]                                     |
| M      | Errors & logging                    | Yes               | errors[], logging                            |
| N      | Security & auth                     | Yes               | auth, roles[], permissions[]                 |
| O      | Full-stack project (implemented)    | Yes               | frontend_files, backend_files, README        |
| P      | Component code (implemented)        | Yes               | component_name, component_code               |
| Q      | Preview HTML (implemented)          | Yes               | html, instructions                           |
| R      | Seed data                           | Yes               | seed_data                                    |
| S      | Docs                                | Yes               | readme, changelog                            |
| T      | Drift report                        | Yes               | missing_keys, extra_keys, ...                |
| U      | Fallback project                    | Yes               | frontend_files, backend_files, README        |
| V      | Final merger                        | Yes               | frontend_files, backend_files, README        |

---

## 25. Debugging Checklist (For Spark — ML Lead)

When a prompt test fails:

1. **Identify drift pattern:**
   - Did the model add explanations?
   - Did it switch to Markdown?
   - Did it change key names?
2. **Tighten instructions:**
   - Add “Respond with JSON only.”
   - Provide positive and negative examples.
3. **Shorten context:**
   - Remove irrelevant examples; keep the core schema close to the end.
4. **Version prompts:**
   - Keep old versions for comparison.
5. **Coordinate with Backend Lead:**
   - Update JSON repair logic and tests in parallel.
