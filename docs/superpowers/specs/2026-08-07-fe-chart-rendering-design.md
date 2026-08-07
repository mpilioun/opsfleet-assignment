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

**Corrections found during plan-writing** (superseding the two points below
that assumed otherwise):
- Tool-call argument names are whatever the Python tool's parameters are
  named — LangChain builds the LLM-facing schema straight from the function
  signature, snake_case, no aliasing layer. Revmark's camelCase came from a
  *different* boundary (a sandbox script's JSON file read by the frontend);
  it doesn't apply here. So `ChartArtifact`/`ChartSeries` use plain
  snake_case fields with **no** `alias=`/`populate_by_name`, and the ported
  frontend types/transforms use snake_case field access
  (`artifact.x_key`, `s.data_key`, ...) to match exactly what a tool call
  actually contains.
- Oversized `data` is **rejected**, not truncated. Revmark's truncate-in-
  place works because their frontend reads the *validated* result.json:
  truncating there is visible downstream. Ours renders straight from the
  original tool-call arguments (that's the whole simplification over the
  old PNG path) — a copy mutated inside the tool is invisible to what's
  displayed. So the row cap is a plain `len(data) > 500` check inside
  `generate_chart` that returns an error `ToolMessage`, and there's no
  separate `artifact_validation.py` module — `ChartArtifact.model_validate()`
  is a one-line call, not worth its own file.

## Backend changes

**New `src/agent/models/artifacts.py`** — shape ported from
`Revmark_AI/src/agent/models/artifacts.py` (drop the
`FinancialAnalysisOutput`/sandbox-result wrapper, keep the artifact shapes),
naming corrected per above (no aliases):

```python
ChartType = Literal["line", "bar", "pie", "scatter", "area", "stackedBar",
    "groupedBar", "combo", "waterfall", "heatmap", "histogram", "boxplot",
    "treemap", "funnel", "radar", "candlestick", "tableChart", "kpiCard"]

class ChartSeries(BaseModel):
    data_key: str
    label: str | None = None
    axis_label: str | None = None
    value_format: Literal["raw", "integer", "compact"] | None = None
    value_prefix: str | None = None
    value_suffix: str | None = None

class ChartArtifact(BaseModel):
    chart_type: ChartType
    title: str | None = None
    description: str | None = None
    x_key: str | None = None
    y_key: str | None = None
    name_key: str | None = None
    value_key: str | None = None
    series: list[ChartSeries] | None = None
    data: list[dict[str, str | int | float | None]]
```

No `id` field (Revmark's sandbox emits multiple artifacts per run and needs
to key them; here one tool call = one chart, the tool call ID already
identifies it).

**`src/agent/tools/generate_chart.py`** — rewritten. Tool args become the
`ChartArtifact` fields directly as named parameters (`chart_type`, `data`,
`title`, `description`, `x_key`, `y_key`, `name_key`, `value_key`, `series:
list[ChartSeries] | None`). Body: reject if `len(data) > 500` (own inline
constant, no separate validation module — see correction above), then
`ChartArtifact.model_validate(...)` catching `ValidationError` for a bad
`chart_type`/shape, each returning an error `ToolMessage` (consistent with
`run_sql`'s `SqlGuardError` handling), else return a short confirmation
`ToolMessage`. No `matplotlib`, `uuid`, `Path`, or file I/O.

**`pyproject.toml`** — drop the `matplotlib` dependency (only consumer was
this tool).

**`src/app/main.py`** — remove `CHARTS_DIR`, the `StaticFiles` import if
unused elsewhere, and the `/charts` mount.

**`src/models/subagent_results.py`** — remove `ReportWriterResult.chart_path`.

## Frontend changes

**Add deps**: `react-plotly.js`, `plotly.js` (and `@types/react-plotly.js`
if available).

**New `frontend/src/copilot/types/artifacts.ts`** — `ChartType`,
`ChartSeries`, `ChartArtifact` TypeScript types, shape ported from
`Revmark_APP/revmark/src/copilot/types/artifacts.ts`, trimmed to the chart
shape only (no `TableArtifact`/`ImageArtifact`/`FileArtifact` — those belong
to the reports-as-attachments sub-project if/when it needs them), fields
**snake_case** per the naming correction above (`x_key`, `data_key`, ...).
No raw/normalize layer — the tool call's `parameters` already are this
shape verbatim.

**New `frontend/src/copilot/utils/chart-transforms.ts`** — the
`chartType → {data, layout}` Plotly transform map, ported from
`Revmark_APP/revmark/src/copilot/utils/artifact-transforms.ts` (688 lines,
all 16 types), with: every `artifact.xKey`/`s.dataKey`/etc. field access
renamed to the snake_case equivalent; the trailing table-formatter block
(`formatCellValue`/`TableColumnType`/currency & percent formatters, lines
651-688) dropped — it exists only to format a generic `TableArtifact`'s
cells, which we're not porting; the combo chart's `renderAs` cast dropped
(dead in Revmark too — no `ChartSeries` field ever populates it under either
name — replaced with the plain `i === 0 ? "bar" : "line"` default it always
falls back to). Three literal color values swapped for this app's exact
token equivalents (checked against `styles.css`'s `:root` — most of
Revmark's palette already matches ours exactly, so this is 3 targeted edits,
not a rewrite): `#0f1219` → `#0f131a` (`--bg`), `#1a1e2e` → `#1d212b`
(`--panel`), `#ff6b6b` → `#ef4343` (`--danger`, used for "decreasing" in
waterfall/candlestick). Left untouched because they already equal the app's
tokens: `#E0E6EB`/`#7B899D` (`--text`/`--muted`), `rgba(43,48,59,*)`
(`--border`), `#00e686`/`#19d5e6` (`--accent`/`--info`). Plain hex literals,
not `var(--x)` — Plotly assigns most of these to SVG attributes rather than
CSS properties, and CSS custom-property resolution in raw SVG attributes is
inconsistent across browsers; literal values sidestep that risk entirely.

**Replace `frontend/src/copilot/components/tool-renderers/chart-renderer.tsx`**:
render directly from the tool call's `parameters` (already a full
`ChartArtifact`) through `chartTransformMap`, inside the existing
`ToolCard` shell. Drop `extractChartUrl`, the `<img>`, and the
`AGENT_BACKEND_URL` import (no longer needed here).

**`frontend/src/styles.css`** — remove the now-unused `.chart-image` rule.

## Testing

- `tests/test_generate_chart.py` (replaces today's PNG-write tests): valid
  args → success `ToolMessage`; `data` over the 500-point cap → error
  `ToolMessage`; invalid `chart_type` → error `ToolMessage`; no filesystem
  interaction to mock anymore.
- Frontend: no existing tool-renderer has a test (matches current
  convention across `data-renderers.tsx`/`report-renderers.tsx`/etc.) — skip
  per YAGNI, consistent with the rest of the codebase.

## Out of scope (this spec)

- Reports-as-chat-attachments and their storage — separate sub-project,
  designed next.
- Fixing LLM-transcribed chart data (would need a code-execution step to
  compute exact values from source data, à la Revmark's sandbox) — flagged
  as a known limitation, not solved here.
