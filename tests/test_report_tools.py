from contextlib import contextmanager
from types import SimpleNamespace

from langchain_core.runnables.config import var_child_runnable_config
from langgraph.store.memory import InMemoryStore

from src.agent.tools.delete_reports import delete_reports
from src.agent.tools.find_reports import find_reports
from src.agent.tools.read_report import read_report
from src.agent.tools.save_report import save_report


def _fake_runtime(store) -> SimpleNamespace:
    return SimpleNamespace(tool_call_id="call-1", store=store)


@contextmanager
def _configured(user_id="alice", thread_id="t1"):
    token = var_child_runnable_config.set(
        {"configurable": {"user_id": user_id, "thread_id": thread_id}}
    )
    try:
        yield
    finally:
        var_child_runnable_config.reset(token)


async def test_save_then_find_report():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    with _configured():
        save_result = await save_report.coroutine(title="Q1 Report", content="body", runtime=runtime)
        assert save_result.status == "success"

        find_result = await find_reports.coroutine(runtime=runtime, query=None, this_conversation_only=False)
        assert "Q1 Report" in find_result.content


async def test_find_reports_scoped_to_this_conversation():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    with _configured(thread_id="t1"):
        await save_report.coroutine(title="Thread1 report", content="", runtime=runtime)
    with _configured(thread_id="t2"):
        await save_report.coroutine(title="Thread2 report", content="", runtime=runtime)

    with _configured(thread_id="t1"):
        result = await find_reports.coroutine(runtime=runtime, query=None, this_conversation_only=True)

    assert "Thread1 report" in result.content
    assert "Thread2 report" not in result.content


async def test_read_report_returns_the_body():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    with _configured():
        save_result = await save_report.coroutine(
            title="Q1 Report", content="revenue up 12%", runtime=runtime
        )
        report_id = save_result.content.split()[-1].rstrip(".")

        result = await read_report.coroutine(report_id=report_id, runtime=runtime)

    assert result.status == "success"
    assert "Q1 Report" in result.content
    assert "revenue up 12%" in result.content


async def test_read_report_cannot_read_another_users_report():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    with _configured(user_id="alice"):
        save_result = await save_report.coroutine(
            title="Alice's report", content="secret", runtime=runtime
        )
    report_id = save_result.content.split()[-1].rstrip(".")

    with _configured(user_id="bob"):
        result = await read_report.coroutine(report_id=report_id, runtime=runtime)

    assert result.status == "error"
    assert "secret" not in result.content


async def test_delete_reports_requires_ids():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    with _configured():
        result = await delete_reports.coroutine(report_ids=[], runtime=runtime)

    assert result.status == "error"


async def test_delete_reports_removes_saved_report():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    with _configured():
        save_result = await save_report.coroutine(title="To delete", content="", runtime=runtime)
        report_id = save_result.content.split()[-1].rstrip(".")

        delete_result = await delete_reports.coroutine(report_ids=[report_id], runtime=runtime)
        assert delete_result.status == "success"

        find_result = await find_reports.coroutine(runtime=runtime, query=None, this_conversation_only=False)
        assert "No matching reports" in find_result.content


async def test_delete_reports_cannot_touch_another_users_reports():
    store = InMemoryStore()
    runtime = _fake_runtime(store)

    with _configured(user_id="alice"):
        save_result = await save_report.coroutine(title="Alice's report", content="", runtime=runtime)
    report_id = save_result.content.split()[-1].rstrip(".")

    with _configured(user_id="bob"):
        delete_result = await delete_reports.coroutine(report_ids=[report_id], runtime=runtime)

    assert delete_result.status == "error"
