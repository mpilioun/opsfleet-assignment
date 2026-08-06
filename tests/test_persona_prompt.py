from types import SimpleNamespace
from unittest.mock import MagicMock

from langchain.agents.middleware.types import ModelRequest
from langchain_core.messages import SystemMessage
from langgraph.store.memory import InMemoryStore

from src.agent.utils import persona
from src.agent.middlewares.persona_prompt import persona_prompt


def _fake_request(store, system_message=None) -> ModelRequest:
    return ModelRequest(
        model=MagicMock(),
        messages=[],
        system_message=system_message,
        runtime=SimpleNamespace(store=store),
    )


async def test_persona_prepended_when_other_content_exists():
    persona._cache.update({"text": None, "expires_at": 0.0})
    store = InMemoryStore()
    await persona.set_active_persona(store, "LIVE PERSONA")
    request = _fake_request(store, system_message=SystemMessage(content="skills index here"))

    async def handler(req):
        return req

    result = await persona_prompt.awrap_model_call(request, handler)

    assert "LIVE PERSONA" in result.system_message.content
    assert "skills index here" in result.system_message.content


async def test_persona_alone_when_no_other_content():
    persona._cache.update({"text": None, "expires_at": 0.0})
    store = InMemoryStore()
    await persona.set_active_persona(store, "LIVE PERSONA")
    request = _fake_request(store, system_message=None)

    async def handler(req):
        return req

    result = await persona_prompt.awrap_model_call(request, handler)

    assert result.system_message.content == "LIVE PERSONA"
