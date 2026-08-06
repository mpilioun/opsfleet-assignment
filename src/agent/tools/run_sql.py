import logging

from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.tools._bq_runner import get_runner
from src.safety.cost_guard import QueryTooExpensiveError, check_query_cost
from src.safety.sql_guard import SqlGuardError, validate_and_prepare_sql

logger = logging.getLogger(__name__)

MAX_SQL_ATTEMPTS = 3


def _count_recent_run_sql_failures(messages: list) -> int:
    """Consecutive run_sql failures counting back from the latest message, reset
    by a successful run_sql call. Non-run_sql tool calls in between don't reset it.
    """
    count = 0
    for message in reversed(messages):
        if getattr(message, "name", None) != "run_sql":
            continue
        if getattr(message, "status", None) == "error":
            count += 1
            continue
        break
    return count


@tool
async def run_sql(sql: str, runtime: ToolRuntime) -> ToolMessage:
    """Validate and execute a read-only SQL query against BigQuery (orders,
    order_items, products, users only), returning results as a markdown table.
    Never selects PII columns directly - use get_schema to see which columns
    those are.
    """
    tool_call_id = runtime.tool_call_id
    messages = runtime.state.get("messages", []) if runtime.state else []

    if _count_recent_run_sql_failures(messages) >= MAX_SQL_ATTEMPTS:
        logger.warning(
            "run_sql self-repair limit reached (%d attempts)", MAX_SQL_ATTEMPTS
        )
        return ToolMessage(
            content=(
                "SQL self-repair limit reached after repeated failures. Stop retrying SQL "
                "variations - explain to the user what went wrong and what you'd need to proceed."
            ),
            status="error",
            tool_call_id=tool_call_id,
        )

    try:
        prepared_sql = validate_and_prepare_sql(sql)
    except SqlGuardError as exc:
        return ToolMessage(
            content=f"SQL rejected: {exc}", status="error", tool_call_id=tool_call_id
        )

    runner = get_runner()
    try:
        check_query_cost(runner.client, prepared_sql)
    except QueryTooExpensiveError as exc:
        return ToolMessage(content=str(exc), status="error", tool_call_id=tool_call_id)

    try:
        df = runner.execute_query(prepared_sql)
    except Exception as exc:  # noqa: BLE001 - tool boundary: never raise, always return a ToolMessage
        return ToolMessage(
            content=f"BigQuery execution failed: {exc}",
            status="error",
            tool_call_id=tool_call_id,
        )

    if df.empty:
        return ToolMessage(
            content=(
                "Query executed successfully but returned no rows. Consider broadening "
                "filters, checking the date range, or verifying the values you filtered on."
            ),
            status="error",
            tool_call_id=tool_call_id,
        )

    return ToolMessage(content=df.to_markdown(index=False), tool_call_id=tool_call_id)
