"""Root logging config for the app. `setup_logging()` runs once, at process
start (`src/app/main.py`); every module then gets its logger via `get_logger`.
"""

import logging

from src.config.env_config import env_config

_configured = False


def setup_logging() -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(
        level=env_config.LOG_LEVEL,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
