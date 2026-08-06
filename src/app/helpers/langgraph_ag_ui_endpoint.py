"""Generic AG-UI-over-FastAPI mounting helper - same shape as Revmark_AI's
`app/helpers/langgraph_ag_ui_endpoint.py`, no auth-header plumbing (nothing here
is Revmark-specific).
"""

from collections.abc import Callable

from ag_ui.core.types import RunAgentInput
from ag_ui.encoder import EventEncoder
from ag_ui_langgraph.agent import LangGraphAgent
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse


def add_langgraph_fastapi_endpoint_with_factory(
    app: FastAPI,
    agent_factory: Callable[[], LangGraphAgent],
    path: str = "/",
    *,
    health_agent_name: str | None = None,
) -> None:
    """Register POST `path` and GET `path/health` for a LangGraph AG-UI agent."""
    resolved_health_name = health_agent_name or agent_factory().name

    @app.post(path)
    async def langgraph_agent_endpoint(
        input_data: RunAgentInput, request: Request
    ) -> StreamingResponse:
        accept_header = request.headers.get("accept")
        encoder = EventEncoder(accept=accept_header)
        agent = agent_factory()

        async def event_generator():
            async for event in agent.run(input_data):
                yield encoder.encode(event)

        return StreamingResponse(
            event_generator(), media_type=encoder.get_content_type()
        )

    @app.get(f"{path}/health")
    def health() -> dict:
        return {"status": "ok", "agent": {"name": resolved_health_name}}
