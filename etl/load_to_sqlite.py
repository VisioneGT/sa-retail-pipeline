"""
etl/load_to_sqlite.py
─────────────────────
Step 2 of the LOCAL pipeline:
  - Reads cleaned CSVs from data/processed/
  - Creates a local SQLite database at data/sa_retail.db
  - Loads all 4 datasets as staging tables
  - Idempotent — safe to re-run, drops and recreates tables each time

No Azure needed — SQLite is built into Python.

Usage:
    python etl/load_to_sqlite.py
"""

import os
import sqlite3
import logging
import pandas as pd
from datetime import datetime

# ── Setup ─────────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
DB_PATH       = os.path.join(os.path.dirname(__file__), "..", "data", "sa_retail.db")

FILE_TABLE_MAP = {
    "products.csv":     "stg_products",
    "stores.csv":       "stg_stores",
    "loadshedding.csv": "stg_loadshedding",
    "sales.csv":        "stg_sales",
}


def load_file(conn: sqlite3.Connection, filename: str, table_name: str):
    path = os.path.join(PROCESSED_DIR, filename)

    if not os.path.exists(path):
        log.error(f"[SQLITE] File not found: {path} — run extract_load.py first")
        return

    log.info(f"[SQLITE] Loading {filename} → {table_name}")
    df = pd.read_csv(path)

    # Drop and recreate table (idempotent)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()

    # Load via pandas — auto-creates table schema from DataFrame
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()

    log.info(f"[SQLITE] {table_name} — {len(df):,} rows loaded ✔")


def verify_tables(conn: sqlite3.Connection):
    """Print row counts for all staging tables as a sanity check."""
    cursor = conn.cursor()
    log.info("\n[SQLITE] Verification — row counts:")
    for table in FILE_TABLE_MAP.values():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        log.info(f"  {table:25s} → {count:,} rows")


def run():
    log.info("=" * 60)
    log.info("STAGE 2 — Loading to SQLite Database (Local)")
    log.info(f"Database: {DB_PATH}")
    log.info("=" * 60)

    conn = sqlite3.connect(DB_PATH)

    for filename, table_name in FILE_TABLE_MAP.items():
        try:
            load_file(conn, filename, table_name)
        except Exception as e:
            log.error(f"[SQLITE] Failed to load {filename}: {e}")

    verify_tables(conn)
    conn.close()

    log.info("=" * 60)
    log.info(f"STAGE 2 COMPLETE — Database saved at: data/sa_retail.db")
    log.info("=" * 60)


if __name__ == "__main__":
    run()
