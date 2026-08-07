from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.utils.agent_config import get_user_id
from src.agent.utils.reports import get_report
from src.observability.logging import get_logger

logger = get_logger(__name__)


@tool
async def read_report(report_id: str, runtime: ToolRuntime) -> ToolMessage:
    """Open one of the user's saved reports and return its full body, so you can
    summarize it, quote it, or build new analysis on top of it. Resolve the id with
    find_reports first (find_reports returns titles and ids only, not bodies).
    """
    logger.info("Agent Called Tool", extra={"tool_name": "read_report"})
    report = await get_report(runtime.store, user_id=get_user_id(), report_id=report_id)
    if report is None:
        return ToolMessage(
            content=f"No saved report with id {report_id}.",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    return ToolMessage(
        content=(
            f"# {report['title']}\n"
            f"(saved {report['created_at']})\n\n"
            f"{report['content']}"
        ),
        tool_call_id=runtime.tool_call_id,
    )
