"""Export Langfuse sessions to docs/conversation_results/*.yaml for manual QA review.

One-off/manual tool (ponytail: not part of the app or test suite) - pulls full
conversation transcripts (human/ai/tool messages, tool call args+results) straight
from Langfuse traces, since each trace's `output.messages` already holds the full
thread history up to that point. Run: `uv run python scripts/export_conversation_results.py`.
Requires LANGFUSE_PUBLIC_KEY/LANGFUSE_SECRET_KEY/LANGFUSE_BASE_URL (see .env.local).
"""

import re
import time
from pathlib import Path

import requests
import yaml

from src.config.env_config import env_config

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "conversation_results"
SINCE = "2026-08-07T06:00:00Z"  # cutoff: start of the manual TEST_CONVERSATIONS.md pass


def api_get(path: str, **params) -> dict:
    for attempt in range(8):
        resp = requests.get(
            f"{env_config.LANGFUSE_BASE_URL}/api/public/{path}",
            auth=(env_config.LANGFUSE_PUBLIC_KEY, env_config.LANGFUSE_SECRET_KEY),
            params=params,
            timeout=30,
        )
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 10 * (attempt + 1)))
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()


def list_sessions_since(since: str) -> list[dict]:
    sessions, page = [], 1
    while True:
        data = api_get("sessions", limit=50, page=page)
        sessions.extend(data["data"])
        if page >= data["meta"]["totalPages"]:
            break
        page += 1
    return [s for s in sessions if s["createdAt"] >= since]


def simplify_message(msg: dict) -> dict:
    out = {"role": msg.get("type"), "content": msg.get("content") or None}
    if msg.get("name") and msg["type"] == "tool":
        out["tool_name"] = msg["name"]
    if msg.get("tool_calls"):
        out["tool_calls"] = [
            {"name": tc["name"], "args": tc["args"]} for tc in msg["tool_calls"]
        ]
    return {k: v for k, v in out.items() if v not in (None, [], {})}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def export_session(session: dict) -> Path | None:
    detail = api_get(f"sessions/{session['id']}")
    traces = sorted(detail.get("traces", []), key=lambda t: t["timestamp"])
    if not traces:
        return None
    last = traces[-1]
    messages = (last.get("output") or {}).get("messages") or []
    if not messages:
        return None

    first_human = next((m["content"] for m in messages if m.get("type") == "human"), "conversation")
    record = {
        "session_id": session["id"],
        "started_at": session["createdAt"],
        "langfuse_session_url": (
            f"{env_config.LANGFUSE_BASE_URL}/project/{session['projectId']}"
            f"/sessions/{session['id']}"
        ),
        "turn_count": sum(1 for m in messages if m.get("type") == "human"),
        "transcript": [simplify_message(m) for m in messages],
    }

    filename = f"{session['createdAt'][:19].replace(':', '')}_{slug(first_human)}.yaml"
    out_path = OUT_DIR / filename
    out_path.write_text(yaml.dump(record, sort_keys=False, allow_unicode=True, width=100))
    return out_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sessions = list_sessions_since(SINCE)
    print(f"{len(sessions)} sessions since {SINCE}")
    already = {p.name.split("_", 1)[0] for p in OUT_DIR.glob("*.yaml")}
    written = 0
    for session in sessions:
        if session["createdAt"][:19].replace(":", "") in already:
            continue
        path = export_session(session)
        if path:
            written += 1
            print(f"  wrote {path.relative_to(OUT_DIR.parent.parent)}")
        else:
            print(f"  skipped {session['id']} (no messages)")
    print(f"{written} files written to {OUT_DIR}")


if __name__ == "__main__":
    main()
