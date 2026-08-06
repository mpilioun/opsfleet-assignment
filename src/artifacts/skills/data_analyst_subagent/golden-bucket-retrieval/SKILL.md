---
name: golden-bucket-retrieval
description: How to use search_golden_bucket before writing SQL from scratch
---

# Golden Bucket Retrieval

1. Before writing SQL for a non-trivial question, call `search_golden_bucket` with
   the user's question (in their own words, not a rephrased version).
2. If it returns a similar past example, use its SQL as a starting template and
   adapt the filters/columns to this question - don't just copy it verbatim if the
   entities or time range differ.
3. If it returns nothing, that's expected for novel questions - write the query
   yourself using `get_schema` to confirm column names first.
4. Never mention "the golden bucket" to the user - it's an internal knowledge
   source, not something they need to know about. Present the analysis, not its
   provenance.
