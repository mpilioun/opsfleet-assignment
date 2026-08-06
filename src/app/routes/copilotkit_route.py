"""Mounts the AG-UI agent endpoint plus a CopilotKit-compatible thread-state route
(for `loadAgentState`/reconnect), same shape as Revmark_AI's `copilotkit_route.py`.
"""

from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from langchain_core.runnables import ensure_config

from src.agent.api.ag_ui_agent_wrapper import (
    AGENT_NAME,
    AGENT_PATH,
    RetailInsightsAGUIAgent,
)
from src.app.helpers.langgraph_ag_ui_endpoint import (
    add_langgraph_fastapi_endpoint_with_factory,
)


def setup_copilotkit_endpoint(
    app: FastAPI, agent_factory: Callable[[], RetailInsightsAGUIAgent]
) -> None:
    add_langgraph_fastapi_endpoint_with_factory(
        app, agent_factory, AGENT_PATH, health_agent_name=AGENT_NAME
    )

    @app.get(f"{AGENT_PATH}/threads/{{thread_id}}/state")
    async def get_thread_state(thread_id: str, request: Request):
        agent = agent_factory()
        config = ensure_config(agent.config.copy() if agent.config else {})
        config["configurable"] = {
            **(config.get("configurable") or {}),
            "thread_id": thread_id,
        }

        try:
            snapshot = await agent.graph.aget_state(config)
        except Exception:  # noqa: BLE001 - a snapshot-read failure degrades to empty state, not a 500
            return JSONResponse(content={"values": {}})

        raw_values = getattr(snapshot, "values", None) if snapshot else None
        if not raw_values:
            return JSONResponse(content={"values": {}})

        allowed = frozenset(agent.constant_schema_keys)
        public_values = {}
        for key in allowed:
            if key not in raw_values:
                continue
            if key == "messages":
                public_values["messages"] = agent._filter_orphan_tool_messages(
                    raw_values["messages"]
                )
            else:
                public_values[key] = raw_values[key]

        response: dict = {"values": public_values}
        interrupts = [
            {
                "value": getattr(interrupt, "value", None),
                "resumable": getattr(interrupt, "resumable", False),
            }
            for task in (getattr(snapshot, "tasks", None) or [])
            for interrupt in (getattr(task, "interrupts", None) or [])
        ]
        if interrupts:
            response["tasks"] = [{"name": "agent", "interrupts": interrupts}]
        if getattr(snapshot, "next", None):
            response["next"] = list(snapshot.next)

        return JSONResponse(content=jsonable_encoder(response))
