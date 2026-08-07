"""Chart artifact contract between the generate_chart tool's arguments and the
frontend's Plotly renderer. The tool call's own arguments ARE the chart spec -
this model only validates their shape; nothing here crosses a JSON-file or
other serialization boundary, so field names are plain snake_case with no
aliasing (contrast Revmark_AI's version of this file, which aliases to
camelCase because its artifacts cross a sandbox-script JSON boundary that
doesn't exist here).
"""

from typing import Literal

from pydantic import BaseModel, Field

ChartType = Literal[
    "line",
    "bar",
    "pie",
    "scatter",
    "area",
    "stackedBar",
    "groupedBar",
    "combo",
    "waterfall",
    "heatmap",
    "histogram",
    "boxplot",
    "treemap",
    "funnel",
    "radar",
    "candlestick",
    "tableChart",
    "kpiCard",
]


class ChartSeries(BaseModel):
    """A single data series within a chart artifact."""

    data_key: str = Field(description="Key in each data record for this series' values")
    label: str | None = Field(default=None, description="Human-readable series label")
    axis_label: str | None = Field(
        default=None, description="Label for the axis this series belongs to"
    )
    value_format: Literal["raw", "integer", "compact"] | None = Field(
        default=None, description="How to format numeric values"
    )
    value_prefix: str | None = Field(
        default=None, description="Prefix for displayed values (e.g. '$')"
    )
    value_suffix: str | None = Field(
        default=None, description="Suffix for displayed values (e.g. '%')"
    )


class ChartArtifact(BaseModel):
    """A chart artifact: the full spec the frontend needs to render one chart,
    built directly from the generate_chart tool's arguments."""

    chart_type: ChartType
    title: str | None = None
    description: str | None = None
    x_key: str | None = Field(
        default=None,
        description="Key in data records for the x-axis or horizontal dimension",
    )
    y_key: str | None = Field(
        default=None,
        description="Key in data records for the y-axis or vertical dimension (heatmap, treemap parent, ...)",
    )
    name_key: str | None = Field(
        default=None,
        description="Key for slice or node names (pie, treemap, funnel, radar)",
    )
    value_key: str | None = Field(
        default=None,
        description="Key for primary numeric values (pie, treemap, funnel, histogram, waterfall, kpiCard)",
    )
    series: list[ChartSeries] | None = None
    data: list[dict[str, str | int | float | None]]
