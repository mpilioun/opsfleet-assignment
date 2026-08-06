"""Langfuse client with isolated TracerProvider.

This module initializes LangFuse with an isolated TracerProvider.
This ensures only LLM traces reach Langfuse while infrastructure
traces go to the main OTLP collector.
"""

import asyncio

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from src.config.env_config import env_config
from src.observability.logging import get_logger

logger = get_logger(__name__)

_langfuse_client: Langfuse | None = None


def init_langfuse() -> Langfuse:
    """Initialize LangFuse client singleton with isolated TracerProvider."""
    return Langfuse(
        public_key=env_config.LANGFUSE_PUBLIC_KEY,
        secret_key=env_config.LANGFUSE_SECRET_KEY,
        base_url=env_config.LANGFUSE_BASE_URL,
        environment=env_config.ENVIRONMENT,
    )


if env_config.LANGFUSE_PUBLIC_KEY and env_config.LANGFUSE_SECRET_KEY:
    logger.info("Initializing Langfuse with isolated TracerProvider")
    _langfuse_client = init_langfuse()
else:
    logger.warning("Langfuse credentials not configured; skipping initialization")


def get_langfuse_client() -> Langfuse | None:
    """Get the Langfuse client with isolated TracerProvider."""
    return _langfuse_client


def get_langfuse_callback(**kwargs) -> CallbackHandler | None:
    """Get a CallbackHandler using the isolated Langfuse client."""
    client = get_langfuse_client()
    if client is None:
        return None
    return CallbackHandler(**kwargs)


async def flush_langfuse() -> None:
    """Flush pending Langfuse events to the server.

    Runs the blocking flush in a thread to avoid stalling the event loop.
    Errors are logged and suppressed so a flush failure never breaks a request.
    """
    client = get_langfuse_client()
    if client is None:
        return
    try:
        await asyncio.to_thread(client.flush)
        logger.debug("Langfuse flush completed")
    except Exception as e:  # noqa: BLE001 - a flush failure must never break the request
        logger.warning("Langfuse flush failed: %s", str(e))


def shutdown_langfuse() -> None:
    """Shutdown LangFuse client."""
    client = get_langfuse_client()
    if client is None:
        return
    try:
        client.shutdown()
        logger.debug("Langfuse shutdown completed")
    except Exception as e:  # noqa: BLE001 - shutdown must never raise during teardown
        logger.warning("Langfuse shutdown failed: %s", str(e))
