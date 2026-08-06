"""Grounds every model call in the real current date. The LLM has no clock, so
without this it guesses a year from training data and filters `created_at` to a
window where `thelook_ecommerce` has no rows - "up-to-date revenue" then comes
back empty or silently wrong. Applied to the root agent and both subagents.
"""

from datetime import UTC, datetime

from langchain.agents.middleware import dynamic_prompt
from langchain.agents.middleware.types import ModelRequest


def datetime_section() -> str:
    """Current-datetime block appended to a system prompt."""
    now = datetime.now(UTC)
    return (
        "# Current datetime\n"
        f"Current datetime: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC)\n"
        f"Current date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Current year: {now.year}\n"
        f"Current month: {now.strftime('%B')} ({now.month})\n\n"
        "Resolve relative time windows ('last month', 'this quarter', 'year to "
        "date', 'up-to-date') against this date. In SQL, prefer "
        "CURRENT_DATE()/DATE_SUB/DATE_TRUNC over hardcoded years."
    )


@dynamic_prompt
async def datetime_prompt(request: ModelRequest) -> str:
    """Append the datetime section after whatever is already in the system message
    (the persona `system_prompt`, skills index, memory) - additive, never replaces it.
    """
    existing = request.system_message.content if request.system_message else ""
    if not existing:
        return datetime_section()
    return f"{existing}\n\n{datetime_section()}"
