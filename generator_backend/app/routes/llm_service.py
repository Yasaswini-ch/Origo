import httpx
import json
import re
import logging

logger = logging.getLogger("uvicorn")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"  # <---- YOUR MODEL


# -------- JSON Extractor -------- #
def extract_json_block(text: str):
    """
    Extracts the first {...} JSON object from the LLM output.
    Removes code fences and ignores surrounding garbage.
    """
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start:end + 1]


# -------- JSON Cleaner -------- #
def _cleanup_json_like(text: str) -> str:
    """Clean JSON-like text to handle minor model mistakes."""

    # Remove comments (// style)
    cleaned_lines = []
    for line in text.splitlines():
        if "//" in line:
            line = line.split("//", 1)[0]
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)

    # Remove trailing commas
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    # Remove control characters
    cleaned = re.sub(r"[\x00-\x1f]", "", cleaned)

    return cleaned


# -------- Main LLM runner -------- #
async def run_prompt(full_prompt: str) -> dict:
    """
    Sends the prompt to Ollama model and ensures only valid JSON is returned.
    Returns a Python dict.
    """
    logger.info(f"Sending prompt to Ollama using model: {MODEL_NAME}")

    # -------------------------
    # Strict JSON-only prompt
    # -------------------------
    safe_prompt = f"""
You are a JSON-only generator. ⚠️ Follow these rules strictly:
1. Return ONLY valid JSON.
2. NO markdown, NO code fences, NO comments, NO explanations.
3. NO extra text outside the JSON.
4. Keys and strings must be quoted properly.
5. No trailing commas.
6. No backticks or control characters.
7. If you cannot produce valid JSON, return exactly: {{"error":"json_error"}}

Now generate the JSON exactly as requested in this prompt:

{full_prompt}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": safe_prompt,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        raw_output = response.json().get("response", "")

    logger.debug(f"RAW MODEL OUTPUT (first 500 chars): {raw_output[:500]}")

    # Model intentionally returned fallback JSON
    if raw_output.strip() == '{"error":"json_error"}':
        return {"error": "json_error", "raw_output": raw_output}

    # Extract JSON block
    json_str = extract_json_block(raw_output)
    if not json_str:
        return {"error": "json_error", "raw_output": raw_output}

    # Clean JSON
    cleaned_json = _cleanup_json_like(json_str)

    # Parse JSON safely
    try:
        data = json.loads(cleaned_json)
        if not isinstance(data, dict):
            return {"error": "json_error", "raw_output": raw_output}
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed: {e}")
        return {"error": "json_error", "raw_output": raw_output}
