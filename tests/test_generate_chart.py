from types import SimpleNamespace

from src.agent.tools.generate_chart import MAX_CHART_DATA_POINTS, generate_chart


def _fake_runtime() -> SimpleNamespace:
    return SimpleNamespace(tool_call_id="call-1")


async def test_generate_chart_accepts_valid_bar_chart():
    result = await generate_chart.coroutine(
        chart_type="bar",
        data=[{"category": "Shoes", "revenue": 1000}, {"category": "Bags", "revenue": 500}],
        runtime=_fake_runtime(),
        title="Revenue by category",
        x_key="category",
        series=[{"data_key": "revenue", "label": "Revenue"}],
    )

    assert result.status != "error"
    assert "Revenue by category" in result.content


async def test_generate_chart_rejects_invalid_chart_type():
    result = await generate_chart.coroutine(
        chart_type="pyramid",
        data=[{"x": 1}],
        runtime=_fake_runtime(),
    )

    assert result.status == "error"
    assert "rejected" in result.content.lower()


async def test_generate_chart_rejects_oversized_data():
    oversized = [{"x": i, "y": i} for i in range(MAX_CHART_DATA_POINTS + 1)]

    result = await generate_chart.coroutine(
        chart_type="line",
        data=oversized,
        runtime=_fake_runtime(),
        series=[{"data_key": "y"}],
    )

    assert result.status == "error"
    assert str(MAX_CHART_DATA_POINTS) in result.content
