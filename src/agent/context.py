from dataclasses import dataclass


@dataclass(init=False)
class AgentContext:
    """Per-invocation context: who is asking, and which conversation.

    Kept a real dataclass (Pydantic/LangGraph introspect `__dataclass_fields__`
    to build a JSON schema for this, e.g. for AG-UI's schema-keys endpoint) but
    with a hand-written __init__: LangGraph builds this via
    `AgentContext(**configurable)`, and the AG-UI/CopilotKit layer injects extra
    keys into `configurable` alongside ours (e.g. `agent_name`) - a dataclass's
    generated __init__ would reject those with a TypeError. Accept and ignore
    anything beyond user_id/thread_id.
    """

    user_id: str = "anonymous"
    thread_id: str = ""

    def __init__(
        self, *, user_id: str = "anonymous", thread_id: str = "", **_extra: object
    ) -> None:
        self.user_id = user_id
        self.thread_id = thread_id
