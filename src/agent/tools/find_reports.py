from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.utils.agent_config import get_thread_id, get_user_id
from src.agent.utils.reports import list_reports
from src.observability.logging import get_logger

logger = get_logger(__name__)


@tool
async def find_reports(
    runtime: ToolRuntime,
    query: str | None = None,
    this_conversation_only: bool = False,
) -> ToolMessage:
    """Read-only search over the user's saved reports. ALWAYS call this before
    delete_reports to resolve a concrete list of report ids/titles - never call
    delete_reports with a guessed or vague filter.
    """
    logger.info("Agent Called Tool", extra={"tool_name": "find_reports"})
    thread_id = get_thread_id() if this_conversation_only else None
    reports = await list_reports(
        runtime.store, user_id=get_user_id(), thread_id=thread_id, query=query
    )
    logger.info("find_reports matched %d report(s)", len(reports))
    if not reports:
        return ToolMessage(
            content="No matching reports found.", tool_call_id=runtime.tool_call_id
        )

    lines = [f"- [{r['id']}] {r['title']} (saved {r['created_at']})" for r in reports]
    return ToolMessage(content="\n".join(lines), tool_call_id=runtime.tool_call_id)
