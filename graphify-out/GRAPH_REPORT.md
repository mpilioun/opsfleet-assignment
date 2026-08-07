# Graph Report - opsfleet-assignment  (2026-08-07)

## Corpus Check
- 130 files · ~53,232 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 758 nodes · 1213 edges · 58 communities (49 shown, 9 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 34 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cf9ae243`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PostgresManager
- main.py
- logging.py
- pg (Postgres service)
- BigQueryRunner
- Mandatory Post-Edit Review Process
- test_golden_bucket.py
- Conventional Commit Names Rule
- make compile (formatting step)
- opsfleet-assignment
- opsfleet-assignment (project)
- agent.py
- eval_golden.py
- test_run_sql.py
- generate_chart
- runtime/package.json
- dependencies
- compilerOptions
- Retail Insights Agent — Test Conversations
- persona.py
- Retail Insights Agent — High-Level Design
- index.ts
- test_guard.py
- agent-provider.tsx
- tool-card.tsx
- compilerOptions
- validate_and_prepare_sql
- Global Constraints
- FE chart rendering (native, no server-side images)
- retail_agent_persona.md
- golden-bucket-retrieval/SKILL.md
- sql-self-repair/SKILL.md
- chart-generation/SKILL.md
- report-writing/SKILL.md
- Conversation results

## God Nodes (most connected - your core abstractions)
1. `validate_and_prepare_sql()` - 20 edges
2. `Retail Insights Agent — Test Conversations` - 20 edges
3. `Retail Insights Agent — High-Level Design` - 17 edges
4. `build_agent()` - 16 edges
5. `get_logger()` - 16 edges
6. `compilerOptions` - 13 edges
7. `create_report()` - 13 edges
8. `datetime_prompt()` - 12 edges
9. `get_user_id()` - 12 edges
10. `list_reports()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `test_final_report_text_returns_empty_string_when_no_ai_message()` --calls--> `_final_report_text()`  [EXTRACTED]
  tests/test_eval_golden.py → scripts/eval_golden.py
- `test_final_report_text_returns_last_ai_message()` --calls--> `_final_report_text()`  [EXTRACTED]
  tests/test_eval_golden.py → scripts/eval_golden.py
- `test_final_report_text_skips_empty_ai_messages()` --calls--> `_final_report_text()`  [EXTRACTED]
  tests/test_eval_golden.py → scripts/eval_golden.py
- `main()` --calls--> `build_agent()`  [EXTRACTED]
  scripts/eval_golden.py → src/agent/agent.py
- `main()` --calls--> `BigQueryRunner`  [EXTRACTED]
  scripts/probe_bq.py → src/clients/bq_client.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Post-Edit Workflow Steps** — claude_md_conventional_commits, claude_md_make_compile, claude_md_code_review_skill, claude_md_ponytail_review_skill [INFERRED 0.85]

## Communities (58 total, 9 thin omitted)

### Community 0 - "PostgresManager"
Cohesion: 0.14
Nodes (10): AsyncConnectionPool, AsyncPostgresSaver, AsyncPostgresStore, _build_store_index_config(), PostgresManager, Indexes the "question" field of golden-bucket trios and the "content" field of…, Owns the async connection pool and hands out checkpointer/store instances., Open the pool and run checkpointer/store schema setup once. Call on startup. (+2 more)

### Community 1 - "main.py"
Cohesion: 0.05
Nodes (43): BaseSettings, CallbackHandler, get, Langfuse, LangGraphAgent, LangGraphAGUIAgent, post, build_ag_ui_agent() (+35 more)

### Community 2 - "logging.py"
Cohesion: 0.07
Nodes (56): Logger, delete_reports(), tool, ToolMessage, ToolRuntime, Permanently delete the given saved reports (by id, resolved via find_reports…, find_reports(), tool (+48 more)

### Community 3 - "pg (Postgres service)"
Cohesion: 0.50
Nodes (4): pg_data volume, pg (Postgres service), pgadmin_data volume, pgadmin (pgAdmin4 service)

### Community 4 - "BigQueryRunner"
Cohesion: 0.08
Nodes (30): DataFrame, main(), _format_table(), get_schema(), tool, ToolMessage, ToolRuntime, Returns (formatted section, ok). A failure is reported inline rather than… (+22 more)

### Community 5 - "Mandatory Post-Edit Review Process"
Cohesion: 0.67
Nodes (3): /code-review skill, /ponytail:ponytail-review skill, Mandatory Post-Edit Review Process

### Community 6 - "test_golden_bucket.py"
Cohesion: 0.10
Nodes (31): tool, ToolMessage, ToolRuntime, Search the golden bucket for past analyst-approved Question->SQL->Report…, search_golden_bucket(), add_candidate_trio(), ensure_seeded(), promote_to_golden() (+23 more)

### Community 13 - "agent.py"
Cohesion: 0.06
Nodes (47): BaseStore, ChatOpenAI, CompositeBackend, main(), build_agent(), build_backend(), Ephemeral state by default; /memory/ persists per-user in the Store; /skills/…, datetime_prompt() (+39 more)

### Community 21 - "eval_golden.py"
Cohesion: 0.10
Nodes (27): _final_report_text(), main(), Offline QA eval: replay each golden-bucket seed question through the live agent…, _run_one(), BaseModel, tool, ToolMessage, ToolRuntime (+19 more)

### Community 22 - "test_run_sql.py"
Cohesion: 0.12
Nodes (27): Client, Exception, _count_recent_run_sql_failures(), tool, ToolMessage, ToolRuntime, Consecutive run_sql failures counting back from the latest message, reset by a…, Validate and execute a read-only SQL query against BigQuery (orders,… (+19 more)

### Community 23 - "generate_chart"
Cohesion: 0.13
Nodes (20): ChartType, generate_chart(), tool, ToolMessage, ToolRuntime, Attach a chart to the report. chart_type picks the shape (line, bar, pie,…, ChartArtifact, ChartSeries (+12 more)

### Community 24 - "runtime/package.json"
Cohesion: 0.07
Nodes (28): @copilotkit/runtime, cors, dotenv, express, dependencies, @copilotkit/runtime, cors, dotenv (+20 more)

### Community 25 - "dependencies"
Cohesion: 0.05
Nodes (39): @copilotkit/react-core, @copilotkit/react-ui, @copilotkit/runtime-client-gql, @copilotkit/shared, dependencies, @copilotkit/react-core, @copilotkit/react-ui, @copilotkit/runtime-client-gql (+31 more)

### Community 26 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 27 - "Retail Insights Agent — Test Conversations"
Cohesion: 0.10
Nodes (20): 10. PII middleware — output-side redaction (`pii.py`), 11. Human-in-the-loop approval — `delete_reports`, 12. Report lifecycle edge cases, 13. Chart generation edge cases (`generate_chart`, `verify_output`), 14. Golden bucket / semantic lookup (`search_golden_bucket`), 15. Malformed / adversarial input, 16. Ambiguous / underspecified requests, 17. Concurrency / session isolation (if testable via two clients) (+12 more)

### Community 28 - "persona.py"
Cohesion: 0.18
Nodes (12): get_active_persona(), Any, Persona hot-reload (requirement 8: the CEO changes report tone weekly, without…, Updates the live override. If no Store is configured (e.g. test mode), degrades…, set_active_persona(), _fake_request(), ModelRequest, test_persona_alone_when_no_other_content() (+4 more)

### Community 29 - "Retail Insights Agent — High-Level Design"
Cohesion: 0.10
Nodes (20): 0. Scope note: CLI → web UI, 10. Requirement 7 — Observability, 11. Requirement 8 — Agility (Persona Management), 12. Setup instructions, 13. Known gaps / what a production pass adds, 1. Architecture Diagram, 2. Component reasoning, 3. Data flow (typical question) (+12 more)

### Community 30 - "index.ts"
Cohesion: 0.19
Nodes (11): createCorsMiddleware(), AGENT_BACKEND_URL, AGENT_NAME, COPILOTKIT_BASE_PATH, COPILOTKIT_SERVER_PORT, CORS_ALLOWED_ORIGINS, projectRoot, srcDir (+3 more)

### Community 31 - "test_guard.py"
Cohesion: 0.20
Nodes (16): before_agent, _classifier_input(), BaseModel, Scope/safety guard (requirement 2, "safeguarded against malicious users"): a…, The latest user message, plus the assistant turn it replies to. Without that…, scope_guard(), ScopeResult, patch (+8 more)

### Community 32 - "agent-provider.tsx"
Cohesion: 0.06
Nodes (33): App(), getOrCreateUserId(), AGENT_BACKEND_URL, AGENT_NAME, COPILOT_RUNTIME_URL, AgentContext, AgentContextValue, AgentProvider() (+25 more)

### Community 33 - "tool-card.tsx"
Cohesion: 0.08
Nodes (36): ApprovalCard, ApprovalCardArgsSection(), ApprovalCardDefaultActions(), ApprovalCardRoot(), ApprovalCardToolRow(), useInterruptContext(), RenderStatus, Tone (+28 more)

### Community 34 - "compilerOptions"
Cohesion: 0.12
Nodes (19): Path, compilerOptions, esModuleInterop, module, moduleResolution, noEmit, outDir, skipLibCheck (+11 more)

### Community 35 - "validate_and_prepare_sql"
Cohesion: 0.18
Nodes (19): Parse, validate, and row-cap a model-generated SQL string. Raises SqlGuardError…, SqlGuardError, validate_and_prepare_sql(), user_geom encodes the same exact location as latitude/longitude - must be…, test_cte_alias_is_not_treated_as_a_table(), test_cte_body_still_validates_table_whitelist(), test_direct_pii_column_is_blocked(), test_disallowed_table_is_blocked() (+11 more)

### Community 39 - "Global Constraints"
Cohesion: 0.20
Nodes (9): FE Chart Rendering Implementation Plan, Global Constraints, Task 1: Chart artifact pydantic model, Task 2: Rewrite `generate_chart` as a validation-only tool, Task 3: Backend cleanup — drop matplotlib, the `/charts` static mount, and `chart_path`, Task 4: Frontend chart deps + `ChartArtifact` type, Task 5: Port the Plotly transform map, Task 6: Rewrite the chart tool-call renderer (+1 more)

### Community 40 - "FE chart rendering (native, no server-side images)"
Cohesion: 0.25
Nodes (7): Backend changes, Context, Decisions, FE chart rendering (native, no server-side images), Frontend changes, Out of scope (this spec), Testing

### Community 41 - "retail_agent_persona.md"
Cohesion: 0.40
Nodes (4): Destructive actions, Style, What you do, What you refuse

## Knowledge Gaps
- **158 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+153 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `uuid` connect `dependencies` to `logging.py`, `eval_golden.py`, `test_golden_bucket.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `build_agent()` (e.g. with `datetime_prompt()` and `scope_guard()`) actually correct?**
  _`build_agent()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _158 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `PostgresManager` be split into smaller, more focused modules?**
  _Cohesion score 0.13970588235294118 - nodes in this community are weakly interconnected._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05194805194805195 - nodes in this community are weakly interconnected._
- **Should `logging.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06820119352088662 - nodes in this community are weakly interconnected._
- **Should `BigQueryRunner` be split into smaller, more focused modules?**
  _Cohesion score 0.07948717948717948 - nodes in this community are weakly interconnected._