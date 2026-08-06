# Graph Report - .  (2026-08-06)

## Corpus Check
- Corpus is ~526 words - fits in a single context window. You may not need a graph.

## Summary
- 45 nodes · 30 edges · 21 communities (16 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 44,755 output

## Community Hubs (Navigation)
- Postgres Connection Pool
- Env Config Settings
- LangGraph Checkpointer
- Docker Compose DB Stack
- LangGraph Store
- Post-Edit Review Process
- Conventional Commits Rule
- Make Compile Step
- Project Package (root)
- Project Root

## God Nodes (most connected - your core abstractions)
1. `PostgresManager` - 9 edges
2. `EnvironmentConfig` - 4 edges
3. `Mandatory Post-Edit Review Process` - 2 edges
4. `pg (Postgres service)` - 2 edges
5. `pgadmin (pgAdmin4 service)` - 2 edges
6. `PostgreSQL connection pool and LangGraph persistence management.` - 1 edges
7. `Owns the async connection pool and hands out checkpointer/store instances.` - 1 edges
8. `Open the pool and run checkpointer/store schema setup once. Call on startup.` - 1 edges
9. `New checkpointer instance backed by the shared pool, or None in test mode.` - 1 edges
10. `New store instance backed by the shared pool, or None in test mode.` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Post-Edit Workflow Steps** — claude_md_conventional_commits, claude_md_make_compile, claude_md_code_review_skill, claude_md_ponytail_review_skill [INFERRED 0.85]

## Communities (21 total, 5 thin omitted)

### Community 0 - "Postgres Connection Pool"
Cohesion: 0.33
Nodes (3): AsyncConnectionPool, PostgresManager, Owns the async connection pool and hands out checkpointer/store instances.

### Community 1 - "Env Config Settings"
Cohesion: 0.29
Nodes (3): BaseSettings, EnvironmentConfig, PostgreSQL connection pool and LangGraph persistence management.

### Community 2 - "LangGraph Checkpointer"
Cohesion: 0.40
Nodes (3): AsyncPostgresSaver, Open the pool and run checkpointer/store schema setup once. Call on startup., New checkpointer instance backed by the shared pool, or None in test mode.

### Community 3 - "Docker Compose DB Stack"
Cohesion: 0.50
Nodes (4): pg_data volume, pg (Postgres service), pgadmin_data volume, pgadmin (pgAdmin4 service)

### Community 5 - "Post-Edit Review Process"
Cohesion: 0.67
Nodes (3): /code-review skill, /ponytail:ponytail-review skill, Mandatory Post-Edit Review Process

## Knowledge Gaps
- **6 isolated node(s):** `opsfleet-assignment`, `/code-review skill`, `/ponytail:ponytail-review skill`, `opsfleet-assignment (project)`, `pg_data volume` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PostgresManager` connect `Postgres Connection Pool` to `Env Config Settings`, `LangGraph Checkpointer`, `LangGraph Store`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **What connects `opsfleet-assignment`, `/code-review skill`, `/ponytail:ponytail-review skill` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._