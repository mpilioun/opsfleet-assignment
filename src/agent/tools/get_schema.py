from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from src.observability.logging import get_logger
from src.safety.sql_guard import ALLOWED_TABLES, PII_BLOCKED_COLUMNS
from src.utils.bq_runner import get_runner

logger = get_logger(__name__)

# Static because the join graph of a fixed 4-table public dataset doesn't change,
# and BigQuery exposes no foreign keys to derive it from. Without this the model
# invents join keys (e.g. users.user_id) when answering structure questions.
RELATIONSHIPS = """Relationships:
- order_items.order_id -> orders.order_id (one order has many items)
- order_items.product_id -> products.id
- order_items.user_id -> users.id (orders.user_id -> users.id too)

Notes:
- Revenue lives on order_items.sale_price (per unit sold); orders has no amount
  column - join to order_items to get money.
- orders.status / order_items.status carry Cancelled/Returned/Complete, and
  returned_at/shipped_at/delivered_at support fulfilment and return analysis.
- Customers can be analysed by users.state/city/country/age/gender/traffic_source
  - never by the PII columns marked above."""


def _format_table(table_name: str) -> tuple[str, bool]:
    """Returns (formatted section, ok). A failure is reported inline rather than
    raised so one unreadable table can't sink a whole-dataset overview.
    """
    try:
        fields = get_runner().get_table_schema(table_name)
    except Exception as exc:  # noqa: BLE001 - tool boundary: never raise, always return a ToolMessage
        return f"(schema unavailable: {exc})", False

    lines = []
    for field in fields:
        marker = (
            " [PII - never select directly]"
            if field["name"] in PII_BLOCKED_COLUMNS
            else ""
        )
        description = f" - {field['description']}" if field.get("description") else ""
        lines.append(
            f"- {field['name']} ({field['type']}, {field['mode']}){marker}{description}"
        )
    return "\n".join(lines), True


@tool
async def get_schema(
    runtime: ToolRuntime, table_name: str | None = None
) -> ToolMessage:
    """Inspect the available data. Call with no arguments for the full dataset
    overview (every table, its columns, and how the tables join) - use that to
    answer "what data do we have / what can we analyse". Pass a table_name
    (orders, order_items, products, users) for just that table's columns. Use this
    instead of guessing column names.
    """
    logger.info("Agent Called Tool", extra={"tool_name": "get_schema"})
    if table_name is not None and table_name not in ALLOWED_TABLES:
        return ToolMessage(
            content=f"Unknown table '{table_name}'. Available tables: {', '.join(sorted(ALLOWED_TABLES))}.",
            status="error",
            tool_call_id=runtime.tool_call_id,
        )

    if table_name:
        section, ok = _format_table(table_name)
        return ToolMessage(
            content=f"## {table_name}\n{section}",
            status="success" if ok else "error",
            tool_call_id=runtime.tool_call_id,
        )

    tables = sorted(ALLOWED_TABLES)
    sections = [
        "Dataset `bigquery-public-data.thelook_ecommerce` (read-only), tables: "
        + ", ".join(tables),
        *(f"## {name}\n{_format_table(name)[0]}" for name in tables),
        RELATIONSHIPS,
    ]
    return ToolMessage(content="\n\n".join(sections), tool_call_id=runtime.tool_call_id)
