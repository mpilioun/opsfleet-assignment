from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.reports import create_report
from src.agent.utils.agent_config import get_thread_id, get_user_id
from src.observability.logging import get_logger

logger = get_logger(__name__)


@tool
async def save_report(title: str, content: str, runtime: ToolRuntime) -> ToolMessage:
    """Save a report (with insights/action items) to the user's Saved Reports
    library, for retrieval or deletion later."""
    logger.info("Agent Called Tool", extra={"tool_name": "save_report"})
    report_id = await create_report(
        runtime.store,
        user_id=get_user_id(),
        thread_id=get_thread_id(),
        title=title,
        content=content,
    )
    return ToolMessage(
        content=f"Report saved with id {report_id}.", tool_call_id=runtime.tool_call_id
    )
