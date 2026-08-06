import pytest

from src.safety.sql_guard import MAX_ROW_LIMIT, SqlGuardError, validate_and_prepare_sql


def test_simple_select_gets_limit_appended():
    sql = validate_and_prepare_sql("SELECT id, sale_price FROM order_items")
    assert f"LIMIT {MAX_ROW_LIMIT}" in sql


def test_select_star_on_non_users_table_is_allowed():
    sql = validate_and_prepare_sql("SELECT * FROM products")
    assert "products" in sql.lower()


def test_select_star_on_users_is_blocked():
    with pytest.raises(SqlGuardError, match="SELECT \\*"):
        validate_and_prepare_sql("SELECT * FROM users")


def test_direct_pii_column_is_blocked():
    with pytest.raises(SqlGuardError, match="email"):
        validate_and_prepare_sql("SELECT email FROM users")


def test_pii_column_blocked_even_inside_aggregate():
    with pytest.raises(SqlGuardError, match="street_address"):
        validate_and_prepare_sql("SELECT COUNT(street_address) FROM users")


def test_non_pii_users_columns_are_allowed():
    sql = validate_and_prepare_sql("SELECT state, COUNT(*) FROM users GROUP BY state")
    assert "state" in sql.lower()


def test_multiple_statements_are_blocked():
    with pytest.raises(SqlGuardError, match="single SELECT"):
        validate_and_prepare_sql("SELECT 1; DROP TABLE users;")


def test_write_statement_is_blocked():
    with pytest.raises(SqlGuardError, match="read-only"):
        validate_and_prepare_sql("DELETE FROM orders WHERE order_id = 1")


def test_disallowed_table_is_blocked():
    with pytest.raises(SqlGuardError, match="disallowed table"):
        validate_and_prepare_sql("SELECT * FROM some_other_dataset.secrets")


def test_existing_limit_is_capped():
    sql = validate_and_prepare_sql("SELECT id FROM products LIMIT 999999")
    assert f"LIMIT {MAX_ROW_LIMIT}" in sql
    assert "999999" not in sql


def test_existing_limit_under_cap_is_preserved():
    sql = validate_and_prepare_sql("SELECT id FROM products LIMIT 5")
    assert "LIMIT 5" in sql


def test_cte_alias_is_not_treated_as_a_table():
    sql = validate_and_prepare_sql(
        "WITH recent AS (SELECT id FROM orders) SELECT id FROM recent"
    )
    assert "recent" in sql.lower()


def test_cte_body_still_validates_table_whitelist():
    with pytest.raises(SqlGuardError, match="disallowed table"):
        validate_and_prepare_sql(
            "WITH leaked AS (SELECT * FROM some_other_dataset.secrets) SELECT * FROM leaked"
        )
