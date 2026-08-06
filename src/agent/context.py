from pydantic import BaseModel, ConfigDict


class AgentContext(BaseModel):
    """Per-invocation context: who is asking, and which conversation.

    A Pydantic model, not a dataclass: LangGraph builds this via
    `AgentContext(**configurable)`, and the AG-UI/CopilotKit layer injects extra
    keys into `configurable` alongside ours (e.g. `agent_name`) - `extra="ignore"`
    drops those instead of raising. Also lets AG-UI's own schema introspection
    (which expects a Pydantic-style `.schema`) work without falling back.
    """

    model_config = ConfigDict(extra="ignore")

    user_id: str = "anonymous"
    thread_id: str = ""
