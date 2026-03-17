"""
generate_data.py
Generates synthetic South African retail + load shedding data.
Run this once to create your raw CSV files before the ETL pipeline.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 31)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PRODUCTS = [
    {"product_id": "P001", "name": "White Bread 700g",     "category": "Bakery",    "cost": 14.99, "price": 22.99},
    {"product_id": "P002", "name": "Full Cream Milk 2L",   "category": "Dairy",     "cost": 22.00, "price": 32.99},
    {"product_id": "P003", "name": "Chicken Braai Pack",   "category": "Meat",      "cost": 65.00, "price": 99.99},
    {"product_id": "P004", "name": "Sunflower Oil 2L",     "category": "Pantry",    "cost": 38.00, "price": 54.99},
    {"product_id": "P005", "name": "Maize Meal 5kg",       "category": "Pantry",    "cost": 42.00, "price": 62.99},
    {"product_id": "P006", "name": "Rooibos Tea 100 bags", "category": "Beverages", "cost": 28.00, "price": 44.99},
    {"product_id": "P007", "name": "Biltong 250g",         "category": "Snacks",    "cost": 55.00, "price": 84.99},
    {"product_id": "P008", "name": "Boerewors 500g",       "category": "Meat",      "cost": 45.00, "price": 69.99},
    {"product_id": "P009", "name": "Pap & Sauce Ready",    "category": "Ready Meal","cost": 18.00, "price": 29.99},
    {"product_id": "P010", "name": "Coca-Cola 2L",         "category": "Beverages", "cost": 20.00, "price": 32.99},
]

STORES = [
    {"store_id": "S001", "name": "Soweto Main",      "city": "Johannesburg", "province": "Gauteng"},
    {"store_id": "S002", "name": "Sandton Central",  "city": "Johannesburg", "province": "Gauteng"},
    {"store_id": "S003", "name": "Cape Town CBD",    "city": "Cape Town",    "province": "Western Cape"},
    {"store_id": "S004", "name": "Durban North",     "city": "Durban",       "province": "KwaZulu-Natal"},
    {"store_id": "S005", "name": "Pretoria East",    "city": "Pretoria",     "province": "Gauteng"},
]

LOADSHED_STAGES = {
    "2023-01": 4, "2023-02": 5, "2023-03": 6, "2023-04": 5,
    "2023-05": 4, "2023-06": 3, "2023-07": 3, "2023-08": 4,
    "2023-09": 3, "2023-10": 2, "2023-11": 2, "2023-12": 1,
    "2024-01": 2, "2024-02": 2, "2024-03": 1, "2024-04": 1,
    "2024-05": 0, "2024-06": 0, "2024-07": 0, "2024-08": 0,
    "2024-09": 0, "2024-10": 0, "2024-11": 0, "2024-12": 0,
}


# ── 1. Products table ─────────────────────────────────────────────────────────
def generate_products():
    df = pd.DataFrame(PRODUCTS)
    df.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)
    print(f"  ✔ products.csv ({len(df)} rows)")


# ── 2. Stores table ───────────────────────────────────────────────────────────
def generate_stores():
    df = pd.DataFrame(STORES)
    df.to_csv(f"{OUTPUT_DIR}/stores.csv", index=False)
    print(f"  ✔ stores.csv ({len(df)} rows)")


# ── 3. Load shedding schedule ─────────────────────────────────────────────────
def generate_loadshedding():
    records = []
    current = START_DATE
    while current <= END_DATE:
        month_key = current.strftime("%Y-%m")
        stage = LOADSHED_STAGES.get(month_key, 0)
        # Add daily variance ±1 stage
        daily_stage = max(0, min(6, stage + random.choice([-1, 0, 0, 1])))
        hours = daily_stage * 2  # each stage = ~2 hrs outage per day
        records.append({
            "date": current.strftime("%Y-%m-%d"),
            "stage": daily_stage,
            "hours_without_power": hours,
            "scheduled": daily_stage > 0,
        })
        current += timedelta(days=1)
    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/loadshedding.csv", index=False)
    print(f"  ✔ loadshedding.csv ({len(df)} rows)")
    return df


# ── 4. Sales transactions ─────────────────────────────────────────────────────
def generate_sales(loadshed_df):
    loadshed_df["date"] = pd.to_datetime(loadshed_df["date"])
    records = []
    sale_id = 1

    current = START_DATE
    while current <= END_DATE:
        ls_row = loadshed_df[loadshed_df["date"] == pd.Timestamp(current)]
        stage = int(ls_row["stage"].values[0]) if not ls_row.empty else 0

        # Sales volume drops with higher loadshedding
        base_sales = random.randint(40, 80)
        impact_factor = 1 - (stage * 0.08)  # Stage 6 = ~48% fewer sales
        num_sales = max(5, int(base_sales * impact_factor))

        # Weekend boost
        if current.weekday() >= 5:
            num_sales = int(num_sales * 1.3)

        for _ in range(num_sales):
            product = random.choice(PRODUCTS)
            store   = random.choice(STORES)
            qty     = random.randint(1, 5)
            records.append({
                "sale_id":       f"TXN{sale_id:06d}",
                "date":          current.strftime("%Y-%m-%d"),
                "store_id":      store["store_id"],
                "product_id":    product["product_id"],
                "quantity":      qty,
                "unit_price":    product["price"],
                "unit_cost":     product["cost"],
                "revenue":       round(qty * product["price"], 2),
                "cogs":          round(qty * product["cost"], 2),
            })
            sale_id += 1

        current += timedelta(days=1)

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/sales.csv", index=False)
    print(f"  ✔ sales.csv ({len(df):,} rows)")


# ── Run all ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🔧 Generating synthetic SA retail data...\n")
    generate_products()
    generate_stores()
    ls = generate_loadshedding()
    generate_sales(ls)
    print("\n✅ All raw data files written to data/raw/\n")
