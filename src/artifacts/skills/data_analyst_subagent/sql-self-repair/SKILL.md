---
name: sql-self-repair
description: How to recover from a failed or empty run_sql call instead of giving up or repeating the same query
---

# SQL Self-Repair

When `run_sql` returns `status="error"`:

1. Read the error message - it already tells you what to fix (rejected PII column,
   disallowed table, BigQuery syntax error, cost cap exceeded, or empty result).
2. Fix the specific issue named in the error and retry with a corrected query. Don't
   change unrelated parts of the query.
3. If the error says the self-repair limit was reached, **stop calling `run_sql`**.
   Explain plainly to the user what you tried, why it didn't work, and what
   additional information (e.g. a narrower date range, a specific product name)
   would let you try again. Never fabricate numbers to fill the gap.
4. An empty result is not automatically a bug - if a second differently-filtered
   attempt also comes back empty, say so; don't keep guessing filters forever.
