import uuid
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")  # no display server in a CLI/container context
import matplotlib.pyplot as plt
from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

CHARTS_DIR = Path("charts")


@tool
async def generate_chart(
    title: str,
    labels: list[str],
    values: list[float],
    runtime: ToolRuntime,
    chart_type: Literal["bar", "line"] = "bar",
) -> ToolMessage:
    """Render a bar or line chart from labels/values and save it as a PNG.
    Example extensibility hook - new output formats (email, other chart types,
    web-search-sourced charts) plug in the same way: one tool, no framework changes.
    """
    if len(labels) != len(values):
        return ToolMessage(
            content="labels and values must be the same length.",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    CHARTS_DIR.mkdir(exist_ok=True)
    path = CHARTS_DIR / f"{uuid.uuid4()}.png"

    fig, ax = plt.subplots()
    if chart_type == "bar":
        ax.bar(labels, values)
    else:
        ax.plot(labels, values, marker="o")
    ax.set_title(title)
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)

    return ToolMessage(
        content=f"Chart saved to {path}", tool_call_id=runtime.tool_call_id
    )
