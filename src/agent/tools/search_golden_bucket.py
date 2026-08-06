from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.agent.utils.golden_bucket import search_similar_trios
from src.observability.logging import get_logger

logger = get_logger(__name__)


@tool
async def search_golden_bucket(question: str, runtime: ToolRuntime) -> ToolMessage:
    """Search the golden bucket for past analyst-approved Question->SQL->Report
    examples similar to this one. Call this before writing SQL from scratch -
    a matching past example shows how analysts have interpreted similar questions.
    """
    logger.info("Agent Called Tool", extra={"tool_name": "search_golden_bucket"})
    trios = await search_similar_trios(runtime.store, question, top_k=3)
    if not trios:
        return ToolMessage(
            content="No similar past analyses found in the golden bucket.",
            tool_call_id=runtime.tool_call_id,
        )

    formatted = "\n\n".join(
        f"### Past example: {trio['question']}\n"
        f"SQL:\n```sql\n{trio['sql']}\n```\n"
        f"Report:\n{trio['report']}"
        for trio in trios
    )
    return ToolMessage(content=formatted, tool_call_id=runtime.tool_call_id)
