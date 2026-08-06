from types import SimpleNamespace

from langgraph.store.memory import InMemoryStore

from src.agent.golden_bucket import ensure_seeded
from src.agent.tools.search_golden_bucket import search_golden_bucket


def _fake_runtime(store) -> SimpleNamespace:
    return SimpleNamespace(tool_call_id="call-1", store=store)


async def test_returns_no_match_message_when_bucket_empty():
    store = InMemoryStore()

    result = await search_golden_bucket.coroutine(question="anything", runtime=_fake_runtime(store))

    assert "No similar past analyses" in result.content


async def test_returns_formatted_trio_when_seeded():
    store = InMemoryStore()
    await ensure_seeded(store)

    result = await search_golden_bucket.coroutine(
        question="top 10 customers by total spend", runtime=_fake_runtime(store)
    )

    assert "seed" not in result.content  # internal id shouldn't leak into the formatted text
    assert "SELECT" in result.content
