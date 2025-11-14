# Origo Quickstart

This is a minimal guide to run the Origo Micro-SaaS generator locally.

## 1. Backend (generator_backend)

```bash
cd C:\Users\<you>\CascadeProjects\windsurf-project-2
python -m venv venv
./venv/Scripts/Activate.ps1
cd generator_backend
pip install fastapi uvicorn pydantic openai sqlalchemy
uvicorn app.main:app --reload --port 8000
```

Backend runs at:
- http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## 2. Frontend (React)

In a second terminal:

```bash
cd C:\Users\<you>\CascadeProjects\windsurf-project-2\frontend
npm install
npm start
```

Frontend runs at:
- http://localhost:3000

## 3. Use Origo

1. Open http://localhost:3000.
2. Fill in the Micro-SaaS Generator form (idea, target users, features, stack).
3. Click "Generate Project".
4. After generation, click "Download ZIP" to download the generated project.
