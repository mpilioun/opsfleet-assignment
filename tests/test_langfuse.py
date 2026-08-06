import importlib
from unittest.mock import patch

from src.config.env_config import env_config


def _reload_with_keys(secret_key: str, public_key: str):
    with (
        patch.object(env_config, "LANGFUSE_SECRET_KEY", secret_key),
        patch.object(env_config, "LANGFUSE_PUBLIC_KEY", public_key),
        patch("langfuse.Langfuse") as mock_langfuse_cls,
    ):
        module = importlib.import_module("src.observability.langfuse")
        module = importlib.reload(module)
        return module, mock_langfuse_cls


def test_no_client_without_credentials():
    module, mock_langfuse_cls = _reload_with_keys("", "")

    assert module.get_langfuse_client() is None
    assert module.get_langfuse_callback() is None
    mock_langfuse_cls.assert_not_called()


def test_client_initialized_with_credentials():
    module, mock_langfuse_cls = _reload_with_keys("secret", "public")

    assert module.get_langfuse_client() is mock_langfuse_cls.return_value
    mock_langfuse_cls.assert_called_once_with(
        public_key="public",
        secret_key="secret",
        base_url=module.env_config.LANGFUSE_BASE_URL,
        environment=module.env_config.ENVIRONMENT,
    )
