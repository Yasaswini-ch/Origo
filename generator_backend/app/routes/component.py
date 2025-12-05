from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..models.schemas import ComponentRequest, ComponentResponse
from ..services.llm_service import run_prompt
from ..services.metadata_service import add_frontend_file_to_metadata, read_metadata
from ..services import file_service
from ..services.zip_service import create_zip
import logging

router = APIRouter(tags=['component'])

PROMPTS_DIR = Path(__file__).resolve().parent.parent / 'prompts'
PROMPT_FILE = PROMPTS_DIR / 'prompt2_component.txt'


def build_prompt(data: ComponentRequest, template: str) -> str:
    return (
        f'{template}\n\n'
        f'component_name: {data.component_name}\n'
        f'feature_description: {data.feature_description}\n'
        f'props: {data.props}\n'
    )


@router.post('/generate/component', response_model=ComponentResponse)
async def generate_component(payload: ComponentRequest) -> ComponentResponse:
    try:
        template = PROMPTS_DIR.joinpath('prompt2_component.txt').read_text(encoding='utf-8')
    except FileNotFoundError:
        template = (
            'You are a React component generator. '
            'Always respond with JSON containing component_name and component_code.'
        )

    full_prompt = build_prompt(payload, template)

    try:
        result = await run_prompt(full_prompt)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    component_name = result.get('component_name', 'AutoComponent.jsx')
    component_code = result.get(
        'component_code',
        'import React from \'react\';\n\n'
        'export default function AutoComponent(){\n'
        '  return <div>AutoComponent</div>;\n'
        '}\n',
    )

    return ComponentResponse(component_name=component_name, component_code=component_code)


@router.post('/projects/{project_id}/components')
async def save_component_to_project(project_id: str, payload: ComponentResponse):
    try:
        # Ensure project exists by metadata
        _ = read_metadata(project_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found") from exc

    name = payload.component_name or 'AutoComponent.jsx'
    if not (name.endswith('.jsx') or name.endswith('.js')):
        name = f"{name}.jsx"
    rel_path = f"src/components/{name}"

    # Write component file
    try:
        proj_dir = file_service.BASE_STORAGE_DIR / project_id
        target = proj_dir / 'frontend' / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload.component_code or '', encoding='utf-8')
        logging.info("Saved component %s for %s", rel_path, project_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Update metadata and rebuild zip
    meta = add_frontend_file_to_metadata(project_id, rel_path)
    try:
        create_zip(project_id)
    except Exception:  # pragma: no cover
        pass

    return {"project_id": project_id, "component_path": rel_path, "metadata": meta}
