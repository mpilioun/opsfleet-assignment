"""Golden Knowledge Bucket: past Question -> SQL -> Report "trios".

Storage: the existing LangGraph Postgres Store (no new infra beyond enabling
pgvector on the same Postgres instance - see postgres_manager.py). `golden`
trios are the curated/promoted set; `candidate` trios are appended
automatically after each successful analysis and promoted later (see
promote_to_golden). Retrieval is the Store's own semantic search (embeddings
over the `question` field via Gemini), not a hand-rolled matcher - `asearch`
is called with `query=` and results are ranked by cosine similarity, golden
tier first.
"""

import uuid
from typing import Any

from src.data.golden_bucket_seeds import SEED_TRIOS

GOLDEN_NAMESPACE = ("golden_bucket", "golden")
CANDIDATE_NAMESPACE = ("golden_bucket", "candidate")

# Below this cosine similarity, a match is noise, not a genuinely similar past question.
MIN_SIMILARITY_SCORE = 0.5


async def ensure_seeded(store: Any) -> None:
    """Seed the golden namespace on first boot if it's empty. No-op otherwise."""
    existing = await store.asearch(GOLDEN_NAMESPACE, limit=1)
    if existing:
        return
    for trio in SEED_TRIOS:
        await store.aput(GOLDEN_NAMESPACE, trio["id"], trio)


async def search_similar_trios(
    store: Any, question: str, top_k: int = 3
) -> list[dict[str, Any]]:
    """Semantic search for trios whose question resembles `question`, golden ranked above candidate."""
    golden_hits = await store.asearch(GOLDEN_NAMESPACE, query=question, limit=top_k)
    remaining = top_k - len(golden_hits)
    candidate_hits = (
        await store.asearch(CANDIDATE_NAMESPACE, query=question, limit=remaining)
        if remaining > 0
        else []
    )

    results = []
    for item in (*golden_hits, *candidate_hits):
        if item.score is not None and item.score < MIN_SIMILARITY_SCORE:
            continue
        results.append(item.value)
    return results


async def add_candidate_trio(
    store: Any, *, question: str, sql: str, report: str, tags: list[str] | None = None
) -> str:
    """Record a completed analysis as a candidate trio for later promotion (system-level learning)."""
    trio_id = str(uuid.uuid4())
    await store.aput(
        CANDIDATE_NAMESPACE,
        trio_id,
        {
            "id": trio_id,
            "question": question,
            "sql": sql,
            "report": report,
            "tags": tags or [],
        },
    )
    return trio_id


async def promote_to_golden(store: Any, trio_id: str) -> bool:
    """Move a candidate trio into the golden tier. Returns False if it wasn't found."""
    item = await store.aget(CANDIDATE_NAMESPACE, trio_id)
    if item is None:
        return False
    await store.aput(GOLDEN_NAMESPACE, trio_id, item.value)
    await store.adelete(CANDIDATE_NAMESPACE, trio_id)
    return True
