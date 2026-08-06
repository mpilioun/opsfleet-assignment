from langchain_openai import ChatOpenAI

from src.config.env_config import env_config


def get_llm_model(model: str, effort: str | None = None, **_kwargs) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        base_url=env_config.LITELLM_BASE_URL,
        api_key=env_config.LITELLM_MASTER_KEY,
        max_retries=env_config.LITELLM_MAX_RETRIES,
        reasoning_effort=effort,
    )
