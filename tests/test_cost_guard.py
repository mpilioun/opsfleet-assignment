from unittest.mock import MagicMock

import pytest

from src.safety.cost_guard import QueryTooExpensiveError, check_query_cost


def test_query_under_cap_returns_estimate():
    client = MagicMock()
    client.query.return_value = MagicMock(total_bytes_processed=1_000)

    estimated = check_query_cost(client, "SELECT 1", max_bytes_billed=500_000_000)

    assert estimated == 1_000
    client.query.assert_called_once()


def test_query_over_cap_is_rejected_without_running():
    client = MagicMock()
    client.query.return_value = MagicMock(total_bytes_processed=10_000_000_000)

    with pytest.raises(QueryTooExpensiveError):
        check_query_cost(client, "SELECT 1", max_bytes_billed=500_000_000)

    client.query.assert_called_once()
