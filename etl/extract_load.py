"""
etl/extract_load.py
───────────────────
Step 1 of the LOCAL pipeline:
  - Reads raw CSVs from data/raw/
  - Validates and cleans each file
  - Saves cleaned CSVs to data/processed/
  - Logs every step to logs/pipeline.log

No Azure needed — runs 100% locally.

Usage:
    python etl/extract_load.py
"""

import os
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

RAW_DIR       = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


# ── Validation rules per file ─────────────────────────────────────────────────
VALIDATIONS = {
    "sales.csv": {
        "required_cols": ["sale_id", "date", "store_id", "product_id",
                          "quantity", "unit_price", "revenue"],
        "not_null": ["sale_id", "date", "store_id", "product_id"],
        "positive": ["quantity", "unit_price", "revenue"],
    },
    "loadshedding.csv": {
        "required_cols": ["date", "stage", "hours_without_power"],
        "not_null": ["date", "stage"],
        "positive": [],
    },
    "products.csv": {
        "required_cols": ["product_id", "name", "category", "cost", "price"],
        "not_null": ["product_id", "name"],
        "positive": ["cost", "price"],
    },
    "stores.csv": {
        "required_cols": ["store_id", "name", "city", "province"],
        "not_null": ["store_id", "name"],
        "positive": [],
    },
}


def extract(filename: str) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, filename)
    log.info(f"[EXTRACT] Reading {filename}")
    df = pd.read_csv(path)
    log.info(f"[EXTRACT] {filename} — {len(df):,} rows, {len(df.columns)} cols")
    return df


def validate(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    rules = VALIDATIONS.get(filename, {})
    original_len = len(df)

    for col in rules.get("required_cols", []):
        if col not in df.columns:
            raise ValueError(f"[VALIDATE] Missing required column '{col}' in {filename}")

    df = df.dropna(subset=rules.get("not_null", []))

    for col in rules.get("positive", []):
        if col in df.columns:
            df = df[df[col] > 0]

    dropped = original_len - len(df)
    if dropped > 0:
        log.warning(f"[VALIDATE] {filename} — dropped {dropped} invalid rows")
    else:
        log.info(f"[VALIDATE] {filename} — all rows passed ✔")
    return df


def transform(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    df["_loaded_at"]   = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    df["_source_file"] = filename

    log.info(f"[TRANSFORM] {filename} — cleaning complete")
    return df


def save_locally(df: pd.DataFrame, filename: str):
    out_path = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(out_path, index=False)
    log.info(f"[SAVE] {filename} → data/processed/{filename} ({len(df):,} rows) ✔")


def run_pipeline():
    log.info("=" * 60)
    log.info("PIPELINE START — SA Retail Analytics ETL (Local)")
    log.info("=" * 60)

    files   = ["products.csv", "stores.csv", "loadshedding.csv", "sales.csv"]
    results = {}

    for filename in files:
        try:
            df = extract(filename)
            df = validate(df, filename)
            df = transform(df, filename)
            save_locally(df, filename)
            results[filename] = {"status": "SUCCESS", "rows": len(df)}
        except Exception as e:
            log.error(f"[PIPELINE] FAILED on {filename}: {e}")
            results[filename] = {"status": "FAILED", "error": str(e)}

    log.info("=" * 60)
    log.info("PIPELINE SUMMARY")
    for fname, res in results.items():
        status = res["status"]
        detail = f"{res.get('rows', 0):,} rows" if status == "SUCCESS" else res.get("error")
        log.info(f"  {status:8s} | {fname:25s} | {detail}")
    log.info("=" * 60)
    log.info("PIPELINE COMPLETE — files saved to data/processed/")


if __name__ == "__main__":
    run_pipeline()
