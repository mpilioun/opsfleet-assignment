from src.clients.bq_client import BigQueryRunner

REQUIRED_TABLES = ["orders", "order_items", "products", "users"]


def main():
    runner = BigQueryRunner()
    for table_name in REQUIRED_TABLES:
        schema = runner.get_table_schema(table_name)
        print(f"{table_name}: {len(schema)} columns")
        for field in schema:
            print(f"  - {field['name']} ({field['type']}, {field['mode']})")


if __name__ == "__main__":
    main()
