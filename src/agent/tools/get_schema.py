from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.tools._bq_runner import get_runner
from src.safety.sql_guard import ALLOWED_TABLES, PII_BLOCKED_COLUMNS


@tool
async def get_schema(table_name: str, runtime: ToolRuntime) -> ToolMessage:
    """Get column names/types for one of the available tables (orders, order_items,
    products, users). Use this instead of guessing column names."""
    if table_name not in ALLOWED_TABLES:
        return ToolMessage(
            content=f"Unknown table '{table_name}'. Available tables: {', '.join(sorted(ALLOWED_TABLES))}.",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )
    try:
        fields = get_runner().get_table_schema(table_name)
    except Exception as exc:  # noqa: BLE001 - tool boundary: never raise, always return a ToolMessage
        return ToolMessage(
            content=f"Failed to fetch schema for '{table_name}': {exc}",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    lines = []
    for field in fields:
        marker = (
            " [PII - never select directly]"
            if field["name"] in PII_BLOCKED_COLUMNS
            else ""
        )
        lines.append(f"- {field['name']} ({field['type']}, {field['mode']}){marker}")

    return ToolMessage(content="\n".join(lines), tool_call_id=runtime.tool_call_id)
