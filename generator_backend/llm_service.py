import json
import subprocess
import logging

MODEL = "qwen2:1.5b"

def run_ollama(prompt: str) -> dict:
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt,
            text=True,
            capture_output=True,
            check=True
        )
        output = result.stdout.strip()
        logging.debug("RAW MODEL OUTPUT: %s", output[:500])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ollama error: {e.stderr}") from e

    # Try parse JSON
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        cleaned = _repair_json(output)
        try:
            return json.loads(cleaned)
        except Exception:
            raise RuntimeError(f"Model did not output valid JSON.\nOutput:\n{output}")

def _repair_json(text: str) -> str:
    # Remove comments (# ...)
    lines = []
    for line in text.split("\n"):
        if "#" in line:
            line = line.split("#")[0]
        lines.append(line)
    text = "\n".join(lines)

    # Replace single quotes → double quotes
    text = text.replace("'", '"')

    # Remove HTML comments
    text = text.replace("<!--", "")
    text = text.replace("-->", "")

    return text.strip()

def run_prompt(idea, target_users, features, stack):
    prompt = f"""
You MUST respond with STRICT JSON ONLY.
No comments, no text outside JSON, no explanations.

Return this exact structure:

{{
  "frontend_files": {{
    "src/index.js": "string content",
    "src/App.jsx": "string content",
    "public/index.html": "string content"
  }},
  "backend_files": {{
    "app/main.py": "string content",
    "app/routes/api.py": "string content",
    "app/models/__init__.py": "string content",
    "app/schemas/__init__.py": "string content",
    "app/services/__init__.py": "string content"
  }},
  "readme": "string"
}}

All values must be JSON strings with \\n escaped.

Project idea: {idea}
Target users: {target_users}
Features: {features}
Stack: {stack}
"""
    return run_ollama(prompt)

