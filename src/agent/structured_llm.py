from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from src.clients.llm_client import get_llm_model


async def run_structured(
    *,
    system_prompt: str,
    user_content: str,
    response_format: type[BaseModel],
    model: str = "gemini-flash",
    effort: str | None = "low",
) -> BaseModel:
    """One-shot structured output via a forced tool call (ToolStrategy), not
    with_structured_output()'s default strict-JSON-mode streaming - the latter is
    what broke (empty/malformed JSON parse errors) on a flaky free-tier fallback
    model. Tool-calling is far more broadly supported across providers, and this
    is the same mechanism already used for the subagents' terminal output.
    """
    agent = create_agent(
        model=get_llm_model(model=model, effort=effort),
        system_prompt=system_prompt,
        response_format=ToolStrategy(response_format),
    )
    result = await agent.ainvoke({"messages": [HumanMessage(content=user_content)]})
    return result["structured_response"]
