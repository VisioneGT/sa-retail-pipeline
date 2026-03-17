"""
etl/export_for_powerbi.py
─────────────────────────
Step 4 of the LOCAL pipeline (run after dbt):
  - Connects to the DuckDB database built by dbt
  - Exports all mart tables to CSV files in data/powerbi_exports/
  - Power BI connects to these CSV files (File → Get Data → Text/CSV)

Usage:
    python etl/export_for_powerbi.py
"""

import os
import logging
import duckdb
import pandas as pd

# ── Setup ─────────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
os.makedirs("data/powerbi_exports", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

DB_PATH    = os.path.join(os.path.dirname(__file__), "..", "data", "sa_retail.duckdb")
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "powerbi_exports")

# Tables to export — these are created by dbt
EXPORT_TABLES = [
    ("marts", "mart_monthly_revenue"),
    ("marts", "fact_sales"),
    ("marts", "dim_products"),
    ("marts", "dim_stores"),
]


def export_tables():
    if not os.path.exists(DB_PATH):
        log.error(f"DuckDB database not found at {DB_PATH}")
        log.error("Make sure you have run: cd dbt_project && dbt run")
        return

    conn = duckdb.connect(DB_PATH, read_only=True)

    log.info("=" * 60)
    log.info("STAGE 4 — Exporting mart tables for Power BI")
    log.info("=" * 60)

    for schema, table in EXPORT_TABLES:
        try:
            df = conn.execute(f"SELECT * FROM {schema}.{table}").df()
            out_path = os.path.join(EXPORT_DIR, f"{table}.csv")
            df.to_csv(out_path, index=False)
            log.info(f"  ✔ {table}.csv — {len(df):,} rows → data/powerbi_exports/")
        except Exception as e:
            log.error(f"  ✗ Failed to export {table}: {e}")

    conn.close()

    log.info("=" * 60)
    log.info("EXPORT COMPLETE")
    log.info(f"Files saved to: data/powerbi_exports/")
    log.info("In Power BI: Get Data → Text/CSV → select each file")
    log.info("=" * 60)


if __name__ == "__main__":
    export_tables()
