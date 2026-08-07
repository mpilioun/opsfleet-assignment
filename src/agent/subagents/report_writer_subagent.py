from deepagents import SubAgent
from langchain.agents.structured_output import ToolStrategy

from src.agent.middlewares.datetime_prompt import datetime_prompt
from src.agent.middlewares.tool_errors import tool_error_boundary
from src.agent.tools import REPORT_WRITER_TOOLS
from src.artifacts import ArtifactTypes, read_artifact
from src.clients.llm_client import get_llm_model
from src.models.subagent_results import ReportWriterResult

SKILLS_SOURCE = "/skills/report_writer_subagent/"


def build_report_writer_subagent() -> SubAgent:
    prompt = read_artifact(ArtifactTypes.PROMPT, "report_writer_subagent.md")
    return SubAgent(
        name="report-writer",
        description=(
            "Turns the data-analyst's findings into a report with insights and "
            "action items, optionally with a chart. Delegate to this subagent once "
            "you have the numbers and are ready to present them to the user."
        ),
        system_prompt=prompt.content,
        tools=REPORT_WRITER_TOOLS,
        model=get_llm_model(
            model=prompt.metadata.get("model", "gemini-flash"),
            effort=prompt.metadata.get("effort"),
        ),
        skills=[SKILLS_SOURCE],
        middleware=[datetime_prompt, tool_error_boundary],
        response_format=ToolStrategy(ReportWriterResult),
    )
