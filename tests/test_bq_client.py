from unittest.mock import MagicMock, patch

import pandas as pd

from src.clients.bq_client import BQ_TIMEOUT_SECONDS, BigQueryRunner


@patch("src.clients.bq_client.bigquery.Client")
def test_execute_query_returns_dataframe(mock_client_cls):
    mock_client = MagicMock()
    mock_client.query.return_value.result.return_value.to_dataframe.return_value = (
        pd.DataFrame({"a": [1, 2]})
    )
    mock_client_cls.return_value = mock_client

    runner = BigQueryRunner(project_id="test-project")
    df = runner.execute_query("SELECT 1")

    assert list(df["a"]) == [1, 2]
    # Both bounds matter: job_timeout_ms cancels the job server-side, result(timeout)
    # stops the request hanging a chat turn.
    job_config = mock_client.query.call_args.kwargs["job_config"]
    assert int(job_config.job_timeout_ms) == int(BQ_TIMEOUT_SECONDS * 1000)
    assert (
        mock_client.query.return_value.result.call_args.kwargs["timeout"]
        == BQ_TIMEOUT_SECONDS
    )


@patch("src.clients.bq_client.bigquery.Client")
def test_get_table_schema_maps_fields(mock_client_cls):
    mock_field = MagicMock(name="id", field_type="INTEGER", mode="NULLABLE", description=None)
    mock_field.name = "id"
    mock_table = MagicMock(schema=[mock_field])
    mock_client = MagicMock()
    mock_client.get_table.return_value = mock_table
    mock_client_cls.return_value = mock_client

    runner = BigQueryRunner(project_id="test-project")
    schema = runner.get_table_schema("orders")

    assert schema == [
        {"name": "id", "type": "INTEGER", "mode": "NULLABLE", "description": ""}
    ]
