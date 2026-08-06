import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.agent.tools.generate_chart import CHARTS_DIR, generate_chart


def _fake_runtime() -> SimpleNamespace:
    return SimpleNamespace(tool_call_id="call-1")


@pytest.fixture(autouse=True)
def _cleanup_charts_dir():
    yield
    shutil.rmtree(CHARTS_DIR, ignore_errors=True)


async def test_generate_chart_saves_png():
    result = await generate_chart.coroutine(
        title="Revenue", labels=["Jan", "Feb"], values=[1.0, 2.0], runtime=_fake_runtime()
    )

    assert result.status == "success"
    saved_path = Path(result.content.removeprefix("Chart saved to "))
    assert saved_path.exists()
    assert saved_path.suffix == ".png"


async def test_generate_chart_rejects_mismatched_lengths():
    result = await generate_chart.coroutine(
        title="Revenue", labels=["Jan", "Feb"], values=[1.0], runtime=_fake_runtime()
    )

    assert result.status == "error"
