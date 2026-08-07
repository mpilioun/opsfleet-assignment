"""Tool-boundary error backstop (requirement 5). LangGraph's ToolNode only converts
`ToolInvocationError` (bad tool args) into a ToolMessage - any other exception
(Postgres down, the embeddings API rate-limiting a store search, matplotlib failing
to write a PNG) propagates out and kills the whole run. This turns one dependency
being down into an error ToolMessage the model can react to and route around.

One middleware instead of a try/except in every tool: it also covers deepagents'
built-in tools and any tool added later.
"""

from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langgraph.errors import GraphBubbleUp

from src.observability.logging import get_logger

logger = get_logger(__name__)


@wrap_tool_call
async def tool_error_boundary(request, handler):
    try:
        return await handler(request)
    except GraphBubbleUp:
        # Control-flow signals, not failures: a GraphInterrupt raised inside a tool
        # (e.g. a subagent graph invoked via `task` hitting its own HITL confirmation)
        # must reach the runtime, or the interrupt is silently swallowed and the
        # destructive-op confirmation never reaches the user. Same carve-out
        # LangGraph's own ToolNode makes before its error handler.
        raise
    except Exception as exc:
        tool_name = request.tool_call["name"]
        logger.exception("Tool failed", extra={"tool_name": tool_name})
        return ToolMessage(
            content=(
                f"{tool_name} failed: {exc}. This is a temporary failure of an "
                "underlying service, not a bad query - do not retry it repeatedly. "
                "Continue without it if you can, otherwise tell the user which "
                "step is unavailable."
            ),
            status="error",
            name=tool_name,
            tool_call_id=request.tool_call["id"],
        )
