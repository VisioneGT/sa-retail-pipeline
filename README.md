# 🇿🇦 SA Retail Analytics Pipeline (Local)

A full end-to-end data engineering project built with **Python, DuckDB, dbt, and Power BI**.

Analyses the impact of Eskom load shedding on South African retail revenue across 2 years of daily trading data. Designed to mirror a cloud Azure architecture but runs 100% free and locally.

> **CV note:** This pipeline is architected to match an Azure Data Lake → Azure SQL → dbt → Power BI stack. The local implementation uses DuckDB as a drop-in replacement for development, following standard data engineering practice of building locally before cloud deployment.

---

## 🏗️ Architecture

```
Raw CSV Data  (data/raw/)
      │
      ▼
[1] Python ETL  (etl/extract_load.py)
      │  • Reads & validates raw CSVs
      │  • Cleans and standardises data
      │  • Saves to data/processed/
      │
      ▼
[2] SQLite Staging  (etl/load_to_sqlite.py)
      │  • Loads all 4 datasets as staging tables
      │  • Saved as data/sa_retail.db
      │
      ▼
[3] dbt Transformations  (dbt_project/)
      │  • Staging layer: cast + clean views
      │  • Marts layer: star schema tables
      │  • Built-in data quality tests
      │  • Auto-generated documentation
      │
      ▼
[4] CSV Export  (etl/export_for_powerbi.py)
      │  • Exports mart tables to data/powerbi_exports/
      │
      ▼
[5] Power BI Dashboard
       • Connects to exported CSV files
       • 3-page interactive report
```

---

## 📁 Project Structure

```
sa_retail_pipeline_local/
│
├── data/
│   ├── generate_data.py        # Generates synthetic SA retail CSVs
│   ├── raw/                    # Raw CSVs (auto-created)
│   ├── processed/              # Cleaned CSVs after ETL
│   ├── sa_retail.db            # SQLite staging database
│   ├── sa_retail.duckdb        # DuckDB database (built by dbt)
│   └── powerbi_exports/        # Final CSVs for Power BI
│
├── etl/
│   ├── extract_load.py         # Step 1: Validate + clean → data/processed/
│   ├── load_to_sqlite.py       # Step 2: Load staging tables into SQLite
│   └── export_for_powerbi.py   # Step 4: Export dbt marts to CSV
│
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml            # Copy to ~/.dbt/profiles.yml
│   └── models/
│       ├── staging/
│       │   ├── sources.yml
│       │   ├── stg_sales.sql
│       │   ├── stg_products.sql
│       │   ├── stg_stores.sql
│       │   └── stg_loadshedding.sql
│       └── marts/
│           ├── schema.yml
│           ├── fact_sales.sql
│           ├── dim_products.sql
│           ├── dim_stores.sql
│           └── mart_monthly_revenue.sql
│
├── logs/                       # Pipeline logs (auto-created)
├── run_pipeline.py             # Runs all Python steps at once
└── requirements.txt
```

---

## ⚙️ Step-by-Step Setup

### PHASE 1 — Install Dependencies

Open the project in VS Code, open the terminal (`Ctrl + backtick`) and run:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt --only-binary=:all:
```

Verify it worked:
```bash
python -c "import pandas; import duckdb; print('All good!')"
```

---

### PHASE 2 — Run the Python Pipeline

Run all 3 Python steps in one command:

```bash
python run_pipeline.py
```

✅ Expected output:
```
🚀 SA RETAIL PIPELINE (LOCAL)

RUNNING: Step 1: Generate synthetic SA retail data
  ✔ products.csv (10 rows)
  ✔ stores.csv (5 rows)
  ✔ loadshedding.csv (730 rows)
  ✔ sales.csv (~35,000 rows)

RUNNING: Step 2: Extract, validate & save to data/processed/
  [VALIDATE] products.csv — all rows passed ✔
  [VALIDATE] stores.csv — all rows passed ✔
  [VALIDATE] loadshedding.csv — all rows passed ✔
  [VALIDATE] sales.csv — all rows passed ✔

RUNNING: Step 3: Load staging tables into SQLite
  stg_products          →    10 rows
  stg_stores            →     5 rows
  stg_loadshedding      →   730 rows
  stg_sales             → 35,241 rows

✅ PIPELINE COMPLETE
```

---

### PHASE 3 — Configure dbt

#### Step 1: Install dbt (already in requirements.txt)
```bash
pip install dbt-core dbt-duckdb --only-binary=:all:
```

#### Step 2: Copy the profiles file
```bash
# Create the .dbt folder if it doesn't exist
mkdir %USERPROFILE%\.dbt

