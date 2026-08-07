"""CopilotKit/AG-UI integration for the retail insights agent - same pattern as
Revmark_AI's `agent/api/ag_ui_agent_wrapper.py`, trimmed to what this agent needs
(no multi-tenant business_id/auth-header plumbing - user_id/thread_id come straight
from the frontend's configurable, matching this prototype's single-org scope).
"""

from copilotkit import LangGraphAGUIAgent
from copilotkit.langgraph import copilotkit_customize_config

from src.agent.agent import build_agent
from src.config.env_config import env_config
from src.observability.langfuse import get_langfuse_callback

AGENT_NAME = "retail-insights-agent"
AGENT_PATH = f"/{AGENT_NAME}"
AGENT_DESCRIPTION = (
    "A data-analysis agent for retail Store/Regional Managers: ask about sales, "
    "inventory, and customer behavior, discuss the results, and manage saved reports."
)

_langfuse_callback = get_langfuse_callback()
_base_config = {
    "agent_name": AGENT_NAME,
    "callbacks": [_langfuse_callback] if _langfuse_callback is not None else [],
    "recursion_limit": env_config.RECURSION_LIMIT,
}


class RetailInsightsAGUIAgent(LangGraphAGUIAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "user_id" not in self.constant_schema_keys:
            self.constant_schema_keys = [*self.constant_schema_keys, "user_id"]

    async def prepare_stream(self, input, agent_state, config):
        """Inject user_id/thread_id into configurable and attach Langfuse metadata."""
        forwarded_props = getattr(input, "forwarded_props", None) or {}
        runtime_configurable = (
            forwarded_props.get("config", {}).get("configurable", {}) or {}
        )

        configurable = {**(config.get("configurable") or {}), **runtime_configurable}
        configurable.setdefault("user_id", "anonymous")
        config["configurable"] = configurable

        thread_id = configurable.get("thread_id")
        user_id = configurable.get("user_id")
        config["metadata"] = {
            **(config.get("metadata", {})),
            "langfuse_session_id": thread_id,
            "langfuse_user_id": str(user_id) if user_id is not None else None,
            "service_name": AGENT_NAME,
            "langfuse_tags": [AGENT_NAME],
            "agent_name": config.get("agent_name"),
        }
        return await super().prepare_stream(input, agent_state, config)


def build_ag_ui_agent() -> RetailInsightsAGUIAgent:
    return RetailInsightsAGUIAgent(
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
        graph=build_agent(),
        config=copilotkit_customize_config(_base_config, emit_tool_calls=True),
    )
