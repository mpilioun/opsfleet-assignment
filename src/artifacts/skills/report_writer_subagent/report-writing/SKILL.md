---
name: report-writing
description: How to structure a report and verify it before returning it
---

# Report Writing

1. Structure: a short narrative summary of the finding, then the supporting numbers
   (table or bullets, per the user's known preference), then an "Action items"
   section when the user asked for a report (not for a quick follow-up question).
2. Only state numbers that came from a `run_sql`/analyst result actually provided to
   you in this conversation. Never invent or round in a way that changes the story.
3. Never include a customer's name, email, phone number, or street address, even if
   it appeared somewhere upstream - describe customers only by aggregate (state,
   segment, opaque id).
4. Before returning a final report (not a short conversational reply), call
   `verify_output` with the original question and your draft. If it flags issues,
   fix them and don't call `verify_output` more than twice for the same draft - on
   the second failure, present the report with a brief caveat instead of looping.
