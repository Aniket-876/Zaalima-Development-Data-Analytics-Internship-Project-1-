# Dataset Source and Overview

> **Status: SIMULATED development data.** Not real company data and not an official Zaalima dataset (stated in `data/raw/README_DATASET.md`). It must not be presented as real data. Whether it can be used for the final project is **awaiting the mentor's confirmation**.

## 1. Which dataset is this?

| Item | Detail |
|---|---|
| Name | `causal_pricing_starter_dataset` |
| How it reached me | Shared by a team member as a zip archive for the data-cleaning phase (the zip was uploaded twice; both copies are byte-identical) |
| Created by | Not stated beyond "simulated development data"; archive files are dated 2026-10-18 |
| Contents | 3 CSV files plus `README_DATASET.md` |
| Real or simulated | **Simulated** (README: "NOT real company data, NOT an official Zaalima dataset, and NOT empirical evidence") |
| Usage permissions | **Not documented.** Being simulated, it contains no confidential or personal data, but no licence or usage statement is included. Confirm with the team lead or mentor before publishing it more widely |

## 2. Files, size and format

| File | Format | Rows | Columns | Grain |
|---|---|---|---|---|
| `regional_market_transactions.csv` | CSV, comma-separated, header row | 87,600 | 17 | One row per market × product × day |
| `market_metadata.csv` | CSV | 20 | 5 | One row per market |
| `product_metadata.csv` | CSV | 12 | 4 | One row per product |

## 3. Coverage

| Item | Detail |
|---|---|
| Time coverage | Daily, 2024-01-01 to 2024-12-30 (365 days; 31 Dec 2024 absent) |
| Markets | 20 (M001–M020), 5 regions with 4 markets each |
| Products | 12 (P001–P012), 4 categories with 3 products each |
| Unit of analysis | **Market-product-day** |
| Panel balance | Complete: every market × product has all 365 days |
| Simulated intervention | 8% price increase in 4 markets (M001–M004) from 2024-07-01. The other 16 markets are never treated |
| Outcome candidates | `units_sold`, `revenue`, `gross_profit` |
| Other variables | `price`, `competitor_price`, `promotion`, `seasonal_index`, `day_of_week`, `unit_cost`, market size index, product baseline price and demand |

## 4. What I could and could not verify

- **Verified:** file structure, row/column counts, date coverage, ID consistency between the three files, and the treatment setup (see `data_quality_report.md`).
- **Could not verify:** whether the project repository holds another, "actual" dataset. I only had the uploaded zip and the task document, not repository access. The task instructions say to inform the team before choosing an alternative if the dataset is unavailable and never to present demo data as real, so this dataset is labelled simulated throughout. An earlier shared file named `algorithmic_pricing_synthetic_control_dataset.csv` was also mentioned in the project; it was not part of this review, so please confirm which file the team treats as the project dataset.

## 5. Open questions for the mentor

1. Is simulated data acceptable for development, and is a real dataset mandatory for the final project?
2. If a real dataset is required, who provides it, and under what usage terms?
3. Is there any restriction on committing the simulated files to the shared GitHub repository?
