ALways use conventional commit names

always run make compile for formatting at the end of you code changes



## After editing code — always review

Whenever you finish editing code, before considering the task done, run both review
skills on the diff and act on what they find:

1. **`/code-review`** — evaluates the diff for correctness/bugs.
2. **`/ponytail:ponytail-review`** — evaluates the diff for over-engineering / simplification.

Apply the fixes, simplifications, and refactors they surface (skip only findings you can
justify skipping, and say why). This is mandatory for any code change, not optional cleanup.


## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
