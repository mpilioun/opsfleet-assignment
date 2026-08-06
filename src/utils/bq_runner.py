from src.clients.bq_client import BigQueryRunner

_runner: BigQueryRunner | None = None


def get_runner() -> BigQueryRunner:
    global _runner
    if _runner is None:
        _runner = BigQueryRunner()
    return _runner
