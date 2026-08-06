# Retail Insights Agent

A data-analysis chat agent for retail Store/Regional Managers: ask about sales,
inventory, and customer behavior over `bigquery-public-data.thelook_ecommerce`,
discuss the results, and manage a Saved Reports library — with PII masking,
destructive-op confirmation, self-correcting SQL, and full observability.

Built for the Opsfleet AI Technical Assignment. **Full architecture, design
reasoning, and requirement-by-requirement writeup: [`docs/HLD.md`](docs/HLD.md).**
Read that first — this file is just setup + day-to-day commands.

## Quick start

See [`docs/HLD.md` §12](docs/HLD.md#12-setup-instructions) for full setup. Short version:

```bash
uv sync
cp .env.example .env   # set GEMINI_API_KEY at minimum
gcloud auth application-default login
make db-up
make run-be                                                            # terminal 1 - backend  :8000
cp runtime/.env.example runtime/.env   && make runtime-install  && make run-runtime  # terminal 2 - runtime  :3001
cp frontend/.env.example frontend/.env && make frontend-install && make run-fe       # terminal 3 - frontend :5173 (opens the chat UI)
```

Open `http://localhost:5173`. All three (`run-be`/`run-runtime`/`run-fe`) need to be
running at once, each in its own terminal - `run-fe` alone won't talk to the agent.

## Project layout

```
src/
  agent/          deepagents graph: root agent, subagents, tools, middleware
  agent/api/      AG-UI/CopilotKit wrapper around the compiled graph
  app/            FastAPI app (AG-UI endpoint, admin routes, static charts)
  artifacts/      persona/subagent prompts + skills (frontmatter markdown)
  clients/        LLM + BigQuery clients (bq_client.py is the assignment's reference file, untouched)
  config/         env settings
  database/       Postgres pool / checkpointer / Store (pgvector-backed)
  safety/         SQL validator + BigQuery cost guard
frontend/         Vite + React + CopilotKit chat UI
runtime/          Node/Express CopilotKit runtime (bridges frontend <-> AG-UI backend)
docs/HLD.md       architecture + design doc (start here)
tests/            pytest, one file per module
```

## Development

```bash
make compile        # isort + ruff format + ruff check --fix
uv run pytest -q    # 60+ unit tests, no external services required
make probe-llm      # smoke test: a chat request through the LiteLLM proxy
make probe-bq       # smoke test: fetch schemas for the 4 required BigQuery tables
                     # requires `gcloud auth application-default login` first
```

Both `/code-review` and `/ponytail:ponytail-review` were run on this diff per
this repo's own `CLAUDE.md`; findings were applied inline as the code was written
rather than as a separate pass.
