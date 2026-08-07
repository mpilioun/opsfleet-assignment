# FE chart rendering (native, no server-side images)

## Context

Charts today come from `generate_chart` (`src/agent/tools/generate_chart.py`):
matplotlib renders a PNG to a local `charts/` directory, the tool result string
is regex-parsed by the frontend for a path (`chart-renderer.tsx`), and the
result is served as a static `<img>` via a FastAPI `StaticFiles` mount at
`/charts`. This is fragile — local disk, lost on redeploy, no multi-replica
story — and produces a static image instead of an interactive chart.

`Revmark_APP`/`Revmark_AI` (sibling local repos, same architecture family)
solve this by having the agent emit a structured `ChartArtifact` (chart type,
axis/series keys, data rows) that the frontend renders natively with
`react-plotly.js`. This spec ports that pattern into this codebase.

Reports-as-chat-attachments (the other half of the original ask) is a
**separate sub-project**, deliberately out of scope here — it will want to
embed chart artifacts once this exists, so this ships first.

## Decisions

- Chart library: **react-plotly.js** (matches Revmark, proven transforms to
  port directly rather than write from scratch).
- Chart type coverage: **full parity with Revmark's 16-type union** (line,
  bar, pie, scatter, area, stackedBar, groupedBar, combo, waterfall, heatmap,
  histogram, boxplot, treemap, funnel, radar, candlestick, tableChart,
  kpiCard) — even though most retail-insights questions will only exercise
  bar/line/pie/area.
- `ReportWriterResult.chart_path` (a file path) is **dropped**, not replaced.
  Nothing downstream reads it; the `generate_chart` tool call itself is the
  chart record.
- Explicit non-goal: the LLM still hand-transcribes numbers into the tool
  call's `data` array (same trust boundary `labels`/`values` had today) —
  there's no sandbox/code-execution step here to compute exact values. Not
  fixed by this spec.

## Backend changes

**New `src/agent/models/artifacts.py`** — ported from
`Revmark_AI/src/agent/models/artifacts.py`, trimmed to what we need (drop the
`FinancialAnalysisOutput`/sandbox-result wrapper, keep the artifact shapes):

```python
ChartType = Literal["line", "bar", "pie", "scatter", "area", "stackedBar",
    "groupedBar", "combo", "waterfall", "heatmap", "histogram", "boxplot",
    "treemap", "funnel", "radar", "candlestick", "tableChart", "kpiCard"]

class ChartSeries(BaseModel):
    data_key: str = Field(..., alias="dataKey")
    label: str | None = None
    axis_label: str | None = Field(default=None, alias="axisLabel")
    value_format: Literal["raw", "integer", "compact"] | None = Field(default=None, alias="valueFormat")
    value_prefix: str | None = Field(default=None, alias="valuePrefix")
    value_suffix: str | None = Field(default=None, alias="valueSuffix")
    model_config = {"populate_by_name": True}

class ChartArtifact(BaseModel):
    chart_type: ChartType = Field(..., alias="chartType")
    title: str | None = None
    description: str | None = None
    x_key: str | None = Field(default=None, alias="xKey")
    y_key: str | None = Field(default=None, alias="yKey")
    name_key: str | None = Field(default=None, alias="nameKey")
    value_key: str | None = Field(default=None, alias="valueKey")
    series: list[ChartSeries] | None = None
    data: list[dict[str, str | int | float | None]]
    model_config = {"populate_by_name": True}
```

No `id` field (Revmark's sandbox emits multiple artifacts per run and needs
to key them; here one tool call = one chart, the tool call ID already
identifies it).

**New `src/agent/utils/artifact_validation.py`** — ported from
`Revmark_AI/src/agent/utils/artifact_validation.py`, trimmed to the one
artifact type:

```python
MAX_CHART_DATA_POINTS = 500

def validate_chart_artifact(raw: dict) -> ChartArtifact:
    """Raises pydantic.ValidationError on a malformed artifact. Truncates
    (doesn't reject) oversized data, logging a warning."""
```

**`src/agent/tools/generate_chart.py`** — rewritten. Tool args become the
`ChartArtifact` fields directly (via `**kwargs` collected into the dict
`validate_chart_artifact` expects, or an explicit parameter per field —
follow whatever pattern `run_sql`/`get_schema` already use for multi-field
tool args). Body: build the dict from args, call
`validate_chart_artifact`, catch `ValidationError` and return an error
`ToolMessage` (consistent with `run_sql`'s `SqlGuardError` handling), else
return a short confirmation `ToolMessage`. No `matplotlib`, `uuid`, `Path`,
or file I/O.

**`pyproject.toml`** — drop the `matplotlib` dependency (only consumer was
this tool).

**`src/app/main.py`** — remove `CHARTS_DIR`, the `StaticFiles` import if
unused elsewhere, and the `/charts` mount.

**`src/models/subagent_results.py`** — remove `ReportWriterResult.chart_path`.

## Frontend changes

**Add deps**: `react-plotly.js`, `plotly.js` (and `@types/react-plotly.js`
if available).

**New `frontend/src/copilot/types/artifacts.ts`** — `ChartType`,
`ChartSeries`, `ChartArtifact` TypeScript types, ported from
`Revmark_APP/revmark/src/copilot/types/artifacts.ts`, trimmed to the chart
shape only (no `TableArtifact`/`ImageArtifact`/`FileArtifact` — those belong
to the reports-as-attachments sub-project if/when it needs them). Since
these fields arrive as tool-call `parameters` (already camelCase per the
pydantic aliases above), **no raw/normalize layer is needed** — Revmark's
`normalizeChartArtifact` exists because their data crosses a JSON-file
sandbox boundary that can be snake_case; ours doesn't.

**New `frontend/src/copilot/utils/chart-transforms.ts`** — the
`chartType → {data, layout}` Plotly transform map, ported from
`Revmark_APP/revmark/src/copilot/utils/artifact-transforms.ts` (688 lines,
all 16 types). Swap Revmark's hardcoded hex colors in `layout` for this
app's CSS custom properties (`--bg`, `--text`, `--muted`, `--border`,
`--accent`, `--info`, `--warn`, `--danger`) so charts theme correctly.

**Replace `frontend/src/copilot/components/tool-renderers/chart-renderer.tsx`**:
render directly from the tool call's `parameters` (already a full
`ChartArtifact`) through `chartTransformMap`, inside the existing
`ToolCard` shell. Drop `extractChartUrl`, the `<img>`, and the
`AGENT_BACKEND_URL` import (no longer needed here).

**`frontend/src/styles.css`** — remove the now-unused `.chart-image` rule.

## Testing

- `tests/test_artifact_validation.py` (new): valid `ChartArtifact` passes;
  oversized `data` (>500 points) truncates with a logged warning, doesn't
  raise; invalid `chart_type` raises `ValidationError`.
- `tests/test_generate_chart.py` (replaces today's PNG-write tests): valid
  args → success `ToolMessage`; invalid args (bad `chart_type`, mismatched
  keys) → error `ToolMessage`; no filesystem interaction to mock anymore.
- Frontend: no existing tool-renderer has a test (matches current
  convention across `data-renderers.tsx`/`report-renderers.tsx`/etc.) — skip
  per YAGNI, consistent with the rest of the codebase.

## Out of scope (this spec)

- Reports-as-chat-attachments and their storage — separate sub-project,
  designed next.
- Fixing LLM-transcribed chart data (would need a code-execution step to
  compute exact values from source data, à la Revmark's sandbox) — flagged
  as a known limitation, not solved here.
