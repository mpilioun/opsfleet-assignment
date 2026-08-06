from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel

from src.agent.structured_llm import run_structured


class _FakeResult(BaseModel):
    ok: bool


@patch("src.agent.structured_llm.create_agent")
@patch("src.agent.structured_llm.get_llm_model")
async def test_run_structured_returns_structured_response(mock_get_llm_model, mock_create_agent):
    agent = MagicMock()
    agent.ainvoke = AsyncMock(return_value={"structured_response": _FakeResult(ok=True)})
    mock_create_agent.return_value = agent

    result = await run_structured(
        system_prompt="classify", user_content="hello", response_format=_FakeResult
    )

    assert result == _FakeResult(ok=True)
    mock_create_agent.assert_called_once()
