from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import logging

from ..services.llm_service import run_prompt
from ..services.file_service import save_project
from ..services.fallback_service import build_minimal_fullstack_fallback
from ..utils.errors import ValidationFailedError

router = APIRouter()


class GenerateRequest(BaseModel):
    idea: str
    target_users: str
    features: str
    stack: str


@router.post("/generate")
async def generate_project(payload: GenerateRequest):
    prompt = f"""
Return only valid JSON. No markdown, no code fences, no comments.
If you cannot produce valid JSON, return: {{"error":"json_error"}}.

Generate a project structure based on:
Idea: {payload.idea}
Target Users: {payload.target_users}
Features: {payload.features}
Stack: {payload.stack}

The JSON must follow this shape exactly:

{{
  "frontend_files": {{
    "path/to/file": "file content as a string"
  }},
  "backend_files": {{
    "path/to/file": "file content as a string"
  }},
  "readme": "string"
}}
"""

    try:
        raw_result = await run_prompt(prompt)

        if not isinstance(raw_result, dict):
            logging.error("generate_project: non-dict result from LLM")
            model_output = None
        elif raw_result.get("error") == "json_error":
            logging.warning("generate_project: LLM reported json_error, using fallback")
            model_output = None
        else:
            frontend_files = raw_result.get("frontend_files")
            backend_files = raw_result.get("backend_files")
            readme = raw_result.get("readme") or raw_result.get("README")

            if not isinstance(frontend_files, dict) or not isinstance(backend_files, dict) or not isinstance(readme, str):
                logging.warning("generate_project: invalid types in model output, using fallback")
                model_output = None
            else:
                model_output = {
                    "frontend_files": frontend_files,
                    "backend_files": backend_files,
                    "README": readme,
                }

        if model_output is None:
            project_data = build_minimal_fullstack_fallback()
        else:
            project_data = model_output

        project_id = uuid.uuid4().hex

        try:
            saved = save_project(project_id, project_data)
        except ValidationFailedError as exc:
            logging.error("generate_project: validation failed even after fallback; details=%s", getattr(exc, "details", None))
            raise HTTPException(status_code=502, detail="Generated project did not pass validation.") from exc

        saved["project_id"] = project_id

        return JSONResponse({"status": "success", "project_id": project_id, "project": saved})

    except HTTPException:
        raise  # propagate HTTPException with meaningful message
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.exception("generate_project: unhandled exception")
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")
