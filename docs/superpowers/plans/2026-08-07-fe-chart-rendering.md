# FE Chart Rendering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `generate_chart`'s matplotlib-PNG-to-local-disk approach with a structured chart artifact the frontend renders natively (interactive, no server-side image).

**Architecture:** `generate_chart` becomes a pure validation boundary — its tool-call arguments *are* the chart's full spec (`chart_type` + axis/series keys + `data` rows), validated by a pydantic model and returned as a short confirmation message, no file I/O. The frontend renders straight from the tool call's own arguments (already the full spec) through a ported Plotly transform map — no result round-trip, no static file serving.

**Tech Stack:** Python/pydantic (backend tool + model), TypeScript/React + `react-plotly.js` (frontend renderer).

**Spec:** `docs/superpowers/specs/2026-08-07-fe-chart-rendering-design.md` (read this first — it has the full rationale, including two corrections made while writing this plan: snake_case field names, reject-not-truncate for oversized data).

## Global Constraints

- Conventional commit messages for every commit (e.g. `feat(agent): ...`, `refactor(frontend): ...`).
- Run `make compile` (isort + ruff format + ruff check --fix on `src/`) after backend code changes, before considering a backend task done.
- New tools/features get unit tests.
- Every tool function's first body line is `logger.info("Agent Called Tool", extra={"tool_name": "<name>"})` (see `run_sql.py`, `get_schema.py` for the exact pattern) — `generate_chart` already does this; keep it.
- Backend tests run via `.venv/bin/python -m pytest tests/ -q` from the repo root.
- Frontend commands run from `frontend/`: `npm run typecheck`, `npx vite build`.

---

### Task 1: Chart artifact pydantic model

**Files:**
- Create: `src/models/artifacts.py` (this is where `ReportWriterResult` and other pydantic models already live — `src/models/subagent_results.py` — not a new `src/agent/models/` package)
- Test: `tests/test_artifacts_model.py`

**Interfaces:**
- Consumes: nothing new (pydantic, stdlib `typing`).
- Produces: `ChartType` (a `Literal` of 18 strings — 18, not 16: recount below), `ChartSeries`, `ChartArtifact` — importable as `from src.models.artifacts import ChartArtifact, ChartSeries, ChartType`. Task 2 imports all three.

