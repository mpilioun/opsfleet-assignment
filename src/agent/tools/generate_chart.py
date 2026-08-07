from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from pydantic import ValidationError

from src.models.artifacts import ChartArtifact, ChartSeries, ChartType
from src.observability.logging import get_logger

logger = get_logger(__name__)

MAX_CHART_DATA_POINTS = 500


@tool
async def generate_chart(
    chart_type: ChartType,
    data: list[dict[str, str | int | float | None]],
    runtime: ToolRuntime,
    title: str | None = None,
    description: str | None = None,
    x_key: str | None = None,
    y_key: str | None = None,
    name_key: str | None = None,
    value_key: str | None = None,
    series: list[ChartSeries] | None = None,
) -> ToolMessage:
    """Attach a chart to the report. chart_type picks the shape (line, bar,
    pie, scatter, area, stackedBar, groupedBar, combo, waterfall, heatmap,
    histogram, boxplot, treemap, funnel, radar, candlestick, tableChart,
    kpiCard). data is the row records to plot; x_key/y_key/name_key/value_key
    and series pick which fields of each row feed the chart. This only
    validates the shape - rendering happens client-side from these same
    arguments, so get the data right the first time.
    """
    logger.info("Agent Called Tool", extra={"tool_name": "generate_chart"})

    if len(data) > MAX_CHART_DATA_POINTS:
        return ToolMessage(
            content=(
                f"Chart rejected: {len(data)} data points exceeds the "
                f"{MAX_CHART_DATA_POINTS} cap. Aggregate or filter the data first."
            ),
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    try:
        ChartArtifact(
            chart_type=chart_type,
            title=title,
            description=description,
            x_key=x_key,
            y_key=y_key,
            name_key=name_key,
            value_key=value_key,
            series=series,
            data=data,
        )
    except ValidationError as exc:
        return ToolMessage(
            content=f"Chart rejected: {exc}",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    return ToolMessage(
        content=f"Chart ready: {title or chart_type}", tool_call_id=runtime.tool_call_id
    )
