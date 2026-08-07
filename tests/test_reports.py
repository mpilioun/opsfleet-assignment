import pytest
from langgraph.store.memory import InMemoryStore

from src.agent.utils.reports import (
    create_report,
    delete_reports_by_ids,
    get_report,
    list_reports,
)


@pytest.fixture
def store():
    return InMemoryStore()


async def test_create_and_list_report(store):
    report_id = await create_report(
        store, user_id="alice", thread_id="t1", title="Q1 Report", content="revenue up"
    )

    reports = await list_reports(store, user_id="alice")

    assert len(reports) == 1
    assert reports[0]["id"] == report_id
    assert reports[0]["title"] == "Q1 Report"


async def test_list_reports_scoped_to_thread(store):
    await create_report(store, user_id="alice", thread_id="t1", title="A", content="")
    await create_report(store, user_id="alice", thread_id="t2", title="B", content="")

    reports = await list_reports(store, user_id="alice", thread_id="t1")

    assert [r["title"] for r in reports] == ["A"]


async def test_reports_are_scoped_per_user(store):
    await create_report(store, user_id="alice", thread_id="t1", title="Alice's", content="")
    await create_report(store, user_id="bob", thread_id="t1", title="Bob's", content="")

    alice_reports = await list_reports(store, user_id="alice")

    assert [r["title"] for r in alice_reports] == ["Alice's"]


async def test_get_report_returns_body(store):
    report_id = await create_report(
        store, user_id="alice", thread_id="t1", title="Q1", content="revenue up 12%"
    )

    report = await get_report(store, user_id="alice", report_id=report_id)

    assert report["content"] == "revenue up 12%"


async def test_get_report_is_scoped_per_user(store):
    report_id = await create_report(
        store, user_id="alice", thread_id="t1", title="Q1", content="secret"
    )

    assert await get_report(store, user_id="bob", report_id=report_id) is None
    assert await get_report(store, user_id="alice", report_id="nope") is None


async def test_delete_reports_by_ids(store):
    r1 = await create_report(store, user_id="alice", thread_id="t1", title="A", content="")
    r2 = await create_report(store, user_id="alice", thread_id="t1", title="B", content="")

    deleted = await delete_reports_by_ids(store, user_id="alice", report_ids=[r1, "not-a-real-id"])

    assert deleted == [r1]
    remaining = await list_reports(store, user_id="alice")
    assert [r["id"] for r in remaining] == [r2]


async def test_delete_does_not_cross_user_boundary(store):
    r1 = await create_report(store, user_id="alice", thread_id="t1", title="A", content="")

    deleted = await delete_reports_by_ids(store, user_id="bob", report_ids=[r1])

    assert deleted == []
    assert len(await list_reports(store, user_id="alice")) == 1
