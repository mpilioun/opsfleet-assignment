from types import SimpleNamespace

import pytest
from langchain_core.messages import ToolMessage
from langgraph.errors import GraphInterrupt

from src.agent.middlewares.tool_errors import tool_error_boundary

REQUEST = SimpleNamespace(tool_call={"name": "search_golden_bucket", "id": "call-1"})


async def _boundary(handler):
    return await tool_error_boundary.awrap_tool_call(REQUEST, handler)


async def test_passes_through_successful_tool_result():
    expected = ToolMessage(content="ok", tool_call_id="call-1")

    async def handler(request):
        return expected

    assert await _boundary(handler) is expected


async def test_lets_graph_interrupts_propagate():
    """Swallowing a GraphInterrupt would silently kill the HITL confirmation flow."""

    async def handler(request):
        raise GraphInterrupt(())

    with pytest.raises(GraphInterrupt):
        await _boundary(handler)


async def test_converts_tool_exception_into_error_tool_message():
    async def handler(request):
        raise RuntimeError("embeddings API unavailable")

    result = await _boundary(handler)

    assert isinstance(result, ToolMessage)
    assert result.status == "error"
    assert result.tool_call_id == "call-1"
    assert result.name == "search_golden_bucket"
    assert "embeddings API unavailable" in result.content
