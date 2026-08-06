"""Persona hot-reload (requirement 8: the CEO changes report tone weekly, without
a redeploy). The artifact file (`retail_agent_persona.md`) is the versioned default
- editing it needs a deploy. The Store row is the live override - a non-developer
overwrites it (see the admin endpoint in the FastAPI app) and every process picks it
up within _CACHE_TTL_SECONDS, no restart needed.
"""

import time
from typing import Any

PERSONA_NAMESPACE = ("system", "persona")
PERSONA_KEY = "active"
_CACHE_TTL_SECONDS = 60.0

_cache: dict[str, Any] = {"text": None, "expires_at": 0.0}


async def get_active_persona(store: Any | None, default_text: str) -> str:
    now = time.monotonic()
    if _cache["text"] is not None and now < _cache["expires_at"]:
        return _cache["text"]

    text = default_text
    if store is not None:
        item = await store.aget(PERSONA_NAMESPACE, PERSONA_KEY)
        text = item.value["text"] if item is not None else default_text
    _cache["text"] = text
    _cache["expires_at"] = now + _CACHE_TTL_SECONDS
    return text


async def set_active_persona(store: Any | None, text: str) -> None:
    """Updates the live override. If no Store is configured (e.g. test mode),
    degrades to in-process-only (no crash, just no cross-process persistence).
    """
    if store is not None:
        await store.aput(PERSONA_NAMESPACE, PERSONA_KEY, {"text": text})
    _cache["text"] = text
    _cache["expires_at"] = time.monotonic() + _CACHE_TTL_SECONDS
