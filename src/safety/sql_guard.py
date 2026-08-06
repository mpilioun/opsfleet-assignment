import sqlglot
from sqlglot import exp

ALLOWED_TABLES = {"orders", "order_items", "products", "users"}

# Flat set: safe only because none of these names collide with a column on any
# other whitelisted table. Never displayed in a report, so blocked outright
# rather than trusted to aggregate away.
PII_BLOCKED_COLUMNS = {
    "first_name",
    "last_name",
    "email",
    "street_address",
    "postal_code",
    "latitude",
    "longitude",
    # GEOGRAPHY point built from latitude/longitude - same precise location, just
    # a different encoding. Selecting it bypasses the lat/long block outright.
    "user_geom",
}

MAX_ROW_LIMIT = 1000
DIALECT = "bigquery"


class SqlGuardError(ValueError):
    pass


def validate_and_prepare_sql(sql: str) -> str:
    """Parse, validate, and row-cap a model-generated SQL string.

    Raises SqlGuardError on anything unsafe (write ops, disallowed tables,
    PII columns). Returns a rewritten SQL string with the row limit capped.
    """
    statements = [s for s in sqlglot.parse(sql, dialect=DIALECT) if s is not None]
    if len(statements) != 1:
        raise SqlGuardError("Only a single SELECT statement is allowed per query.")

    stmt = statements[0]
    if not isinstance(stmt, exp.Select):
        raise SqlGuardError("Only read-only SELECT statements are allowed.")

    with_clause = stmt.args.get("with_")
    cte_aliases = (
        {cte.alias_or_name.lower() for cte in with_clause.expressions}
        if with_clause
        else set()
    )

    tables = {t.name.lower() for t in stmt.find_all(exp.Table)} - cte_aliases
    disallowed = tables - ALLOWED_TABLES
    if disallowed:
        raise SqlGuardError(
            f"Query references disallowed table(s): {', '.join(sorted(disallowed))}."
        )

    def _is_star_projection(proj: exp.Expression) -> bool:
        return isinstance(proj, exp.Star) or (
            isinstance(proj, exp.Column) and isinstance(proj.this, exp.Star)
        )

    if "users" in tables and any(
        _is_star_projection(proj) for proj in stmt.expressions
    ):
        raise SqlGuardError(
            "SELECT * is not allowed on the users table; list columns explicitly."
        )

    blocked_hits = {
        col.name.lower()
        for proj in stmt.expressions
        for col in proj.find_all(exp.Column)
        if col.name.lower() in PII_BLOCKED_COLUMNS
    }
    if blocked_hits:
        raise SqlGuardError(
            f"Query selects PII column(s) that must never be returned: {', '.join(sorted(blocked_hits))}. "
            "Aggregate or drop these columns (e.g. use state/city instead)."
        )

    existing_limit = stmt.args.get("limit")
    capped = MAX_ROW_LIMIT
    if existing_limit is not None:
        try:
            capped = min(int(existing_limit.expression.name), MAX_ROW_LIMIT)
        except (AttributeError, ValueError, TypeError):
            capped = MAX_ROW_LIMIT
    stmt = stmt.limit(capped)

    return stmt.sql(dialect=DIALECT)
