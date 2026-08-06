from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.context import AgentContext
from src.agent.reports import list_reports


@tool
async def find_reports(
    runtime: ToolRuntime[AgentContext],
    query: str | None = None,
    this_conversation_only: bool = False,
) -> ToolMessage:
    """Read-only search over the user's saved reports. ALWAYS call this before
    delete_reports to resolve a concrete list of report ids/titles - never call
    delete_reports with a guessed or vague filter.
    """
    thread_id = runtime.context.thread_id if this_conversation_only else None
    reports = await list_reports(
        runtime.store, user_id=runtime.context.user_id, thread_id=thread_id, query=query
    )
    if not reports:
        return ToolMessage(
            content="No matching reports found.", tool_call_id=runtime.tool_call_id
        )

    lines = [f"- [{r['id']}] {r['title']} (saved {r['created_at']})" for r in reports]
    return ToolMessage(content="\n".join(lines), tool_call_id=runtime.tool_call_id)
