# Conversation results

Full conversation transcripts (every human/ai/tool message, tool call args, tool outputs)
pulled straight from Langfuse traces via `scripts/export_conversation_results.py` — each
trace's `output.messages` already holds the complete thread history, so no manual
transcription. Regenerate after a new test pass with:

```
uv run python scripts/export_conversation_results.py
```

Each YAML has `session_id`, `langfuse_session_url` (click through for the full trace —
tool latencies, token usage, model), `turn_count`, and `transcript`.

## Index — maps to `docs/TEST_CONVERSATIONS.md` sections

| File | TEST_CONVERSATIONS.md section(s) |
|---|---|
| `...070840_what-were-our-top-5...yaml`, `...073722_...yaml` | pre-pass smoke checks (chart/report golden path, dev) |
| `...091845_show-me-total-sales...yaml` | ad hoc smoke test (chart request, pre-section-3) |
| `...092652_what-are-the-top-5-product-categories...yaml` | ad hoc smoke test (inventory question) |
| `...092941_write-me-a-poem...yaml` | §3 scope guard — out-of-scope, §4 PII-fishing, §5 prompt-injection |
| `...093528_query-the-information-schema...yaml` | §6 SQL guard — disallowed tables/write ops |
| `...094147_list-every-single-order...yaml` | §8 row-limit capping, §9 cost-guard rejection |
| `...094630_if-a-customer-emailed...yaml` | §10 PII middleware output redaction |
| `...094901_save-a-report-titled-q1...yaml` | §11 HITL delete approval, §12 report lifecycle edge cases |
| `...101322_find-my-saved-reports...yaml` | §13 chart edge cases, §14 golden bucket, §15 malformed/adversarial input, §16 ambiguous requests |
| `...103400_how-are-we-doing...yaml` | §16 ambiguous requests (cont.) |
| `...103552_who-are-you...yaml` | §18 persona/tone consistency |
| `...103735_what-tables-and-columns...yaml` | §1 golden path (schema discovery) |
| `...104152_show-me-total-orders...yaml`, `...105227_...yaml` | §1 golden path (report+save+find), §2 multi-turn context/memory |

§17 (concurrency/session isolation) was not exercised — needs two separate browser
sessions, not attempted in this pass. Findings/bugs from reviewing these transcripts
are written up in `.claude` memory (`opsfleet-agent-test-findings`) — see chat history
or ask for a summary.
