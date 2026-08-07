import pytest
from pydantic import ValidationError

from src.models.artifacts import ChartArtifact, ChartSeries


def test_valid_bar_chart_artifact():
    artifact = ChartArtifact(
        chart_type="bar",
        title="Revenue by category",
        x_key="category",
        series=[ChartSeries(data_key="revenue", label="Revenue")],
        data=[{"category": "Shoes", "revenue": 1000}, {"category": "Bags", "revenue": 500}],
    )
    assert artifact.chart_type == "bar"
    assert artifact.series[0].data_key == "revenue"


def test_invalid_chart_type_raises():
    with pytest.raises(ValidationError):
        ChartArtifact(chart_type="pyramid", data=[{"x": 1}])


def test_data_is_required():
    with pytest.raises(ValidationError):
        ChartArtifact(chart_type="bar")
