from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.schemas import GenerateRequest, GenerateResponse
from app.services.llm_service import run_prompt
from app.services.file_service import save_project
from app.services.zip_service import create_zip
from app.utils.ids import generate_project_id

router = APIRouter(tags=['generate'])

PROMPTS_DIR = Path(__file__).resolve().parent.parent / 'prompts'
PROMPT_FILE = PROMPTS_DIR / 'prompt1_fullstack.txt'


def build_prompt(data: GenerateRequest, template: str) -> str:
    return (
        f'{template}\n\n'
        f'INPUT:\n'
        f'idea: {data.idea}\n'
        f'target_users: {data.target_users}\n'
        f'features: {data.features}\n'
        f'stack: {data.stack}\n'
    )


@router.post('/generate', response_model=GenerateResponse)
async def generate_project(payload: GenerateRequest) -> GenerateResponse:
    try:
        template = PROMPT_FILE.read_text(encoding='utf-8')
    except FileNotFoundError:
        template = (
            'You are a Micro-SaaS full-stack generator. '
            'Return JSON with frontend_files, backend_files, and README fields.'
        )

    full_prompt = build_prompt(payload, template)

    try:
        llm_output = await run_prompt(full_prompt)
    except Exception as exc:  # pragma: no cover - propagated as HTTP error
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    project_id = generate_project_id()
    save_project(project_id, llm_output)

    return GenerateResponse(project_id=project_id, status='success')


@router.get('/projects/{project_id}/download')
async def download_project(project_id: str) -> FileResponse:
    """Return a ZIP archive containing the generated project files."""

    try:
        zip_path = create_zip(project_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail='Project not found')

    return FileResponse(
        path=zip_path,
        media_type='application/zip',
        filename=f'{project_id}.zip',
    )
