ALways use conventional commit names

always run make compile for formatting at the end of you code changes



## After editing code — always review

Whenever you finish editing code, before considering the task done, run both review
skills on the diff and act on what they find:

1. **`/code-review`** — evaluates the diff for correctness/bugs.
2. **`/ponytail:ponytail-review`** — evaluates the diff for over-engineering / simplification.

Apply the fixes, simplifications, and refactors they surface (skip only findings you can
justify skipping, and say why). This is mandatory for any code change, not optional cleanup.
