from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from src.agent.middlewares.guard import (
    PREVIOUS_TURN_CHARS,
    ScopeResult,
    _classifier_input,
    scope_guard,
)


def test_classifier_input_finds_most_recent_user_message():
    messages = [HumanMessage(content="first"), HumanMessage(content="second")]
    assert _classifier_input(messages) == "second"


def test_classifier_input_empty_when_none():
    assert _classifier_input([]) == ""


def test_classifier_input_includes_the_assistant_turn_being_replied_to():
    messages = [
        HumanMessage(content="what is my last report?"),
        AIMessage(content="Your latest saved report is 'July 2026 Top 5 Products'."),
        HumanMessage(content="open it and summarise"),
    ]

    result = _classifier_input(messages)

    assert "July 2026 Top 5 Products" in result
    assert "open it and summarise" in result


def test_classifier_input_ignores_assistant_turns_after_the_latest_user_message():
    messages = [
        AIMessage(content="stale"),
        HumanMessage(content="latest question"),
        AIMessage(content="not yet replied to"),
    ]

    assert _classifier_input(messages).endswith("latest question")
    assert "not yet replied to" not in _classifier_input(messages)


def test_classifier_input_truncates_a_long_assistant_turn():
    messages = [
        HumanMessage(content="show me the report"),
        AIMessage(content="head" + "x" * 10_000 + "tail"),
        HumanMessage(content="summarise it"),
    ]

    result = _classifier_input(messages)

    assert "head" in result
    assert "tail" not in result
    assert len(result) < PREVIOUS_TURN_CHARS + 500


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
