---
name: chart-generation
description: When and how to use generate_chart
---

# Chart Generation

1. Offer a chart when the data is naturally time-series or a comparison across a
   handful of categories (e.g. monthly revenue, product A vs B) - not for single
   numbers or long lists.
2. Use `chart_type="line"` for trends over time, `"bar"` for comparisons across
   categories.
3. Pass the same aggregated, non-PII labels/values you'd put in a report table -
   never raw customer identifiers as labels.
4. Mention the saved file path in your response so the user knows where to find it.