Note on the type count: the spec says "16 chart types" but the actual `Literal` has 18 entries (`line, bar, pie, scatter, area, stackedBar, groupedBar, combo, waterfall, heatmap, histogram, boxplot, treemap, funnel, radar, candlestick, tableChart, kpiCard` — count them: that's 18). Use the exact list below; it's the one Revmark's own type actually has, the "16" in prose was an approximation.

- [ ] **Step 1: Write the failing test**

Create `tests/test_artifacts_model.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_artifacts_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.models.artifacts'` (or similar import error).

- [ ] **Step 3: Write the model**

Create `src/models/artifacts.py`:

```python
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
        default=None, description="Key for slice or node names (pie, treemap, funnel, radar)"
    )
    value_key: str | None = Field(
        default=None,
        description="Key for primary numeric values (pie, treemap, funnel, histogram, waterfall, kpiCard)",
    )
    series: list[ChartSeries] | None = None
    data: list[dict[str, str | int | float | None]]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_artifacts_model.py -v`
Expected: 3 passed.

- [ ] **Step 5: `make compile`**

Run: `make compile`
Expected: isort/ruff format/ruff check all clean (no errors; reformatting the new file is fine).

- [ ] **Step 6: Commit**

```bash
git add src/models/artifacts.py tests/test_artifacts_model.py
git commit -m "feat(agent): add ChartArtifact/ChartSeries model for chart tool args"
```

---

### Task 2: Rewrite `generate_chart` as a validation-only tool

**Files:**
- Modify: `src/agent/tools/generate_chart.py` (full rewrite)
- Modify: `tests/test_generate_chart.py` (full rewrite)

**Interfaces:**
- Consumes: `ChartArtifact`, `ChartSeries`, `ChartType` from Task 1 (`src.models.artifacts`).
- Produces: `generate_chart` tool (same name, same import path `src.agent.tools.generate_chart`), now with a different signature — `chart_type: ChartType, data: list[dict], runtime: ToolRuntime, title: str | None = None, description: str | None = None, x_key: str | None = None, y_key: str | None = None, name_key: str | None = None, value_key: str | None = None, series: list[ChartSeries] | None = None`. Also exports `MAX_CHART_DATA_POINTS = 500`. No other task consumes this directly (the frontend reads the tool call's raw arguments, not this module), but `src/agent/tools/__init__.py`'s existing export of `generate_chart` must keep working unchanged.

- [ ] **Step 1: Check how `generate_chart` is currently exported**

Run: `grep -n "generate_chart" src/agent/tools/__init__.py`

Confirm it's re-exported by name only (no signature-specific wrapping) — if so, no change needed there. If it's referenced anywhere else (`grep -rn "generate_chart" src/ frontend/src/`), note every call site; this task only touches the tool's own file and its test, but check nothing else imports `CHARTS_DIR` from this module (Task 3 also touches a `CHARTS_DIR`, a *different* one, in `src/app/main.py` — don't confuse the two).

- [ ] **Step 2: Write the failing tests**

Replace `tests/test_generate_chart.py` entirely with:

```python
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_generate_chart.py -v`
Expected: FAIL — `generate_chart` still has the old `title/labels/values/chart_type` signature, so these calls raise `TypeError` for unexpected keyword arguments (or `ImportError` for `MAX_CHART_DATA_POINTS`, which doesn't exist yet).

- [ ] **Step 4: Rewrite the tool**

Replace `src/agent/tools/generate_chart.py` entirely with:

```python
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
            content=f"Chart rejected: {exc}", status="error", tool_call_id=runtime.tool_call_id
        )

    return ToolMessage(
        content=f"Chart ready: {title or chart_type}", tool_call_id=runtime.tool_call_id
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_generate_chart.py -v`
Expected: 3 passed.

- [ ] **Step 6: Run the full backend test suite**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: all pass, no failures introduced elsewhere (e.g. nothing else imported the old `CHARTS_DIR`/`uuid`/`Path` from this module — Step 1 already checked this, this is the confirming run).

- [ ] **Step 7: `make compile`**

Run: `make compile`
Expected: clean.

- [ ] **Step 8: Commit**

```bash
git add src/agent/tools/generate_chart.py tests/test_generate_chart.py
git commit -m "feat(agent): generate_chart validates a chart artifact instead of rendering a PNG"
```

---

### Task 3: Backend cleanup — drop matplotlib, the `/charts` static mount, and `chart_path`

**Files:**
- Modify: `pyproject.toml` (remove `matplotlib` dependency line)
- Modify: `src/app/main.py` (remove `CHARTS_DIR`, the `StaticFiles` mount, and the now-unused imports)
- Modify: `src/models/subagent_results.py` (remove `ReportWriterResult.chart_path`)

**Interfaces:**
- Consumes: nothing new.
- Produces: `ReportWriterResult` with only `report: str` (the `chart_path` field is gone — confirmed via Task 1's grep that nothing reads it).

- [ ] **Step 1: Remove `chart_path` from `ReportWriterResult`**

In `src/models/subagent_results.py`, remove:

```python
    chart_path: str | None = Field(
        default=None, description="Path to a generated chart image, if one was created."
    )
```

leaving only `report: str = Field(...)` in that class.

- [ ] **Step 2: Remove the `/charts` static mount from `src/app/main.py`**

Remove the line `CHARTS_DIR = Path("charts")`, the two lines:
```python
CHARTS_DIR.mkdir(exist_ok=True)
app.mount("/charts", StaticFiles(directory=str(CHARTS_DIR)), name="charts")
```
and the now-unused imports `from pathlib import Path` and `from fastapi.staticfiles import StaticFiles` (confirm both are unused elsewhere in the file after removal — `grep -n "Path\|StaticFiles" src/app/main.py` should show nothing left besides what you're deleting).

- [ ] **Step 3: Drop the matplotlib dependency**

Run `grep -rn "matplotlib" src/ tests/` to confirm no other file references it (Task 2 already removed the only import) — expect no output. Then run `uv remove matplotlib` from the repo root, which edits `pyproject.toml` and `uv.lock` together in one step.

- [ ] **Step 4: Run the full backend test suite**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: all pass.

- [ ] **Step 5: `make compile`**

Run: `make compile`
Expected: clean.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock src/app/main.py src/models/subagent_results.py
git commit -m "refactor(agent): drop matplotlib, /charts static mount, and unused chart_path field"
```

(If the lockfile has a different name/path than `uv.lock`, use that instead — check `ls *.lock` first.)

---

### Task 4: Frontend chart deps + `ChartArtifact` type

**Files:**
- Modify: `frontend/package.json` (add `plotly.js`, `react-plotly.js`, `@types/react-plotly.js`)
- Create: `frontend/src/copilot/types/artifacts.ts`

**Interfaces:**
- Consumes: nothing new.
- Produces: `ChartType`, `ChartSeries`, `ChartArtifact` TypeScript types, importable as `import type { ChartArtifact, ChartSeries, ChartType } from "../../types/artifacts"` (relative path from `frontend/src/copilot/components/tool-renderers/`) or `"./types/artifacts"` (relative path from `frontend/src/copilot/utils/`) — both resolve to the same file at `frontend/src/copilot/types/artifacts.ts`. Task 5 and Task 6 both import from here.

- [ ] **Step 1: Add the dependencies**

From `frontend/`, run:

```bash
npm install plotly.js@^3.0.1 react-plotly.js@^2.6.0
npm install --save-dev @types/react-plotly.js@^2.6.4
```

- [ ] **Step 2: Create the type file**

Create `frontend/src/copilot/types/artifacts.ts`:

```typescript
export type ChartType =
  | "line"
  | "bar"
  | "pie"
  | "scatter"
  | "area"
  | "stackedBar"
  | "groupedBar"
  | "combo"
  | "waterfall"
  | "heatmap"
  | "histogram"
  | "boxplot"
  | "treemap"
  | "funnel"
  | "radar"
  | "candlestick"
  | "tableChart"
  | "kpiCard";

export type ValueFormat = "raw" | "integer" | "compact";

export type ChartSeries = {
  data_key: string;
  label?: string;
  axis_label?: string;
  value_format?: ValueFormat;
  value_prefix?: string;
  value_suffix?: string;
};

export type ChartArtifact = {
  chart_type: ChartType;
  title?: string;
  description?: string;
  x_key?: string;
  y_key?: string;
  name_key?: string;
  value_key?: string;
  series?: ChartSeries[];
  data: Record<string, string | number | null>[];
};
```

- [ ] **Step 3: Typecheck**

From `frontend/`, run: `npm run typecheck`
Expected: passes (this file isn't imported by anything yet, so there's nothing to break — this just confirms the new file itself is syntactically valid TypeScript).

- [ ] **Step 4: Commit**

```bash
git add package.json package-lock.json frontend/src/copilot/types/artifacts.ts
git commit -m "feat(frontend): add plotly deps and ChartArtifact type"
```

(Adjust the `package.json`/lockfile paths above if run from inside `frontend/` — `git add` paths are relative to your cwd; use `frontend/package.json` etc. if committing from the repo root.)

---

### Task 5: Port the Plotly transform map

**Files:**
- Create: `frontend/src/copilot/utils/chart-transforms.ts`

**Interfaces:**
- Consumes: `ChartArtifact`, `ChartType` from Task 4.
- Produces: `chartTransformMap: Record<ChartType, ChartTransformFn>` and `PlotlyChartData` type, importable as `import { chartTransformMap } from "../../utils/chart-transforms"` (relative path from `frontend/src/copilot/components/tool-renderers/`). Task 6 consumes this.

- [ ] **Step 1: Copy the ported file verbatim**

The full corrected content (snake_case field access, 3 color values swapped to this app's exact CSS-token equivalents, the dead `renderAs` branch simplified, the unused table-formatter tail dropped — see the spec's "Corrections found during plan-writing" section for why) is at:

`/Users/mike/Desktop/opsfleet-assignment/docs/superpowers/plans/chart-transforms-ported.ts.txt`

Copy that file's exact contents into `frontend/src/copilot/utils/chart-transforms.ts` (e.g. `cp docs/superpowers/plans/chart-transforms-ported.ts.txt frontend/src/copilot/utils/chart-transforms.ts` from the repo root, then delete the `.txt` reference file since it was only scaffolding for this step: `git rm docs/superpowers/plans/chart-transforms-ported.ts.txt` — check `git status` first in case it's not yet tracked, in which case just `rm` it).

- [ ] **Step 2: Typecheck**

From `frontend/`, run: `npm run typecheck`
Expected: passes. If it doesn't, the likely cause is a stray camelCase field reference the port missed — search the new file for `xKey|yKey|nameKey|valueKey|dataKey|valuePrefix|valueSuffix` (all should be snake_case now) and fix any hits.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/copilot/utils/chart-transforms.ts
git rm docs/superpowers/plans/chart-transforms-ported.ts.txt
git commit -m "feat(frontend): port Plotly chart transform map for all 18 chart types"
```

---

### Task 6: Rewrite the chart tool-call renderer

**Files:**
- Modify: `frontend/src/copilot/components/tool-renderers/chart-renderer.tsx` (full rewrite)
- Modify: `frontend/src/styles.css` (remove `.chart-image`)

**Interfaces:**
- Consumes: `chartTransformMap` (Task 5), `ChartArtifact` (Task 4), existing `ToolCard`/`isErrorResult`/`MutedText` (`../tool-card`, `../tool-display`), existing `TOOL_NAMES.GENERATE_CHART` (`./constants`).
- Produces: `useChartRenderer` (same export name — `tool-renderers/index.tsx` already imports this and needs no change).

- [ ] **Step 1: Rewrite the renderer**

Replace `frontend/src/copilot/components/tool-renderers/chart-renderer.tsx` entirely with:

```tsx
import Plot from "react-plotly.js";
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

import { ToolCard } from "../tool-card";
import { isErrorResult, MutedText } from "../tool-display";
import { TOOL_NAMES } from "./constants";
import type { ChartArtifact } from "../../types/artifacts";
import { chartTransformMap } from "../../utils/chart-transforms";

const chartSeriesSchema = z.object({
  data_key: z.string(),
  label: z.string().optional(),
  axis_label: z.string().optional(),
  value_format: z.enum(["raw", "integer", "compact"]).optional(),
  value_prefix: z.string().optional(),
  value_suffix: z.string().optional(),
});

const chartSchema = z.object({
  chart_type: z.string().optional(),
  title: z.string().optional(),
  description: z.string().optional(),
  x_key: z.string().optional(),
  y_key: z.string().optional(),
  name_key: z.string().optional(),
  value_key: z.string().optional(),
  series: z.array(chartSeriesSchema).optional(),
  data: z.array(z.record(z.union([z.string(), z.number(), z.null()]))).optional(),
});

export const useChartRenderer = (): void => {
  useRenderTool(
    {
      name: TOOL_NAMES.GENERATE_CHART,
      parameters: chartSchema,
      render: ({ status, parameters, result }) => {
        const errored = status === "complete" && isErrorResult(result);
        const ready =
          status === "complete" && !errored && parameters?.chart_type && parameters?.data?.length;

        return (
          <ToolCard.Root tone="info" status={status} variant={errored ? "error" : "default"}>
            <ToolCard.Header title={parameters?.title ?? "Chart"}>
              <ToolCard.Subtitle>
                <MutedText>
                  {status !== "complete"
                    ? "Building chart…"
                    : errored
                      ? result
                      : "Chart ready"}
                </MutedText>
              </ToolCard.Subtitle>
            </ToolCard.Header>
            {ready && (
              <ToolCard.Body>
                <ChartPlot artifact={parameters as ChartArtifact} />
              </ToolCard.Body>
            )}
          </ToolCard.Root>
        );
      },
    },
    [],
  );
};

const ChartPlot: React.FC<{ artifact: ChartArtifact }> = ({ artifact }) => {
  const transform = chartTransformMap[artifact.chart_type];
  if (!transform) return null;
  const { data, layout } = transform(artifact);

  return (
    <Plot
      data={data}
      layout={{ ...layout, height: 300 }}
      config={{ displayModeBar: false, responsive: true }}
      useResizeHandler
      style={{ width: "100%", height: 300 }}
    />
  );
};
```

Note what's gone from the old version: `AGENT_BACKEND_URL` import, `extractChartUrl`, the `<img>` tag, and the `chart_type`/`labels`/`values` zod schema (replaced by the full `ChartArtifact`-shaped schema above, since the tool's args changed in Task 2).

- [ ] **Step 2: Remove the now-unused `.chart-image` CSS rule**

In `frontend/src/styles.css`, remove:

```css
.chart-image {
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid var(--border);
}
```

- [ ] **Step 3: Typecheck**

From `frontend/`, run: `npm run typecheck`
Expected: passes.

- [ ] **Step 4: Build**

From `frontend/`, run: `npx vite build`
Expected: succeeds (matches the existing convention of checking a clean build after frontend changes — see prior session's verification of the tool-renderers split).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/copilot/components/tool-renderers/chart-renderer.tsx frontend/src/styles.css
git commit -m "refactor(frontend): render charts natively from tool-call args via Plotly"
```

---

### Task 7: Update the report-writer prompt, refresh the knowledge graph, final verification

**Files:**
- Modify: `src/artifacts/prompts/report_writer_subagent.md` (only if the tool's new args need explanation — check first)
- Modify: `graphify-out/` (regenerated, not hand-edited)

**Interfaces:**
- Consumes: everything from Tasks 1-6.
- Produces: nothing new — this is the final verification + housekeeping task.

- [ ] **Step 1: Check whether the report-writer prompt needs updating**

Read `src/artifacts/prompts/report_writer_subagent.md`. It currently says "Optionally attach a chart when it clarifies a trend or comparison" with no mention of the tool's shape (the tool's own docstring carries that detail, per this codebase's existing convention — `run_sql`'s prompt doesn't restate its parameters either). Leave the prompt as-is unless you find it now says something factually wrong about the old PNG behavior (it doesn't, as of this plan's writing) — don't add unrequested detail.

- [ ] **Step 2: Full backend verification**

Run: `.venv/bin/python -m pytest tests/ -q`
Expected: all pass.

Run: `make compile`
Expected: clean.

- [ ] **Step 3: Full frontend verification**

From `frontend/`, run: `npm run typecheck && npx vite build`
Expected: both succeed.

- [ ] **Step 4: Refresh the knowledge graph**

From the repo root, run: `graphify update .`
Expected: "Code graph updated" with node/edge/community counts — this is AST-only, no LLM cost (see `CLAUDE.md`'s graphify rules).

- [ ] **Step 5: Commit**

```bash
git add graphify-out
git commit -m "chore(graphify): update knowledge graph after chart-rendering rewrite"
```

If Step 1 found a real prompt fix needed, commit that separately first with its own conventional-commit message before this final graphify commit.
