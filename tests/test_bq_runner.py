from unittest.mock import patch

from src.utils import bq_runner


@patch("src.utils.bq_runner.BigQueryRunner")
def test_get_runner_is_a_lazy_singleton(mock_runner_cls):
    bq_runner._runner = None

    first = bq_runner.get_runner()
    second = bq_runner.get_runner()

    assert first is second
    mock_runner_cls.assert_called_once()
