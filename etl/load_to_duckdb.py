import os
import duckdb
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
DB_PATH       = os.path.join(os.path.dirname(__file__), "..", "data", "sa_retail.duckdb")

FILE_TABLE_MAP = {
    "products.csv":     "stg_products",
    "stores.csv":       "stg_stores",
    "loadshedding.csv": "stg_loadshedding",
    "sales.csv":        "stg_sales",
}

conn = duckdb.connect(DB_PATH)

for filename, table_name in FILE_TABLE_MAP.items():
    path = os.path.join(PROCESSED_DIR, filename)
    df = pd.read_csv(path)
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  OK  {table_name:25s} {count:,} rows")

conn.close()
print("DONE - DuckDB ready for dbt")