"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config.env_config import env_config
from src.observability.logging import setup_logging

setup_logging()

from src.agent.api.ag_ui_agent_wrapper import build_ag_ui_agent
from src.agent.utils import golden_bucket, persona
from src.app.routes.copilotkit_route import setup_copilotkit_endpoint
from src.database.postgres_manager import postgres_manager

CHARTS_DIR = Path("charts")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await postgres_manager.initialize()
    store = postgres_manager.get_store()
    if store is not None:
        await golden_bucket.ensure_seeded(store)

    setup_copilotkit_endpoint(app, agent_factory=build_ag_ui_agent)

    yield

    await postgres_manager.close()


app = FastAPI(title="Retail Insights Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"]
    if env_config.ENVIRONMENT == "local"
    else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHARTS_DIR.mkdir(exist_ok=True)
app.mount("/charts", StaticFiles(directory=str(CHARTS_DIR)), name="charts")


@app.get("/")
async def root():
    return {
        "message": "Retail Insights Agent API",
        "environment": env_config.ENVIRONMENT,
    }


class SetPersonaRequest(BaseModel):
    text: str


@app.post("/admin/persona")
async def set_persona(body: SetPersonaRequest):
    """Requirement 8: a non-developer updates the report tone without a redeploy.
    NOTE: unauthenticated here for the prototype - a production deployment must
    gate this behind an admin role, not leave it open.
    """
    store = postgres_manager.get_store()
    await persona.set_active_persona(store, body.text)
    return {"status": "ok"}


def main():
    import uvicorn

    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=env_config.ENVIRONMENT == "local",
    )


if __name__ == "__main__":
    main()
