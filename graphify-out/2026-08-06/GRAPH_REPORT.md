# Graph Report - opsfleet-assignment  (2026-08-06)

## Corpus Check
- 113 files · ~19,065 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 640 nodes · 994 edges · 60 communities (50 shown, 10 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2cd582b2`
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
- validate_and_prepare_sql
- generate_chart
- runtime/package.json
- dependencies
- compilerOptions
- langfuse.py
- persona_prompt
- Retail Insights Agent — High-Level Design
- index.ts
- golden_bucket_seeds.py
- agent-provider.tsx
- tool-card.tsx
- compilerOptions
- interrupt-utils.ts
- chart-renderer.tsx
- approval-card.tsx
- interrupt-context.tsx
- App.tsx
- InterruptActions
- retail_agent_persona.md
- golden-bucket-retrieval/SKILL.md
- sql-self-repair/SKILL.md
- chart-generation/SKILL.md
- report-writing/SKILL.md

## God Nodes (most connected - your core abstractions)
1. `validate_and_prepare_sql()` - 19 edges
2. `build_agent()` - 15 edges
3. `Retail Insights Agent — High-Level Design` - 15 edges
4. `get_logger()` - 14 edges
5. `compilerOptions` - 13 edges
6. `datetime_prompt()` - 12 edges
7. `list_reports()` - 12 edges
8. `run_structured()` - 12 edges
9. `BigQueryRunner` - 12 edges
10. `get_llm_model()` - 12 edges

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

## Communities (60 total, 10 thin omitted)

### Community 0 - "PostgresManager"
Cohesion: 0.13
Nodes (11): AsyncConnectionPool, AsyncPostgresSaver, AsyncPostgresStore, _build_store_index_config(), PostgresManager, PostgreSQL connection pool and LangGraph persistence management., Indexes the "question" field of golden-bucket trios and the "content" field of…, Owns the async connection pool and hands out checkpointer/store instances. (+3 more)

### Community 1 - "main.py"
Cohesion: 0.09
Nodes (24): get, LangGraphAgent, LangGraphAGUIAgent, post, build_ag_ui_agent(), CopilotKit/AG-UI integration for the retail insights agent - same pattern as…, Inject user_id/thread_id into configurable and attach Langfuse metadata., RetailInsightsAGUIAgent (+16 more)

### Community 2 - "logging.py"
Cohesion: 0.08
Nodes (46): Logger, delete_reports(), tool, ToolMessage, ToolRuntime, Permanently delete the given saved reports (by id, resolved via find_reports…, find_reports(), tool (+38 more)

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
Nodes (30): tool, ToolMessage, ToolRuntime, Search the golden bucket for past analyst-approved Question->SQL->Report…, search_golden_bucket(), add_candidate_trio(), ensure_seeded(), promote_to_golden() (+22 more)

### Community 13 - "agent.py"
Cohesion: 0.06
Nodes (48): BaseStore, before_agent, ChatOpenAI, CompositeBackend, main(), build_agent(), build_backend(), Ephemeral state by default; /memory/ persists per-user in the Store; /skills/… (+40 more)

### Community 21 - "eval_golden.py"
Cohesion: 0.10
Nodes (27): _final_report_text(), main(), Offline QA eval: replay each golden-bucket seed question through the live agent…, _run_one(), BaseModel, tool, ToolMessage, ToolRuntime (+19 more)

### Community 22 - "validate_and_prepare_sql"
Cohesion: 0.08
Nodes (43): Client, Exception, _count_recent_run_sql_failures(), tool, ToolMessage, ToolRuntime, Consecutive run_sql failures counting back from the latest message, reset by a…, Validate and execute a read-only SQL query against BigQuery (orders,… (+35 more)

### Community 23 - "generate_chart"
Cohesion: 0.20
Nodes (11): generate_chart(), tool, ToolMessage, ToolRuntime, Render a bar or line chart from labels/values and save it as a PNG. Example…, _cleanup_charts_dir(), _fake_runtime(), fixture (+3 more)

### Community 24 - "runtime/package.json"
Cohesion: 0.07
Nodes (28): @copilotkit/runtime, cors, dotenv, express, dependencies, @copilotkit/runtime, cors, dotenv (+20 more)

### Community 25 - "dependencies"
Cohesion: 0.05
Nodes (38): @copilotkit/react-core, @copilotkit/react-ui, @copilotkit/runtime-client-gql, @copilotkit/shared, dependencies, @copilotkit/react-core, @copilotkit/react-ui, @copilotkit/runtime-client-gql (+30 more)

### Community 26 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 27 - "langfuse.py"
Cohesion: 0.11
Nodes (18): BaseSettings, CallbackHandler, Langfuse, EnvironmentConfig, flush_langfuse(), get_langfuse_callback(), get_langfuse_client(), init_langfuse() (+10 more)

### Community 28 - "persona_prompt"
Cohesion: 0.14
Nodes (16): persona_prompt(), dynamic_prompt, ModelRequest, Prepend the live persona (Store, falling back to the artifact default) ahead of…, get_active_persona(), Any, Persona hot-reload (requirement 8: the CEO changes report tone weekly, without…, Updates the live override. If no Store is configured (e.g. test mode), degrades… (+8 more)

### Community 29 - "Retail Insights Agent — High-Level Design"
Cohesion: 0.12
Nodes (15): 0. Scope note: CLI → web UI, 10. Requirement 7 — Observability, 11. Requirement 8 — Agility (Persona Management), 12. Setup instructions, 13. Known gaps / what a production pass adds, 1. Architecture Diagram, 2. Component reasoning, 3. Data flow (typical question) (+7 more)

### Community 30 - "index.ts"
Cohesion: 0.19
Nodes (11): createCorsMiddleware(), AGENT_BACKEND_URL, AGENT_NAME, COPILOTKIT_BASE_PATH, COPILOTKIT_SERVER_PORT, CORS_ALLOWED_ORIGINS, projectRoot, srcDir (+3 more)

### Community 32 - "agent-provider.tsx"
Cohesion: 0.24
Nodes (9): AGENT_NAME, COPILOT_RUNTIME_URL, AgentContext, AgentContextValue, AgentProvider(), InterruptRenderer(), useInterruptState(), useThread() (+1 more)

### Community 33 - "tool-card.tsx"
Cohesion: 0.17
Nodes (6): RenderStatus, Tone, ToolCard, ToolCardContext, ToolCardContextValue, ToolCardVariant

### Community 34 - "compilerOptions"
Cohesion: 0.17
Nodes (11): compilerOptions, esModuleInterop, module, moduleResolution, noEmit, outDir, skipLibCheck, strict (+3 more)

### Community 35 - "interrupt-utils.ts"
Cohesion: 0.29
Nodes (10): AgentRegistrations(), ActionRequest, EMPTY_INTERRUPT, InterruptValue, isRecord(), normalize(), parseInterruptValue(), ReviewConfig (+2 more)

### Community 36 - "chart-renderer.tsx"
Cohesion: 0.29
Nodes (8): AGENT_BACKEND_URL, chartSchema, extractChartUrl(), useChartRenderer(), ArgsBlock(), isErrorResult(), KVRow(), MutedText()

### Community 37 - "approval-card.tsx"
Cohesion: 0.33
Nodes (6): ApprovalCard, ApprovalCardArgsSection(), ApprovalCardDefaultActions(), ApprovalCardRoot(), ApprovalCardToolRow(), useInterruptContext()

### Community 38 - "interrupt-context.tsx"
Cohesion: 0.22
Nodes (8): Decision, DecisionType, InterruptContext, InterruptContextValue, InterruptMeta, InterruptProvider(), InterruptState, ToolAction

### Community 39 - "App.tsx"
Cohesion: 0.39
Nodes (4): App(), getOrCreateUserId(), useAgentContext(), Chat()

### Community 41 - "retail_agent_persona.md"
Cohesion: 0.40
Nodes (4): Destructive actions, Style, What you do, What you refuse

## Knowledge Gaps
- **112 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+107 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `uuid` connect `logging.py` to `dependencies`, `eval_golden.py`, `test_golden_bucket.py`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `uuid` connect `dependencies` to `logging.py`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `build_agent()` (e.g. with `datetime_prompt()` and `scope_guard()`) actually correct?**
  _`build_agent()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _112 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `PostgresManager` be split into smaller, more focused modules?**
  _Cohesion score 0.1286549707602339 - nodes in this community are weakly interconnected._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09462365591397849 - nodes in this community are weakly interconnected._
- **Should `logging.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07656341320864991 - nodes in this community are weakly interconnected._