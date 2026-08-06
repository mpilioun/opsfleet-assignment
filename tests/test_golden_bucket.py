import hashlib
import math

import pytest
from langgraph.store.memory import InMemoryStore

from src.agent.utils.golden_bucket import (
    CANDIDATE_NAMESPACE,
    GOLDEN_NAMESPACE,
    SEED_TRIOS,
    add_candidate_trio,
    ensure_seeded,
    promote_to_golden,
    search_similar_trios,
)

FAKE_EMBED_DIMS = 32


def _fake_embed(texts: list[str]) -> list[list[float]]:
    """Deterministic bag-of-words hash embedding - offline stand-in for Gemini in tests."""
    vectors = []
    for text in texts:
        vec = [0.0] * FAKE_EMBED_DIMS
        for token in text.lower().split():
            idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % FAKE_EMBED_DIMS
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        vectors.append([v / norm for v in vec])
    return vectors


@pytest.fixture
def store():
    return InMemoryStore(index={"embed": _fake_embed, "dims": FAKE_EMBED_DIMS, "fields": ["question"]})


async def test_ensure_seeded_populates_golden_namespace(store):
    await ensure_seeded(store)
    items = await store.asearch(GOLDEN_NAMESPACE, limit=100)
    assert len(items) == len(SEED_TRIOS)


async def test_ensure_seeded_is_idempotent(store):
    await ensure_seeded(store)
    await store.aput(GOLDEN_NAMESPACE, "extra", {"question": "extra", "sql": "", "report": ""})
    await ensure_seeded(store)
    items = await store.asearch(GOLDEN_NAMESPACE, limit=100)
    assert len(items) == len(SEED_TRIOS) + 1


async def test_search_finds_relevant_seed_trio(store):
    await ensure_seeded(store)
    results = await search_similar_trios(store, "top 10 customers total spend", top_k=1)
    assert results
    assert results[0]["id"] == "seed-top-customers"


async def test_search_returns_nothing_for_unrelated_question(store):
    await ensure_seeded(store)
    results = await search_similar_trios(store, "zzqx flarn woobly plonk gibberish", top_k=3)
    assert results == []


async def test_golden_trios_rank_above_candidate_trios_on_tie(store):
    await store.aput(
        CANDIDATE_NAMESPACE,
        "cand-1",
        {"id": "cand-1", "question": "monthly revenue trend", "sql": "", "report": ""},
    )
    await store.aput(
        GOLDEN_NAMESPACE,
        "gold-1",
        {"id": "gold-1", "question": "monthly revenue trend", "sql": "", "report": ""},
    )
    results = await search_similar_trios(store, "monthly revenue trend", top_k=1)
    assert results[0]["id"] == "gold-1"


async def test_add_candidate_trio_then_promote(store):
    trio_id = await add_candidate_trio(
        store, question="new question", sql="SELECT 1", report="report", tags=["custom"]
    )
    assert await store.aget(CANDIDATE_NAMESPACE, trio_id) is not None

    promoted = await promote_to_golden(store, trio_id)

    assert promoted is True
    assert await store.aget(CANDIDATE_NAMESPACE, trio_id) is None
    golden_item = await store.aget(GOLDEN_NAMESPACE, trio_id)
    assert golden_item.value["question"] == "new question"


async def test_promote_unknown_trio_returns_false(store):
    assert await promote_to_golden(store, "does-not-exist") is False
