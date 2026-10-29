# Fatima Data Preparation: Causal Inference & Synthetic Control for Algorithmic Pricing

**Owner:** Fatima: data collection, quality, cleaning and basic EDA
**Hands over to:** Shrusti (causal design / Synthetic Control) and Aniket (DML)

> **The dataset is SIMULATED.** It is not real company data (see `data/raw/README_DATASET.md`). Treat every number as a simulation/demo result until the mentor confirms whether simulated data is acceptable for the final project.

## Folder layout

```
data_preparation/
├── data/raw/          original files, never modified (3 CSVs + README_DATASET.md)
├── data/processed/    cleaned CSVs produced by the script
├── src/               clean_pricing_data.py: reusable cleaning + validation pipeline
├── reports/           dq_issue_log.csv, validation_results.csv
├── docs/              dataset_overview.md, data_dictionary.md, data_quality_report.md,
│                      eda_summary.md, handover_note.md, figures/
├── notebooks/         01_eda.ipynb
└── requirements.txt
```

## Start here

| If you want to... | Read |
|---|---|
| Know where the data came from | `docs/dataset_overview.md` |
| Understand every column | `docs/data_dictionary.md` |
| See the problems found and how they were handled | `docs/data_quality_report.md` |
| See the charts and observations | `docs/eda_summary.md` or `notebooks/01_eda.ipynb` |
| Use the data for causal design or modeling | `docs/handover_note.md` |

## Run it

Open a terminal **inside the `data_preparation` folder**, then:

```bash
pip install -r requirements.txt
python src/clean_pricing_data.py --input-dir data/raw --output-dir data/processed --report-dir reports
jupyter notebook notebooks/01_eda.ipynb
```

The script only reads `data/raw/`, writes to `data/processed/` and `reports/`, refuses to run if the input and output folders are the same, and prints 14 pass/fail validation checks (all pass on this dataset).

## Status

| Deliverable | Status |
|---|---|
| Dataset source and overview | Done. Usage permissions and mentor confirmation still open |
| Data dictionary | Done |
| Data quality report | Done |
| Reusable cleaning script | Done. Ran on the dataset, 14/14 checks pass |
| EDA notebook with charts and observations | Done |
| Cleaned dataset | Included (simulated data) |
| Handover to Shrusti and Aniket | Done |

## Known limitations

Simulated data; only 4 treated markets; 60 competitor prices and 30 promotion values missing (flagged, not imputed); 31 Dec 2024 absent. Full list in `docs/data_quality_report.md`.






# Shrusti = Causal Design & Synthetic Control for Algorithmic Pricing Evaluation

## 1. Objective

This project evaluates the causal impact of the algorithmic price increase implemented on July 1, 2024, in treated markets M001, M002, M003, and M004. The key business question is whether the intervention increased gross profit, while also understanding whether any increase came at the expense of unit sales volume.

The intervention is a roughly 8% increase in selling price. We estimate its effect on three outcomes:

- gross_profit
- revenue
- units_sold

The analysis is conducted using a causal inference framework based on a comparison between treated markets and untreated donor markets, with synthetic control as the primary robustness design.

---

## 2. Treatment Definition

The intervention is defined as:

- Treatment date: July 1, 2024
- Treated markets: M001, M002, M003, M004
- Control markets: M005 through M020
- Exposure: treated markets receive the pricing intervention; untreated markets do not
- Treatment indicator: treatment = 1 for treated markets on or after July 1, 2024

This creates a difference-in-differences / synthetic control setup where the treated group is compared against a counterfactual constructed from untreated markets.

---

## 3. Core Causal Question

Did the approximately 8% algorithmic price increase on July 1, 2024, causally change:

- gross profit
- revenue
- units sold

in the treated markets relative to what would have happened without the intervention?

This is not a simple revenue-only outcome analysis. The business decision depends on balancing:

- margin expansion from higher selling price
- reduced demand due to price resistance
- overall profit impact after accounting for volume decline

Thus, gross_profit is treated as the primary business outcome, while units_sold and revenue serve as supporting economic indicators.

---

## 4. Key Confounders and Structural Variables

Several variables affect outcomes independently of treatment and must be considered in the causal design:

| Variable | Role | Why it matters |
|---|---|---|
| promotion | observed confounder | Promotions reduce prices and can increase units sold sharply |
| competitor_price | observed confounder | Competitor pricing changes demand elasticity and substitution behavior |
| seasonal_index | demand driver | Seasonal demand patterns affect sales across markets |
| day_of_week | demand driver | Weekly behavior impacts shopping volume |
| market_size_index | market characteristic | Markets differ in scale and baseline demand |
| region | fixed market characteristic | Regional structure may affect both exposure and sales behavior |
| price | mediator | Selling price is part of the causal pathway and not to be conditioned on when estimating total intervention effect |

Important note: price is not controlled as a direct covariate when estimating total policy effect because it is the mechanism through which treatment operates. Instead, we model the policy effect through treatment status and compare treated and synthetic counterfactuals.

---

## 5. Hypothesized Causal DAG

The causal structure is represented as:

