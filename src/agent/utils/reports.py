"""Saved Reports library: the "Saved Reports" managers can create, browse, and
delete. Backed by the same Postgres Store as the golden bucket (namespace
("reports", user_id)) - no new SQL tables. `content` is indexed by the same
semantic index as golden-bucket questions (see postgres_manager.py), so
list_reports's `query` can do fuzzy matching like "mentioning Client X".
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from src.observability.logging import get_logger

logger = get_logger(__name__)


def _namespace(user_id: str) -> tuple[str, str]:
    return ("reports", user_id)


async def create_report(
    store: Any, *, user_id: str, thread_id: str, title: str, content: str
) -> str:
    report_id = str(uuid.uuid4())
    await store.aput(
        _namespace(user_id),
        report_id,
        {
            "id": report_id,
            "thread_id": thread_id,
            "title": title,
            "content": content,
            "created_at": datetime.now(UTC).isoformat(),
        },
    )
    logger.info("Report saved", extra={"report_id": report_id, "user_id": user_id})
    return report_id


async def list_reports(
    store: Any,
    *,
    user_id: str,
    thread_id: str | None = None,
    query: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List saved reports, optionally scoped to one conversation and/or matched
    semantically against `query` (e.g. "reports mentioning Client X")."""
    items = await store.asearch(_namespace(user_id), query=query, limit=limit)
    reports = [item.value for item in items]
    if thread_id is not None:
        reports = [r for r in reports if r.get("thread_id") == thread_id]
    return reports


async def get_report(
    store: Any, *, user_id: str, report_id: str
) -> dict[str, Any] | None:
    """Fetch one saved report, body included. None if this user has no such report."""
    item = await store.aget(_namespace(user_id), report_id)
    return item.value if item is not None else None


async def delete_reports_by_ids(
    store: Any, *, user_id: str, report_ids: list[str]
) -> list[str]:
    """Delete the given report ids for this user. Returns the ids that were actually found."""
    namespace = _namespace(user_id)
    deleted = []
    for report_id in report_ids:
        if await store.aget(namespace, report_id) is not None:
            await store.adelete(namespace, report_id)
            deleted.append(report_id)
    logger.info("Reports deleted", extra={"user_id": user_id, "count": len(deleted)})
    return deleted
