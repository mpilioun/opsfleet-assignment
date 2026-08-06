from langgraph.config import get_config

DEFAULT_USER_ID = "anonymous"


def get_user_id() -> str:
    """Get user ID from the request's `configurable`, defaulting to "anonymous".

    The AG-UI/CopilotKit layer sets `configurable.user_id` on every request
    (see `RetailInsightsAGUIAgent.prepare_stream`).
    """
    configurable = get_config().get("configurable", {})
    user_id = configurable.get("user_id")
    return user_id if isinstance(user_id, str) and user_id else DEFAULT_USER_ID


def get_thread_id() -> str:
    """Get thread ID from the request's `configurable`, defaulting to ""."""
    configurable = get_config().get("configurable", {})
    thread_id = configurable.get("thread_id")
    return thread_id if isinstance(thread_id, str) else ""
