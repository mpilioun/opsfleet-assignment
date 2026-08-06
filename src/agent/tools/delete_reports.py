from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.reports import delete_reports_by_ids
from src.agent.utils.agent_config import get_user_id
from src.observability.logging import get_logger

logger = get_logger(__name__)


@tool
async def delete_reports(report_ids: list[str], runtime: ToolRuntime) -> ToolMessage:
    """Permanently delete the given saved reports (by id, resolved via find_reports
    first). Destructive and irreversible - the agent's HITL confirmation flow
    intercepts this tool before it runs.
    """
    logger.info("Agent Called Tool", extra={"tool_name": "delete_reports"})
    if not report_ids:
        return ToolMessage(
            content="No report ids provided; nothing deleted.",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    deleted = await delete_reports_by_ids(
        runtime.store, user_id=get_user_id(), report_ids=report_ids
    )
    if not deleted:
        return ToolMessage(
            content="None of the given report ids were found.",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )
    return ToolMessage(
        content=f"Deleted {len(deleted)} report(s): {', '.join(deleted)}.",
        tool_call_id=runtime.tool_call_id,
    )
