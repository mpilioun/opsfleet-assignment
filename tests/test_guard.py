from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import HumanMessage

from src.agent.middlewares.guard import ScopeResult, _last_human_message_content, scope_guard


def test_last_human_message_content_finds_most_recent():
    messages = [HumanMessage(content="first"), HumanMessage(content="second")]
    assert _last_human_message_content(messages) == "second"


def test_last_human_message_content_empty_when_none():
    assert _last_human_message_content([]) == ""


@patch("src.agent.middlewares.guard.get_llm_model")
async def test_in_scope_request_passes_through(mock_get_llm_model):
    classifier = MagicMock()
    classifier.ainvoke = AsyncMock(return_value=ScopeResult(in_scope=True))
    mock_get_llm_model.return_value.with_structured_output.return_value = classifier

    state = {"messages": [HumanMessage(content="What were top customers last month?")]}
    result = await scope_guard.abefore_agent(state, SimpleNamespace())

    assert result is None


@patch("src.agent.middlewares.guard.get_llm_model")
async def test_out_of_scope_request_is_refused(mock_get_llm_model):
    classifier = MagicMock()
    classifier.ainvoke = AsyncMock(
        return_value=ScopeResult(in_scope=False, refusal_reason="Requests a customer's raw email.")
    )
    mock_get_llm_model.return_value.with_structured_output.return_value = classifier

    state = {"messages": [HumanMessage(content="What's John Smith's email?")]}
    result = await scope_guard.abefore_agent(state, SimpleNamespace())

    assert result["jump_to"] == "end"
    assert "email" in result["messages"][0].content.lower()
