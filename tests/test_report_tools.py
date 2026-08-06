from types import SimpleNamespace

from langgraph.store.memory import InMemoryStore

from src.agent.context import AgentContext
from src.agent.tools.delete_reports import delete_reports
from src.agent.tools.find_reports import find_reports
from src.agent.tools.save_report import save_report


def _fake_runtime(store, user_id="alice", thread_id="t1") -> SimpleNamespace:
    return SimpleNamespace(
        tool_call_id="call-1", store=store, context=AgentContext(user_id=user_id, thread_id=thread_id)
    )


async def test_save_then_find_report():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    save_result = await save_report.coroutine(title="Q1 Report", content="body", runtime=runtime)
    assert save_result.status == "success"

    find_result = await find_reports.coroutine(runtime=runtime, query=None, this_conversation_only=False)
    assert "Q1 Report" in find_result.content


async def test_find_reports_scoped_to_this_conversation():
    store = InMemoryStore()
    runtime_t1 = _fake_runtime(store, thread_id="t1")
    runtime_t2 = _fake_runtime(store, thread_id="t2")
    await save_report.coroutine(title="Thread1 report", content="", runtime=runtime_t1)
    await save_report.coroutine(title="Thread2 report", content="", runtime=runtime_t2)

    result = await find_reports.coroutine(runtime=runtime_t1, query=None, this_conversation_only=True)

    assert "Thread1 report" in result.content
    assert "Thread2 report" not in result.content


async def test_delete_reports_requires_ids():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    result = await delete_reports.coroutine(report_ids=[], runtime=runtime)

    assert result.status == "error"


async def test_delete_reports_removes_saved_report():
    store = InMemoryStore()
    runtime = _fake_runtime(store)
    save_result = await save_report.coroutine(title="To delete", content="", runtime=runtime)
    report_id = save_result.content.split()[-1].rstrip(".")

    delete_result = await delete_reports.coroutine(report_ids=[report_id], runtime=runtime)

    assert delete_result.status == "success"
    find_result = await find_reports.coroutine(runtime=runtime, query=None, this_conversation_only=False)
    assert "No matching reports" in find_result.content


async def test_delete_reports_cannot_touch_another_users_reports():
    store = InMemoryStore()
    alice_runtime = _fake_runtime(store, user_id="alice")
    bob_runtime = _fake_runtime(store, user_id="bob")
    save_result = await save_report.coroutine(title="Alice's report", content="", runtime=alice_runtime)
    report_id = save_result.content.split()[-1].rstrip(".")

    delete_result = await delete_reports.coroutine(report_ids=[report_id], runtime=bob_runtime)

    assert delete_result.status == "error"
