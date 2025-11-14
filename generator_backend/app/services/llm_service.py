import asyncio
import json
import os
from typing import Any, Dict

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None  # type: ignore


async def run_prompt(prompt: str) -> Dict[str, Any]:
    """Execute a text prompt against the OpenAI API and return parsed JSON.

    If OpenAI is not configured (no library or no OPENAI_API_KEY), fall back to a
    small, deterministic stub response so the app can run locally without keys.
    """

    api_key = os.getenv('OPENAI_API_KEY')

    # Fallback: no OpenAI available → return a stub project/component/preview.
    if openai is None or not api_key:
        # Try to infer which prompt is being used based on keywords.
        lower = prompt.lower()
        if 'frontend_files' in lower and 'backend_files' in lower:
            # Full project generation stub
            return {
                'project_id': 'stub-project',
                'status': 'success',
                'frontend_files': {
                    'src/index.js': "console.log('stub frontend');",
                },
                'backend_files': {
                    'app/main.py': "print('stub backend')",
                },
                'README': '# Stub Project\nGenerated without OpenAI; replace with real generation when configured.',
            }
        if 'component_name' in lower:
            # Component generation stub
            return {
                'component_name': 'AutoComponent.jsx',
                'component_code': (
                    "import React from 'react';\n\n"
                    "export default function AutoComponent(){\n"
                    "  return <div>AutoComponent (stub)</div>;\n"
                    "}\n"
                ),
            }
        if 'frontend_files_json' in lower:
            # Preview stub
            return {
                'html': '<div>Preview stub (no OpenAI configured)</div>',
                'instructions': 'Configure OPENAI_API_KEY to get real previews.',
            }

        # Generic fallback
        return {'raw': 'Stub response (no OpenAI configured).'}

    # Real OpenAI call path
    openai.api_key = api_key

    loop = asyncio.get_running_loop()

    def _call() -> str:
        completion = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.2,
        )
        message = completion.choices[0].message
        if isinstance(message, dict):
            return message.get('content', '')
        return getattr(message, 'content', '')

    text = await loop.run_in_executor(None, _call)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {'raw': text}
