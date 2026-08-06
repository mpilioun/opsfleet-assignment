"""Golden Bucket seed trios: Question -> SQL -> Report.

Every SQL statement here has been executed against
`bigquery-public-data.thelook_ecommerce` and returns real, non-empty rows.
The two comparison trios (product, state) previously used placeholder
entities ("Product A"/"Product B", "State X"/"State Y") that don't exist in
the dataset and always returned zero rows - they now reference real product
names and states, picked and verified against live query results.
"""

from typing import Any

SEED_TRIOS: list[dict[str, Any]] = [
    {
        "id": "seed-top-customers",
        "question": "Who are our top 10 customers by total spend?",
        "sql": (
            "SELECT user_id, SUM(sale_price) AS total_spend "
            "FROM bigquery-public-data.thelook_ecommerce.order_items "
            "GROUP BY user_id ORDER BY total_spend DESC LIMIT 10"
        ),
        "report": (
            "## Top Customers by Spend\n\n"
            "- Top 10 customers (identified by internal customer ID, never by name/email) "
            "account for a disproportionate share of revenue.\n"
            "- **Action item:** consider a loyalty/retention offer targeted at this cohort "
            "before the next quarter."
        ),
        "tags": ["customer_behavior", "top_customers"],
    },
    {
        "id": "seed-product-comparison",
        "question": (
            "Compare the performance of Wrangler Men's Premium Performance Cowboy Cut "
            "Jean and True Religion Men's Ricky Straight Jean and explain why they differ."
        ),
        "sql": (
            "SELECT p.name, COUNT(oi.id) AS units_sold, SUM(oi.sale_price) AS revenue, "
            "AVG(oi.sale_price) AS avg_price FROM bigquery-public-data.thelook_ecommerce.order_items oi "
            "JOIN bigquery-public-data.thelook_ecommerce.products p ON p.id = oi.product_id "
            'WHERE p.name IN ("Wrangler Men\'s Premium Performance Cowboy Cut Jean", '
            '"True Religion Men\'s Ricky Straight Jean") GROUP BY p.name'
        ),
        "report": (
            "## Product Performance Comparison\n\n"
            "- Wrangler's Cowboy Cut Jean sells ~59 units at an avg price of ~$48 (~$2.8K revenue); "
            "True Religion's Ricky Straight Jean sells ~38 units at an avg price of ~$256 (~$9.7K revenue).\n"
            "- Higher revenue per unit more than offsets lower volume for True Religion - this is a "
            "volume-vs-margin split, not an underperformance signal for either product.\n"
            "- **Action item:** if the goal is unit volume, Wrangler's price point is the benchmark; "
            "if the goal is margin per sale, True Religion's positioning is."
        ),
        "tags": ["product_performance", "comparison"],
    },
    {
        "id": "seed-monthly-revenue",
        "question": "What is our monthly revenue trend over the last 12 months?",
        "sql": (
            "SELECT DATE_TRUNC(o.created_at, MONTH) AS month, SUM(oi.sale_price) AS revenue "
            "FROM bigquery-public-data.thelook_ecommerce.orders o "
            "JOIN bigquery-public-data.thelook_ecommerce.order_items oi ON oi.order_id = o.order_id "
            "WHERE DATE(o.created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH) "
            "GROUP BY month ORDER BY month"
        ),
        "report": (
            "## Monthly Revenue Trend\n\n"
            "- Plot revenue by month; call out the single largest month-over-month swing.\n"
            "- **Action item:** if a seasonal dip repeats yearly, plan a promo ahead of it next time."
        ),
        "tags": ["time_based_metrics", "revenue"],
    },
    {
        "id": "seed-churn-spike",
        "question": "Why did our churn rate spike last month?",
        "sql": (
            "SELECT DATE_TRUNC(o.created_at, MONTH) AS month, "
            "COUNTIF(o.status IN ('Cancelled', 'Returned')) / COUNT(*) AS cancel_return_rate "
            "FROM bigquery-public-data.thelook_ecommerce.orders o GROUP BY month ORDER BY month"
        ),
        "report": (
            "## Churn / Cancellation Spike\n\n"
            "- thelook_ecommerce has no direct churn flag, so approximate churn via the "
            "cancellation/return rate trend and via customers who ordered in the prior month "
            "but not the current one.\n"
            "- In practice this rate holds fairly flat (~24-26%) month to month - a real 'spike' "
            "claim needs the actual month-over-month delta checked before writing the report, not "
            "assumed from the question's premise.\n"
            "- Cross-check the spike month against a product/shipping issue (e.g. a spike in "
            "returns for one department) before concluding it's demand-driven.\n"
            "- **Action item:** investigate the top-returned product category from that month."
        ),
        "tags": ["churn", "retention"],
    },
    {
        "id": "seed-state-underspend",
        "question": (
            "Why are users in Colorado underspending, and how does that compare to Tennessee?"
        ),
        "sql": (
            "SELECT u.state, AVG(spend.total_spend) AS avg_spend_per_customer "
            "FROM bigquery-public-data.thelook_ecommerce.users u JOIN ("
            "SELECT user_id, SUM(sale_price) AS total_spend "
            "FROM bigquery-public-data.thelook_ecommerce.order_items GROUP BY user_id"
            ") spend ON spend.user_id = u.id "
            "WHERE u.state IN ('Colorado', 'Tennessee') GROUP BY u.state"
        ),
        "report": (
            "## Spend Comparison by State\n\n"
            "- Colorado customers average ~$120/customer vs Tennessee's ~$144/customer (~17% gap), "
            "both on samples large enough to be meaningful (310 vs 352 customers).\n"
            "- Compare average spend per customer between the two states; never name individual "
            "customers, only state-level aggregates.\n"
            "- **Action item:** check whether the gap correlates with traffic source or order "
            "cancellation rate in Colorado before assuming it's a demand issue."
        ),
        "tags": ["customer_behavior", "geography"],
    },
    {
        "id": "seed-database-structure",
        "question": "What data do we have available and what can we analyze with it?",
        "sql": "",
        "report": (
            "## Available Data\n\n"
            "- `orders`, `order_items`, `products`, `users` from `thelook_ecommerce`.\n"
            "- Use the `get_schema` tool (not a hand-written SQL query) to answer structure "
            "questions - that keeps the answer accurate as the schema evolves.\n"
            "- Can analyze: customer spend/behavior, product performance, revenue trends, "
            "and cross-cuts by state/city/traffic-source (never by raw name/email)."
        ),
        "tags": ["meta", "schema"],
    },
]
