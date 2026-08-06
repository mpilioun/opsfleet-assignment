"""PostgreSQL connection pool and LangGraph persistence management."""

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from src.config.env_config import env_config

CONNECTION_KWARGS = {
    "autocommit": True,
    "prepare_threshold": 0,
    "row_factory": dict_row,
}


class PostgresManager:
    """Owns the async connection pool and hands out checkpointer/store instances."""

    def __init__(self):
        self._pool: AsyncConnectionPool | None = None
        self._schema_initialized: bool = False
        self._is_test_mode = env_config.is_test
        if not self._is_test_mode:
            self._pool = self._create_pool()

    def _create_pool(self) -> AsyncConnectionPool:
        async def set_schema(conn) -> None:
            await conn.execute(
                f'SET search_path TO "{env_config.POSTGRES_SCHEMA}", public'
            )

        return AsyncConnectionPool(
            conninfo=env_config.postgres_conninfo,
            max_size=env_config.PG_MAX_POOL_SIZE,
            min_size=env_config.PG_MIN_POOL_SIZE,
            kwargs=CONNECTION_KWARGS,
            configure=set_schema,
            open=False,
            timeout=env_config.PG_TIMEOUT,
        )

    async def initialize(self) -> None:
        """Open the pool and run checkpointer/store schema setup once. Call on startup."""
        if self._is_test_mode:
            return

        await self._pool.open()

        if not self._schema_initialized:
            await self.get_checkpointer().setup()
            await self.get_store().setup()
            self._schema_initialized = True

    async def close(self) -> None:
        if self._is_test_mode:
            return
        await self._pool.close()

    def get_pool_stats(self) -> dict:
        if self._is_test_mode:
            return {}
        return self._pool.get_stats()

    def get_checkpointer(self) -> AsyncPostgresSaver | None:
        """New checkpointer instance backed by the shared pool, or None in test mode."""
        if self._is_test_mode:
            return None
        return AsyncPostgresSaver(self._pool)

    def get_store(self) -> AsyncPostgresStore | None:
        """New store instance backed by the shared pool, or None in test mode."""
        if self._is_test_mode:
            return None
        return AsyncPostgresStore(self._pool)


postgres_manager = PostgresManager()
