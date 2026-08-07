from google.cloud import bigquery

from src.clients.bq_client import BQ_TIMEOUT_SECONDS

# 500 MB per query keeps a chat session comfortably inside BigQuery's 1 TB/month free tier.
DEFAULT_MAX_BYTES_BILLED = 500_000_000


class QueryTooExpensiveError(Exception):
    """Raised when a query's dry-run byte estimate exceeds the configured cap."""


def check_query_cost(
    client: bigquery.Client,
    sql_query: str,
    max_bytes_billed: int = DEFAULT_MAX_BYTES_BILLED,
) -> int:
    """Dry-run a query to estimate bytes processed, without executing it.

    Returns the estimated byte count. Raises QueryTooExpensiveError if it
    exceeds max_bytes_billed, so the caller can reject the query before it
    ever reaches BigQueryRunner.execute_query.
    """
    dry_run_job = client.query(
        sql_query,
        job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False),
        timeout=BQ_TIMEOUT_SECONDS,
    )
    estimated_bytes = dry_run_job.total_bytes_processed
    if estimated_bytes > max_bytes_billed:
        raise QueryTooExpensiveError(
            f"Query would process {estimated_bytes / 1e9:.2f} GB, exceeding the "
            f"{max_bytes_billed / 1e9:.2f} GB cap. Narrow the query (add filters, "
            "aggregate, or reduce the date range) and try again."
        )
    return estimated_bytes
