from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from langchain_core.messages import HumanMessage

from src.agent.middlewares.guard import ScopeResult, _last_human_message_content, scope_guard


def test_last_human_message_content_finds_most_recent():
    messages = [HumanMessage(content="first"), HumanMessage(content="second")]
    assert _last_human_message_content(messages) == "second"


def test_last_human_message_content_empty_when_none():
    assert _last_human_message_content([]) == ""


@patch("src.agent.middlewares.guard.run_structured", new_callable=AsyncMock)
async def test_in_scope_request_passes_through(mock_run_structured):
    mock_run_structured.return_value = ScopeResult(in_scope=True)

    state = {"messages": [HumanMessage(content="What were top customers last month?")]}
    result = await scope_guard.abefore_agent(state, SimpleNamespace())

    assert result is None


@patch("src.agent.middlewares.guard.run_structured", new_callable=AsyncMock)
async def test_out_of_scope_request_is_refused(mock_run_structured):
    mock_run_structured.return_value = ScopeResult(
        in_scope=False, refusal_reason="Requests a customer's raw email."
    )

    state = {"messages": [HumanMessage(content="What's John Smith's email?")]}
    result = await scope_guard.abefore_agent(state, SimpleNamespace())

    assert result["jump_to"] == "end"
    assert "email" in result["messages"][0].content.lower()


@patch("src.agent.middlewares.guard.run_structured", new_callable=AsyncMock)
async def test_classifier_failure_fails_open(mock_run_structured):
    mock_run_structured.side_effect = RuntimeError("rate limited")

    state = {"messages": [HumanMessage(content="What were top customers last month?")]}
    result = await scope_guard.abefore_agent(state, SimpleNamespace())

    assert result is None
