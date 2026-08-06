from dataclasses import dataclass


@dataclass
class AgentContext:
    """Per-invocation context: who is asking, and which conversation."""

    user_id: str
    thread_id: str
