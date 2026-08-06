from langgraph.store.memory import InMemoryStore

from src.agent import persona


async def test_falls_back_to_default_when_store_empty():
    persona._cache.update({"text": None, "expires_at": 0.0})
    store = InMemoryStore()

    text = await persona.get_active_persona(store, "default persona text")

    assert text == "default persona text"


async def test_set_then_get_returns_live_override():
    persona._cache.update({"text": None, "expires_at": 0.0})
    store = InMemoryStore()

    await persona.set_active_persona(store, "new CEO-mandated tone")
    text = await persona.get_active_persona(store, "default persona text")

    assert text == "new CEO-mandated tone"


async def test_get_is_served_from_cache_without_hitting_store_again():
    persona._cache.update({"text": None, "expires_at": 0.0})
    store = InMemoryStore()
    await persona.set_active_persona(store, "cached tone")

    await store.aput(persona.PERSONA_NAMESPACE, persona.PERSONA_KEY, {"text": "changed underneath"})
    text = await persona.get_active_persona(store, "default")

    assert text == "cached tone"
