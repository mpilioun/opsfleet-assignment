from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.context import AgentContext
from src.agent.reports import create_report


@tool
async def save_report(
    title: str, content: str, runtime: ToolRuntime[AgentContext]
) -> ToolMessage:
    """Save a report (with insights/action items) to the user's Saved Reports
    library, for retrieval or deletion later."""
    report_id = await create_report(
        runtime.store,
        user_id=runtime.context.user_id,
        thread_id=runtime.context.thread_id,
        title=title,
        content=content,
    )
    return ToolMessage(
        content=f"Report saved with id {report_id}.", tool_call_id=runtime.tool_call_id
    )
