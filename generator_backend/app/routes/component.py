from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models.schemas import ComponentRequest, ComponentResponse
from app.services.llm_service import run_prompt

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
