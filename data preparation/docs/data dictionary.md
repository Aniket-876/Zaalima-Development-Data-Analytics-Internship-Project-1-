# Data Dictionary — Causal Pricing Starter Dataset (SIMULATED)

> The data is simulated (see `README_DATASET.md`). Anything estimated from it must be labelled simulation/demo until the mentor confirms it can be used. Currency is not specified in the source files.

Cleaned files are in `data/processed/`; raw files are in `data/raw/` and are never modified. Columns marked **added** do not exist in the raw data.

## 1. `data/processed/cleaned_regional_market_transactions.csv` (main dataset)

Grain: one row per **market × product × day**. 87,600 rows = 20 markets × 12 products × 365 days (2024-01-01 to 2024-12-30). Unique key: `market_id + product_id + date`.

| Column | Type | Description | Values / ranges | Notes |
|---|---|---|---|---|
| market_id | string | Market identifier (FK to market metadata) | M001–M020 | No missing values |
| region | string | Region of the market | Region_1–Region_5 | 30 blanks in raw, filled from market metadata |
| product_id | string | Product identifier (FK to product metadata) | P001–P012 | No missing values |
| category | string | Product category | Category_1–Category_4 | Fully determined by `product_id`; consistent with metadata |
| date | date | Observation day (ISO `YYYY-MM-DD`) | 2024-01-01 – 2024-12-30 | 2024-12-31 is absent |
| treated_market | 0/1 | 1 if the market is in the pricing-intervention group | 0, 1 | Markets M001–M004 = 1. **Unchanged from raw** |
| treatment_date | date | Date the price intervention starts in a treated market | 2024-07-01 or blank | Blank for all control markets (by design). **Unchanged** |
| treatment | 0/1 | 1 when the market is treated **and** date ≥ `treatment_date` (post-intervention row) | 0, 1 | This is the DiD-style treated×post indicator, not the group flag. **Unchanged** |
| price | float | Selling price per unit | 8.20 – 79.70 | Rounded to 2 dp |
| competitor_price | float | Competitor's price for the same product | 7.69 – 87.28 | 60 missing, left missing |
| promotion | 0/1 (Int) | 1 if a promotion ran that day | 0, 1 | Float in raw, now integer. 30 missing, left missing |
| day_of_week | int | Day of week, 0 = Monday … 6 = Sunday | 0–6 | Verified against `date` |
| seasonal_index | float | Simulated seasonal demand multiplier (mean ≈ 1.0) | 0.835 – 1.170 | Same value for all markets/products on a given day |
| units_sold | int | Units sold that day | 21 – 219 | |
| revenue | float | Sales value, ≈ `price × units_sold` | 267.46 – 10,290.24 | Rounded separately, so can differ from `price × units_sold` by up to 0.005 × units (see report) |
| unit_cost | float | Cost per unit | 4.38 – 56.45 | Varies daily; always below `price` |
| gross_profit | float | `revenue − unit_cost × units_sold` | 80.76 – 4,908.60 | Reconciles exactly in every row |
| region_filled_from_metadata | 0/1 | **added**: 1 if `region` was blank in raw and filled by lookup | 0, 1 | 30 rows |
| competitor_price_missing | 0/1 | **added**: 1 if `competitor_price` is missing | 0, 1 | 60 rows |
| promotion_missing | 0/1 | **added**: 1 if `promotion` is missing | 0, 1 | 30 rows |

## 2. `data/processed/cleaned_market_metadata.csv`

Grain: one row per market (20 rows). Key: `market_id`.

| Column | Type | Description | Values | Notes |
|---|---|---|---|---|
| market_id | string | Market identifier | M001–M020 | Unique, no missing; all 20 appear in transactions |
| region | string | Region the market belongs to | Region_1–Region_5 | 4 markets per region |
| market_size_index | float | Relative market size (1.0 ≈ average) | 0.70 – 1.48 | |
| treated_market | 0/1 | Intervention group flag | M001–M004 = 1 | |
| treatment_date | date | Intervention start | 2024-07-01 for treated, blank otherwise | Blank for the 16 control markets is expected |

## 3. `data/processed/cleaned_product_metadata.csv`

Grain: one row per product (12 rows). Key: `product_id`.

| Column | Type | Description | Values | Notes |
|---|---|---|---|---|
| product_id | string | Product identifier | P001–P012 | Unique, no missing; all 12 appear in transactions |
| category | string | Product category | Category_1–Category_4 | 3 products per category |
| base_price | float | Baseline price used by the simulation | 9.60 – 69.16 | Observed `price` averages ≈ 1.00 × this value |
| base_demand | int | Baseline daily demand used by the simulation | 45 – 89 | |

## Supporting outputs

| File | Purpose |
|---|---|
| `reports/dq_issue_log.csv` | Every check run, rows affected, action taken |
| `reports/validation_results.csv` | Post-cleaning PASS/FAIL checks (14/14 pass) |
| `src/clean_pricing_data.py` | Script that reproduces all of the above |
| `notebooks/01_eda.ipynb` | Exploratory analysis using these cleaned files |
