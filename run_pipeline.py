"""
run_pipeline.py
───────────────
Runs the full LOCAL pipeline in one command:

  Step 1: Generate synthetic SA retail data (CSVs)
  Step 2: Extract, validate, clean → save to data/processed/
  Step 3: Load staging tables into SQLite (data/sa_retail.db)

After this script completes, run dbt manually:
  cd dbt_project
  dbt run
  dbt test

Then export for Power BI:
  cd ..
  python etl/export_for_powerbi.py

Usage:
    python run_pipeline.py
"""

import subprocess
import sys
import logging
import os
from datetime import datetime

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


def run_step(name: str, command: list):
    log.info(f"\n{'='*60}")
    log.info(f"RUNNING: {name}")
    log.info(f"{'='*60}\n")
    result = subprocess.run(command)
    if result.returncode != 0:
        log.error(f"STEP FAILED: {name} (exit code {result.returncode})")
        sys.exit(1)
    log.info(f"\nSTEP COMPLETE: {name} ✔")


if __name__ == "__main__":
    start = datetime.now()
    log.info(f"\n🚀 SA RETAIL PIPELINE (LOCAL) — {start.strftime('%Y-%m-%d %H:%M:%S')}\n")

    run_step(
        "Step 1: Generate synthetic SA retail data",
        [sys.executable, "data/generate_data.py"]
    )

    run_step(
        "Step 2: Extract, validate & save to data/processed/",
        [sys.executable, "etl/extract_load.py"]
    )

    run_step(
        "Step 3: Load staging tables into SQLite",
        [sys.executable, "etl/load_to_sqlite.py"]
    )

    duration = (datetime.now() - start).seconds
    log.info(f"\n{'='*60}")
    log.info(f"✅ PIPELINE COMPLETE in {duration}s")
    log.info(f"{'='*60}")
    log.info("\nNext steps:")
    log.info("  1. cd dbt_project")
    log.info("  2. dbt run")
    log.info("  3. dbt test")
    log.info("  4. cd ..")
    log.info("  5. python etl/export_for_powerbi.py")
    log.info("  6. Open Power BI → connect to data/powerbi_exports/ CSVs\n")
