import types
import json
import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_llm_openai(monkeypatch):
    fake_openai = types.SimpleNamespace()
    fake_chat = MagicMock()

    def create_side_effect(*args, **kwargs):
        # inspect prompt/messages to decide which "name" to return
        src = ""
        if "messages" in kwargs and kwargs["messages"] is not None:
            src = str(kwargs["messages"])
        elif "prompt" in kwargs and kwargs["prompt"] is not None:
            src = str(kwargs["prompt"])
        else:
            src = " ".join(map(str, args)) if args else ""

        if "route-mapping" in src or "route mapping" in src or "route_mapping" in src:
            payload = {"name": "route-mapping", "ok": True, "message": "validated"}
        else:
            payload = {"name": "ok", "ok": True, "message": "auto-mock"}

        content_str = json.dumps(payload)

        # Build a response that contains many common shapes
        # 1) classic ChatCompletion-like shape with message.content
        choice_msg = {"message": {"content": content_str, "parts": [content_str]}, "text": content_str}

        return {"choices": [choice_msg], "id": "fake"}

    fake_chat.create.side_effect = create_side_effect
    fake_openai.ChatCompletion = types.SimpleNamespace(create=fake_chat.create)

    # also provide responses.create() style used by new SDKs
    fake_responses = MagicMock()
    def responses_create_side_effect(*args, **kwargs):
        # return object with output -> list -> content -> dict with text
        payload = {"name": "route-mapping", "ok": True, "message": "validated"}
        content = json.dumps(payload)
        return types.SimpleNamespace(output=[types.SimpleNamespace(content=[types.SimpleNamespace(_type="output_text", text=content)])])
    fake_responses.create.side_effect = responses_create_side_effect
    fake_openai.responses = fake_responses

    # also create an OpenAI class with an instance method if code uses OpenAI()
    fake_openai.OpenAI = MagicMock()
    fake_openai.OpenAI.return_value = types.SimpleNamespace(chat=types.SimpleNamespace(create=fake_chat.create), responses=fake_responses)

    try:
        import app.services.llm_service as llm_service
        monkeypatch.setattr(llm_service, "openai", fake_openai, raising=False)
    except Exception:
        monkeypatch.setattr("app.services.llm_service.openai", fake_openai, raising=False)

    return fake_openai

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    import importlib
    app = None
    candidates = ["app.main","app.app","main","generator_backend.app.main","generator_backend.main"]
    for mod in candidates:
        try:
            m = importlib.import_module(mod)
            if hasattr(m,"app"):
                app = getattr(m,"app")
                break
            if getattr(m, "__class__", None) is not None and m.__class__.__name__ == "FastAPI":
                app = m
                break
        except Exception:
            continue
    if app is None:
        try:
            pkg = importlib.import_module("app")
            if hasattr(pkg,"main") and hasattr(pkg.main,"app"):
                app = getattr(pkg.main,"app")
        except Exception:
            pass
    if app is None:
        raise RuntimeError("Could not import the web app. Adjust conftest.py to point at your app object.")
    return TestClient(app)
