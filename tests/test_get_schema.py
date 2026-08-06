from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.agent.tools.get_schema import get_schema


def _runtime() -> SimpleNamespace:
    return SimpleNamespace(tool_call_id="call-1")


def _field(name: str, description: str = "") -> dict:
    return {
        "name": name,
        "type": "STRING",
        "mode": "NULLABLE",
        "description": description,
    }


async def test_rejects_unknown_table():
    result = await get_schema.coroutine(table_name="secrets", runtime=_runtime())
    assert result.status == "error"
    assert "Unknown table" in result.content


@patch("src.agent.tools.get_schema.get_runner")
async def test_single_table_lists_columns_and_marks_pii(mock_get_runner):
    mock_get_runner.return_value.get_table_schema.return_value = [
        _field("id"),
        _field("email"),
        _field("state", description="US state"),
    ]

    result = await get_schema.coroutine(table_name="users", runtime=_runtime())

    assert "## users" in result.content
    assert "email (STRING, NULLABLE) [PII - never select directly]" in result.content
    assert "state (STRING, NULLABLE) - US state" in result.content
    # A single-table call stays focused: no dataset header, no relationship block.
    assert "Relationships:" not in result.content


@patch("src.agent.tools.get_schema.get_runner")
async def test_no_argument_returns_full_overview(mock_get_runner):
    mock_get_runner.return_value.get_table_schema.return_value = [_field("id")]

    result = await get_schema.coroutine(runtime=_runtime())

    for table in ("orders", "order_items", "products", "users"):
        assert f"## {table}" in result.content
    assert "Relationships:" in result.content
    assert "order_items.order_id -> orders.order_id" in result.content
    assert result.status != "error"


@patch("src.agent.tools.get_schema.get_runner")
async def test_failed_single_table_lookup_is_an_error(mock_get_runner):
    mock_get_runner.return_value.get_table_schema.side_effect = RuntimeError("boom")

    result = await get_schema.coroutine(table_name="orders", runtime=_runtime())

    assert result.status == "error"
    assert "boom" in result.content


@patch("src.agent.tools.get_schema.get_runner")
async def test_one_unreadable_table_does_not_sink_the_overview(mock_get_runner):
    def _schema(table_name: str):
        if table_name == "products":
            raise RuntimeError("boom")
        return [_field("id")]

    mock_get_runner.return_value.get_table_schema = MagicMock(side_effect=_schema)

    result = await get_schema.coroutine(runtime=_runtime())

    assert "(schema unavailable: boom)" in result.content
    assert "## users" in result.content
