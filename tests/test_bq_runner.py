from unittest.mock import patch

from src.agent.tools import _bq_runner


@patch("src.agent.tools._bq_runner.BigQueryRunner")
def test_get_runner_is_a_lazy_singleton(mock_runner_cls):
    _bq_runner._runner = None

    first = _bq_runner.get_runner()
    second = _bq_runner.get_runner()

    assert first is second
    mock_runner_cls.assert_called_once()