```mermaid
flowchart TD
    subgraph Exogenous_Market_Factors ["Exogenous Market Context"]
        Seasonality["Seasonality & Calendar\n(seasonal_index, day_of_week)"]
        MarketScale["Market Size & Fixed Characteristics\n(market_size_index, region)"]
        CompPrice["Competitor Pricing\n(competitor_price)"]
        Promo["Promotions / Discounts\n(promotion)"]
    end

    subgraph Intervention_Mechanism ["Policy & Mechanism"]
        Policy["Pricing Policy Intervention\n(Treated Markets × Post-July 1)"]
        Price["Selling Price per Unit\n(price)"]
    end

    subgraph End_Outcomes ["Business Outcomes"]
        Units["Sales Volume\n(units_sold)"]
        Revenue["Top-Line Sales\n(revenue)"]
        Profit["Gross Profit\n(gross_profit)"]
    end

    MarketScale --> Units
    MarketScale --> Revenue
    MarketScale --> Profit
    MarketScale -.->|Selection/Assignment| Policy

    Seasonality --> CompPrice
    Seasonality --> Promo
    Seasonality --> Units
    Seasonality --> Revenue
    Seasonality --> Profit

    Promo --> Price
    Promo --> Units
    CompPrice --> Units

    Policy -->|Direct Implementation| Price
    Price --> Units
    Price --> Revenue
    Price --> Profit

    Units --> Revenue
    Units --> Profit

----------------------------------------------------------------------------------------------------------------------

 - 


> 
> 
> ## Aniket — Week 3 Deliverables
#  Aniket — DOUBLE MACHINE LEARNING, VALIDATION & INTEGRATION**
## Files added



- `src/dml_pipeline.py`: cross-fitted partially linear DML baseline for three outcomes.
- `src/dml_diagnostics.py`: dataset, treatment and panel-key diagnostics.
- `notebooks/02_dml_analysis.ipynb`: interactive analysis entry point.
- `tests/test_dml_pipeline.py`: unit tests for input validation and fold/overlap helpers.
- `docs/dml_methodology.md`: method, assumptions, limits and run commands.
- `reports/dml_input_diagnostics.json`: diagnostics from the supplied processed CSV.
- `reports/dml_run/`: actual exploratory outputs generated from the supplied simulated data.

## Run from the `data preparation` directory

```bash
pip install -r requirements.txt
python src/dml_diagnostics.py --input "data/processed/cleaned regional market transactions.csv" --output reports/dml_input_diagnostics.json
python src/dml_pipeline.py --input "data/processed/cleaned regional market transactions.csv" --output-dir reports/dml_run --folds 5
python -m pytest -q
```

## Current verification
- Input audit observed 87,600 rows, 20 markets, 12 products, dates 2024-01-01 to 2024-12-30, and no duplicate market-product-date keys.
- Unit tests: 4 passed in the current environment.
- The DML pipeline ran successfully for all three outcomes and wrote exploratory outputs.

## Critical caveats
- The data are simulated.
- Estimates are exploratory, not validated causal effects.
- The overlap flag is a screening heuristic, not proof of positivity.
- IID-only standard errors do not account for panel dependence and are not final inferential intervals.
- The causal design must be reviewed because treatment is assigned to four markets after a common date.
- Do not claim the entire project or final deployment is complete based on these module runs.

 


This package contains the Week 3 DML module files. It does not include the source dataset; run it against the processed CSV in the main project repository.

## Run from the main project's `data preparation` directory

Install dependencies:
```bash
pip install -r requirements.txt
```
Run diagnostics:
```bash
python src/dml_diagnostics.py --input "data/processed/cleaned regional market transactions.csv" --output reports/dml_input_diagnostics.json
```
Run the DML baseline:
```bash
python src/dml_pipeline.py --input "data/processed/cleaned regional market transactions.csv" --output-dir reports/dml_run --folds 5
```
Run tests:
```bash
python -m pytest -q
```

**Important:** Source data are simulated. Estimates are exploratory and not validated causal findings. IID-only standard errors are not suitable as final inference for this panel. Read `docs/dml_methodology.md` before interpreting results.



# Harish Work Package

# Harish —Testing, Dashboard & Documentation Package

## Included dashboard
This package includes a runnable Streamlit dashboard configured with the project's current **simulated development dataset** and available SCM/DML artifacts. It includes:

- Executive overview and filterable descriptive trends
- Market- and product-level summaries
- Existing Synthetic Control diagnostics, weights, and plots
- Existing exploratory DML estimates and their warnings
- Data quality checks, missingness summary, and CSV exports

**Important:** The data is simulated. DML estimates are exploratory and not validated for final causal inference. Do not present these as real-world business results. Existing SCM diagnostics should also be reviewed with their methodological assumptions. Dashboard display is not proof of causal validity.

## Run on Windows
1. Extract this ZIP.
2. Open the extracted folder in VS Code.
3. Open Terminal in VS Code and run:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

If PowerShell blocks activation, use Command Prompt, or run `.venv\\Scripts\\python -m pip install -r requirements.txt` and `.venv\\Scripts\\streamlit run app/streamlit_app.py` without activating.

## Project data
The dashboard reads its bundled data from `data/`. To use an updated dataset, replace `data/cleaned_regional_market_transactions.csv` only after confirming schema and data permissions. SCM and DML outputs are loaded from their corresponding CSV files when present.

## Tests
```bash
python -m pytest tests/test_dashboard_utils.py -v
```

Passing unit tests verify the tested code paths only; they do not validate causal identification or the entire dashboard experience on every machine.

## Suggested ownership / status
This is a starter implementation for Harish's testing, dashboard support, and documentation responsibility. Harish should run it locally, verify the displayed outputs, record issues, and commit the genuine changes to his assigned branch. Confirm exact branch name and merge process with the team.