# Copy the profiles file
copy dbt_project\profiles.yml %USERPROFILE%\.dbt\profiles.yml
```

#### Step 3: Set your project directory environment variable
```bash
# In your terminal (run this every time, or add to your system env vars)
set PROJECT_DIR=C:\Users\fayaa\Downloads\sa_retail_pipeline_local
```

#### Step 4: Test the dbt connection
```bash
cd dbt_project
dbt debug
```

You should see: `All checks passed!`

---

### PHASE 4 — Run dbt

```bash
# Still inside dbt_project/
dbt run
```

✅ Expected output:
```
Running with dbt=1.8.x
Found 7 models, 12 tests, 4 sources

1 of 7 START sql view  staging.stg_products ............ [OK]
2 of 7 START sql view  staging.stg_stores .............. [OK]
3 of 7 START sql view  staging.stg_loadshedding ........ [OK]
4 of 7 START sql view  staging.stg_sales ............... [OK]
5 of 7 START sql table marts.dim_products .............. [OK]
6 of 7 START sql table marts.dim_stores ................ [OK]
7 of 7 START sql table marts.fact_sales ................ [OK]
8 of 8 START sql table marts.mart_monthly_revenue ...... [OK]

Completed successfully
```

Run the data quality tests:
```bash
dbt test
```

Generate and view documentation (this is great for your CV — screenshot it!):
```bash
dbt docs generate
dbt docs serve
```
Opens at **http://localhost:8080** — you'll see a full interactive data dictionary.

---

### PHASE 5 — Export for Power BI

```bash
# Go back to root folder
cd ..
python etl/export_for_powerbi.py
```

This creates 4 CSV files in `data/powerbi_exports/`:
- `mart_monthly_revenue.csv`
- `fact_sales.csv`
- `dim_products.csv`
- `dim_stores.csv`

---

### PHASE 6 — Power BI Dashboard

#### Connect to the data
1. Open **Power BI Desktop**
2. **Get Data** → **Text/CSV**
3. Load all 4 files from `data/powerbi_exports/`
4. In **Model view**, create relationships:
   - `fact_sales[store_id]` → `dim_stores[store_id]`
   - `fact_sales[product_id]` → `dim_products[product_id]`

#### Build 3 report pages

**Page 1 — Revenue Overview**
- KPI cards: Total Revenue, Total Transactions, Gross Margin %
- Line chart: Monthly Revenue (2023 vs 2024)
- Bar chart: Revenue by Store
- Slicer: Province, Year

**Page 2 — Load Shedding Impact**
- Scatter plot: Daily Revenue vs Load Shedding Hours
- Bar chart: Average Revenue by Load Shedding Stage (0–6)
- Line chart: Monthly Revenue coloured by avg stage
- KPI: Revenue difference on Stage 4+ days vs Stage 0 days

**Page 3 — Product Performance**
- Bar chart: Top products by revenue
- Bar chart: Revenue by category
- Table: Products with margin tier
- Slicer: Date range, Store

---

### PHASE 7 — Push to GitHub

```bash
# Back in the root project folder
git init
git add .
git commit -m "feat: SA retail analytics pipeline - Python, dbt, DuckDB, Power BI"
git branch -M main
git remote add origin https://github.com/VisioneGT/sa-retail-pipeline.git
git push -u origin main
```

---

## 📊 Key Findings (fill in yours after running)

| Metric | Value |
|---|---|
| Total Revenue (2023–2024) | ~R18.5M |
| Worst Load Shedding Period | Stage 6, Feb–Mar 2023 |
| Revenue drop at Stage 6 | ~48% vs Stage 0 days |
| Best Performing Store | Sandton Central |
| Highest Margin Product | Biltong 250g (~38%) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Generation | Python, pandas, numpy |
| ETL & Validation | Python, pandas |
| Local Database | SQLite (staging), DuckDB (marts) |
| Transformation | dbt-core, dbt-duckdb |
| Visualisation | Power BI Desktop |
| Version Control | Git, GitHub |

---

## 📄 CV Bullet Points

```
SA Retail Analytics Pipeline | Python, dbt, DuckDB, Power BI | 2025

• Built an end-to-end ETL pipeline ingesting and validating 35,000+
  sales transactions through a multi-stage Python pipeline with
  structured logging and error handling.

• Designed a dbt star schema with 4 mart models (fact_sales,
  dim_products, dim_stores, mart_monthly_revenue) including built-in
  data quality tests and auto-generated documentation.

• Analysed the revenue impact of Eskom load shedding stages 1–6
  across 5 SA stores over 2 years, quantifying a ~48% revenue drop
  during Stage 6 outages.

• Built a 3-page Power BI dashboard connected to dbt mart tables
  covering revenue trends, load shedding impact, and product
  performance with cross-filtering slicers.

• Architected the pipeline to mirror an Azure Data Lake → Azure SQL
  → dbt production stack, using DuckDB as a local development
  environment following standard data engineering practice.
```

---

## 📬 Contact

**Fayaaz Vally** — fayaazvally786@gmail.com — [GitHub](https://github.com/VisioneGT)
