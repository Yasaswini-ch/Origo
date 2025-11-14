from pathlib import Path
import json

from fastapi import APIRouter, HTTPException

from app.models.schemas import PreviewRequest, PreviewResponse
from app.services.llm_service import run_prompt

router = APIRouter(tags=['preview'])

PROMPTS_DIR = Path(__file__).resolve().parent.parent / 'prompts'
PROMPT_FILE = PROMPTS_DIR / 'prompt3_preview.txt'


def build_prompt(data: PreviewRequest, template: str) -> str:
    frontend_json = json.dumps(data.frontend_files, indent=2)
    return f'{template}\n\nFRONTEND_FILES_JSON:\n{frontend_json}\n'


@router.post('/generate/preview', response_model=PreviewResponse)
async def generate_preview(payload: PreviewRequest) -> PreviewResponse:
    try:
        template = PROMPT_FILE.read_text(encoding='utf-8')
    except FileNotFoundError:
        template = (
            'You are a preview generator. '
            'Always respond with JSON containing html and instructions fields.'
        )

    full_prompt = build_prompt(payload, template)

    try:
        result = await run_prompt(full_prompt)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    html = result.get('html', '<div>No preview available</div>')
    instructions = result.get('instructions', 'No instructions provided.')

    return PreviewResponse(html=html, instructions=instructions)
