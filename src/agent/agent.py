from deepagents import create_deep_agent
from langchain.agents.middleware import InterruptOnConfig

from src.agent.backend import (
    PREFERENCES_FILE,
    SKILLS_READ_ONLY_PERMISSION,
    build_backend,
)
from src.agent.context import AgentContext
from src.agent.middlewares.datetime_prompt import datetime_prompt
from src.agent.middlewares.guard import scope_guard
from src.agent.middlewares.persona_prompt import persona_prompt
from src.agent.middlewares.pii import PII_MIDDLEWARE
from src.agent.subagents.data_analyst_subagent import build_data_analyst_subagent
from src.agent.subagents.report_writer_subagent import build_report_writer_subagent
from src.agent.tools import ROOT_TOOLS
from src.artifacts import ArtifactTypes, read_artifact
from src.clients.llm_client import get_llm_model
from src.database.postgres_manager import postgres_manager


def _delete_reports_description(tool_call, state, runtime) -> str:
    report_ids = tool_call.get("args", {}).get("report_ids", [])
    return (
        f"Delete {len(report_ids)} report(s) ({', '.join(report_ids)})? "
        "This cannot be undone."
    )


INTERRUPT_ON = {
    "delete_reports": InterruptOnConfig(
        allowed_decisions=["approve", "reject"],
        description=_delete_reports_description,
    ),
}


def build_agent():
    persona = read_artifact(ArtifactTypes.PROMPT, "retail_agent_persona.md")
    store = postgres_manager.get_store()

    return create_deep_agent(
        name="retail-insights-agent",
        model=get_llm_model(model=persona.metadata.get("model", "gemini-flash")),
        tools=ROOT_TOOLS,
        subagents=[build_data_analyst_subagent(), build_report_writer_subagent()],
        backend=build_backend(store),
        permissions=[SKILLS_READ_ONLY_PERMISSION],
        memory=[PREFERENCES_FILE],
        middleware=[scope_guard, persona_prompt, datetime_prompt, *PII_MIDDLEWARE],
        interrupt_on=INTERRUPT_ON,
        context_schema=AgentContext,
        checkpointer=postgres_manager.get_checkpointer(),
        store=store,
    )
