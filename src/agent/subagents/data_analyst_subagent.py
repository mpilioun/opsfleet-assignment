from deepagents import SubAgent
from langchain.agents.structured_output import ToolStrategy

from src.agent.middlewares.datetime_prompt import datetime_prompt
from src.agent.tools import DATA_ANALYST_TOOLS
from src.artifacts import ArtifactTypes, read_artifact
from src.clients.llm_client import get_llm_model
from src.models.subagent_results import DataAnalystResult

SKILLS_SOURCE = "/skills/data_analyst_subagent/"


def build_data_analyst_subagent() -> SubAgent:
    prompt = read_artifact(ArtifactTypes.PROMPT, "data_analyst_subagent.md")
    return SubAgent(
        name="data-analyst",
        description=(
            "Answers data questions about orders/order_items/products/users by "
            "querying BigQuery and consulting the golden bucket. Delegate any "
            "question that needs numbers, SQL, or schema info to this subagent."
        ),
        system_prompt=prompt.content,
        tools=DATA_ANALYST_TOOLS,
        model=get_llm_model(
            model=prompt.metadata.get("model", "gemini-flash"),
            effort=prompt.metadata.get("effort"),
        ),
        skills=[SKILLS_SOURCE],
        middleware=[datetime_prompt],
        response_format=ToolStrategy(DataAnalystResult),
    )
