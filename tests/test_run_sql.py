from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
from langchain_core.messages import ToolMessage

from src.agent.tools.run_sql import _count_recent_run_sql_failures, run_sql
from src.safety.cost_guard import QueryTooExpensiveError


def _fake_runtime(messages=None) -> SimpleNamespace:
    return SimpleNamespace(tool_call_id="call-1", state={"messages": messages or []})


def test_no_recent_failures_on_empty_history():
    assert _count_recent_run_sql_failures([]) == 0


def test_counts_consecutive_run_sql_failures():
    messages = [
        ToolMessage(content="x", name="run_sql", status="error", tool_call_id="1"),
        ToolMessage(content="x", name="get_schema", status="error", tool_call_id="2"),
        ToolMessage(content="x", name="run_sql", status="error", tool_call_id="3"),
    ]
    assert _count_recent_run_sql_failures(messages) == 2


def test_successful_run_sql_resets_the_count():
    messages = [
        ToolMessage(content="x", name="run_sql", status="error", tool_call_id="1"),
        ToolMessage(content="x", name="run_sql", tool_call_id="2"),
        ToolMessage(content="x", name="run_sql", status="error", tool_call_id="3"),
    ]
    assert _count_recent_run_sql_failures(messages) == 1


async def test_run_sql_rejects_unsafe_sql():
    result = await run_sql.coroutine(sql="DELETE FROM orders", runtime=_fake_runtime())
    assert result.status == "error"
    assert "rejected" in result.content.lower()


async def test_run_sql_stops_after_max_attempts():
    history = [
        ToolMessage(content="x", name="run_sql", status="error", tool_call_id=str(i))
        for i in range(3)
    ]
    result = await run_sql.coroutine(sql="SELECT 1", runtime=_fake_runtime(history))
    assert result.status == "error"
    assert "self-repair limit" in result.content.lower()


@patch("src.agent.tools.run_sql.get_runner")
async def test_run_sql_reports_empty_results(mock_get_runner):
    mock_runner = MagicMock()
    mock_runner.client.query.return_value = MagicMock(total_bytes_processed=100)
    mock_runner.execute_query.return_value = pd.DataFrame()
    mock_get_runner.return_value = mock_runner

    result = await run_sql.coroutine(sql="SELECT * FROM products", runtime=_fake_runtime())

    assert result.status == "error"
    assert "no rows" in result.content.lower()


@patch("src.agent.tools.run_sql.get_runner")
async def test_run_sql_returns_markdown_table_on_success(mock_get_runner):
    mock_runner = MagicMock()
    mock_runner.client.query.return_value = MagicMock(total_bytes_processed=100)
    mock_runner.execute_query.return_value = pd.DataFrame({"id": [1, 2]})
    mock_get_runner.return_value = mock_runner

    result = await run_sql.coroutine(sql="SELECT id FROM products", runtime=_fake_runtime())

    assert result.status == "success"
    assert "1" in result.content and "2" in result.content


@patch("src.agent.tools.run_sql.check_query_cost")
@patch("src.agent.tools.run_sql.get_runner")
async def test_run_sql_rejects_over_cost_cap(mock_get_runner, mock_check_cost):
    mock_get_runner.return_value = MagicMock()
    mock_check_cost.side_effect = QueryTooExpensiveError("too expensive")

    result = await run_sql.coroutine(sql="SELECT id FROM products", runtime=_fake_runtime())

    assert result.status == "error"
    assert "too expensive" in result.content.lower()
