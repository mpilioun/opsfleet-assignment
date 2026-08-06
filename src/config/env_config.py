import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentType = Literal["local", "development", "staging", "production", "test"]


class EnvironmentConfig(BaseSettings):
    ENVIRONMENT: EnvironmentType = "local"
    LOG_LEVEL: str = "INFO"

    # Postgres (checkpointer / store backend)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    # Hardcoded default: POC/local-run convenience only, minimizes env setup for
    # running locally. Never rely on this default in a real production deployment -
    # set POSTGRES_PASSWORD via env/secret manager there.
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SCHEMA: str = "public"

    PG_MIN_POOL_SIZE: int = 1
    PG_MAX_POOL_SIZE: int = 10
    PG_TIMEOUT: float = 10.0

    # LiteLLM proxy (OpenAI-compatible endpoint for all chat LLM calls)
    LITELLM_BASE_URL: str = "http://localhost:4000"
    # Hardcoded default: POC/local-run convenience only, same reasoning as
    # POSTGRES_PASSWORD above. Not a real key - a real deployment sets its own.
    LITELLM_MASTER_KEY: str = "sk-litellm-master"
    LITELLM_MAX_RETRIES: int = 3

    # Google AI Studio (embeddings for the Store's semantic index - called directly,
    # not through LiteLLM, since embeddings are a distinct API from chat completions)
    GEMINI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    EMBEDDING_DIMS: int = 768
    OPENROUTER_API_KEY: str = ""

    # Langfuse
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"

    @property
    def is_test(self) -> bool:
        return self.ENVIRONMENT == "test"

    @property
    def postgres_conninfo(self) -> str:
        host = "127.0.0.1" if self.POSTGRES_HOST == "localhost" else self.POSTGRES_HOST
        password = (
            f"password={self.POSTGRES_PASSWORD} " if self.POSTGRES_PASSWORD else ""
        )
        return (
            f"dbname={self.POSTGRES_DB} "
            f"user={self.POSTGRES_USER} "
            f"{password}"
            f"host={host} "
            f"port={self.POSTGRES_PORT}"
        )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=(".env", f".env.{os.getenv('ENVIRONMENT', 'local')}"),
        extra="ignore",
    )


env_config = EnvironmentConfig()
