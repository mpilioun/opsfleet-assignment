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

GOLDEN_NAMESPACE = ("golden_bucket", "golden")
CANDIDATE_NAMESPACE = ("golden_bucket", "candidate")

# Below this cosine similarity, a match is noise, not a genuinely similar past question.
MIN_SIMILARITY_SCORE = 0.5

SEED_TRIOS: list[dict[str, Any]] = [
    {
        "id": "seed-top-customers",
        "question": "Who are our top 10 customers by total spend?",
        "sql": (
            "SELECT user_id, SUM(sale_price) AS total_spend "
            "FROM bigquery-public-data.thelook_ecommerce.order_items "
            "GROUP BY user_id ORDER BY total_spend DESC LIMIT 10"
        ),
        "report": (
            "## Top Customers by Spend\n\n"
            "- Top 10 customers (identified by internal customer ID, never by name/email) "
            "account for a disproportionate share of revenue.\n"
            "- **Action item:** consider a loyalty/retention offer targeted at this cohort "
            "before the next quarter."
        ),
        "tags": ["customer_behavior", "top_customers"],
    },
    {
        "id": "seed-product-comparison",
        "question": "Compare the performance of Product A and Product B and explain why they differ.",
        "sql": (
            "SELECT p.name, COUNT(oi.id) AS units_sold, SUM(oi.sale_price) AS revenue, "
            "AVG(oi.sale_price) AS avg_price FROM bigquery-public-data.thelook_ecommerce.order_items oi "
            "JOIN bigquery-public-data.thelook_ecommerce.products p ON p.id = oi.product_id "
            "WHERE p.name IN ('Product A', 'Product B') GROUP BY p.name"
        ),
        "report": (
            "## Product Performance Comparison\n\n"
            "- Compare units sold, revenue, and average selling price side by side.\n"
            "- A price or margin gap combined with a units-sold gap usually explains the "
            "difference (e.g. one product is priced above its category's willing-to-pay range).\n"
            "- **Action item:** if the underperformer is priced higher with no differentiation, "
            "test a price adjustment next cycle."
        ),
        "tags": ["product_performance", "comparison"],
    },
    {
        "id": "seed-monthly-revenue",
        "question": "What is our monthly revenue trend over the last 12 months?",
        "sql": (
            "SELECT DATE_TRUNC(o.created_at, MONTH) AS month, SUM(oi.sale_price) AS revenue "
            "FROM bigquery-public-data.thelook_ecommerce.orders o "
            "JOIN bigquery-public-data.thelook_ecommerce.order_items oi ON oi.order_id = o.order_id "
            "GROUP BY month ORDER BY month"
        ),
        "report": (
            "## Monthly Revenue Trend\n\n"
            "- Plot revenue by month; call out the single largest month-over-month swing.\n"
            "- **Action item:** if a seasonal dip repeats yearly, plan a promo ahead of it next time."
        ),
        "tags": ["time_based_metrics", "revenue"],
    },
    {
        "id": "seed-churn-spike",
        "question": "Why did our churn rate spike last month?",
        "sql": (
            "SELECT DATE_TRUNC(o.created_at, MONTH) AS month, "
            "COUNTIF(o.status IN ('Cancelled', 'Returned')) / COUNT(*) AS cancel_return_rate "
            "FROM bigquery-public-data.thelook_ecommerce.orders o GROUP BY month ORDER BY month"
        ),
        "report": (
            "## Churn / Cancellation Spike\n\n"
            "- thelook_ecommerce has no direct churn flag, so approximate churn via the "
            "cancellation/return rate trend and via customers who ordered in the prior month "
            "but not the current one.\n"
            "- Cross-check the spike month against a product/shipping issue (e.g. a spike in "
            "returns for one department) before concluding it's demand-driven.\n"
            "- **Action item:** investigate the top-returned product category from that month."
        ),
        "tags": ["churn", "retention"],
    },
    {
        "id": "seed-state-underspend",
        "question": "Why are users in state X underspending, and how does that compare to state Y?",
        "sql": (
            "SELECT u.state, AVG(spend.total_spend) AS avg_spend_per_customer "
            "FROM bigquery-public-data.thelook_ecommerce.users u JOIN ("
            "SELECT user_id, SUM(sale_price) AS total_spend "
            "FROM bigquery-public-data.thelook_ecommerce.order_items GROUP BY user_id"
            ") spend ON spend.user_id = u.id "
            "WHERE u.state IN ('State X', 'State Y') GROUP BY u.state"
        ),
        "report": (
            "## Spend Comparison by State\n\n"
            "- Compare average spend per customer between the two states; never name individual "
            "customers, only state-level aggregates.\n"
            "- **Action item:** if the gap is large, check whether it correlates with traffic "
            "source or order cancellation rate in that state before assuming it's a demand issue."
        ),
        "tags": ["customer_behavior", "geography"],
    },
    {
        "id": "seed-database-structure",
        "question": "What data do we have available and what can we analyze with it?",
        "sql": "",
        "report": (
            "## Available Data\n\n"
            "- `orders`, `order_items`, `products`, `users` from `thelook_ecommerce`.\n"
            "- Use the `get_schema` tool (not a hand-written SQL query) to answer structure "
            "questions - that keeps the answer accurate as the schema evolves.\n"
            "- Can analyze: customer spend/behavior, product performance, revenue trends, "
            "and cross-cuts by state/city/traffic-source (never by raw name/email)."
        ),
        "tags": ["meta", "schema"],
    },
]


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
