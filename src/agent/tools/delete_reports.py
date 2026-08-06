from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.context import AgentContext
from src.agent.reports import delete_reports_by_ids


@tool
async def delete_reports(
    report_ids: list[str], runtime: ToolRuntime[AgentContext]
) -> ToolMessage:
    """Permanently delete the given saved reports (by id, resolved via find_reports
    first). Destructive and irreversible - the agent's HITL confirmation flow
    intercepts this tool before it runs.
    """
    if not report_ids:
        return ToolMessage(
            content="No report ids provided; nothing deleted.",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    deleted = await delete_reports_by_ids(
        runtime.store, user_id=runtime.context.user_id, report_ids=report_ids
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
