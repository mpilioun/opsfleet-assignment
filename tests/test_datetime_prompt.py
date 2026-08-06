from datetime import UTC, datetime
from types import SimpleNamespace

from langchain_core.messages import SystemMessage

from src.agent.middlewares.datetime_prompt import datetime_prompt, datetime_section


def test_section_states_the_real_current_year():
    section = datetime_section()
    assert str(datetime.now(UTC).year) in section
    assert "CURRENT_DATE()" in section


async def _prompt_for(system_message) -> str:
    captured = {}

    async def handler(request):
        captured["content"] = request.system_message.content
        return "done"

    request = SimpleNamespace(
        system_message=system_message,
        override=lambda **kwargs: SimpleNamespace(**kwargs),
    )
    await datetime_prompt.awrap_model_call(request, handler)
    return captured["content"]


async def test_appends_after_existing_prompt():
    content = await _prompt_for(SystemMessage(content="PERSONA TEXT"))
    assert content.startswith("PERSONA TEXT")
    assert "# Current datetime" in content


async def test_works_with_no_existing_prompt():
    content = await _prompt_for(None)
    assert content.startswith("# Current datetime")
