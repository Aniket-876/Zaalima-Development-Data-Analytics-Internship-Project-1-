# Handover: Data Preparation → Causal Design and Modeling

**From:** Fatima (data, quality, cleaning, EDA) **To:** Shrusti and Aniket (Harish for testing/docs)
**Status:** Data cleaned and documented. **The data is simulated**; the mentor's decision on whether it can be used for the final project is still pending. Please label all results simulation/demo until then.

## 1. What is ready

| Item | Location |
|---|---|
| Cleaned data (3 files) | `data/processed/` |
| Raw data (unchanged) | `data/raw/` |
| Dataset source and overview | `docs/dataset_overview.md` |
| Data dictionary | `docs/data_dictionary.md` |
| Data quality report | `docs/data_quality_report.md` |
| Cleaning script (reruns everything) | `src/clean_pricing_data.py` |
| Issue log and validation results (14/14 pass) | `reports/` |
| EDA notebook and charts | `notebooks/01_eda.ipynb`, `docs/figures/`, `docs/eda_summary.md` |

Load the main table:
```python
import pandas as pd
txn = pd.read_csv("data/processed/cleaned_regional_market_transactions.csv", parse_dates=["date", "treatment_date"])
```

## 2. Facts relevant to the causal design (for Shrusti)

- **Unit:** market × product × day; 87,600 rows; the panel is complete (365 days for every market-product).
- **Treated markets:** M001, M002, M003, M004 (one each in Regions 1–4). **Treatment date:** 2024-07-01 for all four. Pre-period 2024-01-01 to 2024-06-30 (182 days); post-period 2024-07-01 to 2024-12-30 (183 days).
- **Candidate donors:** the 16 control markets (M005–M020) are never treated and have complete data for every day. Market size varies a lot (index 0.70–1.48), and the treated markets range from 0.73 (M003) to 1.40 (M001), so size will matter for donor matching. Region_5 has no treated market.
- **Outcome columns:** `units_sold`, `revenue`, `gross_profit` have no missing values. Revenue is dominated by high-priced products, so aggregating to market level will weight those products more.
- **Candidate confounders available:** `promotion` (30 missing), `competitor_price` (60 missing), `seasonal_index`, `day_of_week`, `market_size_index`, product `base_price`.
- **Treatment columns are untouched.** `treated_market` is a fixed group label; `treatment` = 1 only for treated markets on or after 2024-07-01 (8,784 rows). Control markets have `treatment_date` blank on purpose.
- **Observed in the EDA (descriptive only):** treated and control markets track each other closely before July (monthly ratio of average units 1.00–1.01), and price in treated markets rises about 8% after July. The EDA does not estimate a causal effect.
- **Question for you:** in treated markets after July, the `price` increase *is* the intervention. Please decide whether `price` belongs among the covariates, since it may be part of the treatment rather than a control.

## 3. Facts relevant to modeling (for Aniket)

- **Missing values left in on purpose:** `competitor_price` (60 rows, `competitor_price_missing = 1`) and `promotion` (30 rows, `promotion_missing = 1`). They are isolated single days spread across all markets. Please agree on one rule with the team (exclude, interpolate, or skip those variables) and apply it consistently. A sensitivity run with and without the flagged rows is easy using the flags.
- **Leakage risk:** `revenue = price × units_sold` (up to rounding) and `gross_profit = revenue − unit_cost × units_sold`. If `units_sold` is the outcome, `revenue` and `gross_profit` must not be features, and vice versa.
- **Overlap/positivity:** `treatment` is fully determined by market and date. Treated rows only exist in 4 markets after 1 July, and control rows are never treated, so overlap in covariates deserves a check before fitting.
- **Time structure:** strong seasonality (`seasonal_index`) and a weekday pattern (Monday highest, Thursday/Friday lowest) are present in every market.
- **Outliers:** 27 values more than 4 standard deviations from their product mean were kept; they are plausible.
- **Skew:** price and revenue are right-skewed because of the product mix; consider this when choosing outcome scaling.

## 4. Known limitations

1. Simulated data; nothing here is real-world evidence.
2. Only 4 treated markets, all starting on the same date; treated rows are 20% of the data, active treatment about 10%.
3. 60 competitor prices and 30 promotion values missing; 31 Dec 2024 missing for every market.
4. `revenue` does not equal `price × units_sold` to the cent (rounding only). Do not recompute it.
5. Currency and units are not documented in the dataset.

## 5. Decisions still needed from the team

1. Mentor's answer on simulated versus real data.
2. One agreed treatment of the 90 flagged rows (60 + 30).
3. The analysis level (market-product-day, market-day, or market-week) for the synthetic control and DML.

## 6. If data problems appear later

Rerun `python src/clean_pricing_data.py`; any new issue shows up in `reports/dq_issue_log.csv` and `reports/validation_results.csv`. Message me in the group with the issue and I will update the documents.
