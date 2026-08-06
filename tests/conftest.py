import os

# Must run before anything imports src.config.env_config, so external
# dependencies (Postgres pool, Gemini embeddings client) stay inert in tests.
os.environ.setdefault("ENVIRONMENT", "test")
