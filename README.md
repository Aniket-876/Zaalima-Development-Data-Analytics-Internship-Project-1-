# Causal Inference & Synthetic Control Engine for Algorithmic Pricing

> **Project context:** Zaalima Development — Data Analytics Internship  
> **Project status:** Development / exploratory validation  
> **Data status:** The currently documented dataset is simulated development data. It must not be presented as real-world evidence. Confirm with the project mentor whether simulated data is acceptable for the final submission or whether an approved real dataset is required.

## Table of Contents

- [1. Overview](#1-overview)
- [2. Business Problem](#2-business-problem)
- [3. Objectives](#3-objectives)
- [4. Scope and Important Caveats](#4-scope-and-important-caveats)
- [5. Current Data](#5-current-data)
- [6. Methodology](#6-methodology)
- [7. Project Architecture](#7-project-architecture)
- [8. Streamlit Dashboard](#8-streamlit-dashboard)
- [9. Repository Structure](#9-repository-structure)
- [10. Technology Stack](#10-technology-stack)
- [11. Setup and Execution](#11-setup-and-execution)
- [12. Testing and Validation](#12-testing-and-validation)
- [13. Interpreting Results](#13-interpreting-results)
- [14. Known Limitations and Risks](#14-known-limitations-and-risks)
- [15. Recommended Next Steps](#15-recommended-next-steps)
- [16. Team Workflow and Contributions](#16-team-workflow-and-contributions)
- [17. Documentation Guide](#17-documentation-guide)
- [18. Disclaimer](#18-disclaimer)

## 1. Overview

This project explores how to estimate the effect of an algorithmic pricing intervention using causal-inference techniques. It combines panel-style market and product data, Synthetic Control diagnostics, a Double Machine Learning (DML) pipeline, data-quality checks, and an interactive Streamlit dashboard.

The intended workflow is:

**Business question → data ingestion → data quality and preparation → causal design → Synthetic Control and DML analysis → diagnostics and validation → dashboard → business interpretation.**

The project is an analytical decision-support prototype. Its current outputs are exploratory and should not be treated as confirmed causal findings until the data lineage, treatment design, assumptions, and inference methods have been independently validated.

## 2. Business Problem

A business may change prices in selected markets and want to understand whether the change affected outcomes such as revenue, units sold, or gross profit. A simple before-and-after comparison can be misleading because outcomes may also change due to seasonality, promotions, competitor prices, market-specific trends, and other time-varying factors.

The project investigates whether a counterfactual comparison can help estimate what might have happened in treated markets if the pricing intervention had not occurred.

### Core question

> What is the estimated effect of a pricing intervention on selected business outcomes, compared with a defensible estimate of the counterfactual outcome without the intervention?

## 3. Objectives

- Prepare and validate market-product-date observations.
- Document the treatment, comparison group, intervention date, and causal assumptions.
- Explore Synthetic Control methods and donor-market diagnostics.
- Implement a DML-style estimation pipeline with preprocessing and cross-fitting.
- Report data-quality and model diagnostics alongside estimates.
- Present selected data and precomputed analytical outputs in a Streamlit dashboard.
- Make assumptions, uncertainty, limitations, and reproducibility requirements explicit.

## 4. Scope and Important Caveats

### In scope

- Data inspection, cleaning, and quality checks.
- Exploratory analysis of price, competitor price, promotion, units sold, revenue, and gross profit.
- Synthetic Control and DML prototype workflows.
- Diagnostics, tests, documentation, and dashboard presentation.

### Not established by the current implementation

- A validated real-world causal effect of algorithmic pricing.
- Proof that a price change caused the observed changes in business outcomes.
- Production readiness or deployment to a production environment.
- Valid final statistical inference from the exploratory DML output.

The current dataset and DML artifacts are labelled as simulated/exploratory. Any external presentation must preserve these qualifications.

## 5. Current Data

The project files document a simulated panel-style dataset with approximately **87,600 rows**, covering **20 markets**, **12 products**, and dates from **1 January 2024 to 30 December 2024**. The final calendar day of the leap year is not present in the documented date range.

The simulated intervention is documented as an **8% price increase** in markets **M001–M004**, beginning **1 July 2024**. These are development assumptions, not observed real-world events.

### Main fields

| Field | Meaning |
|---|---|
| `market_id` | Market identifier |
| `region` | Market region/metadata |
| `product_id` | Product identifier |
| `category` | Product category |
| `date` | Observation date |
| `treated_market` | Indicator for designated treated markets |
| `treatment_date` | Configured intervention date |
| `treatment` | Treatment-period indicator used in the analysis data |
| `price` | Product price |
| `competitor_price` | Competitor-price feature |
| `promotion` | Promotion indicator/feature |
| `day_of_week` | Day-of-week feature |
| `seasonal_index` | Simulated seasonal feature |
| `units_sold` | Units sold outcome |
| `revenue` | Revenue outcome |
| `unit_cost` | Unit cost feature |
| `gross_profit` | Gross-profit outcome |

The cleaned dataset may also include missingness/imputation flags. Consult the data dictionary and cleaning script for the exact definitions and types used in the current files.

### Data-use note

The dataset is synthetic. Its patterns and model estimates cannot establish what would happen in a real market. Before using a real dataset, document its source, licence/permission, extraction date, coverage, data dictionary, and any privacy or confidentiality restrictions.

## 6. Methodology

### 6.1 Data preparation and quality

The preparation workflow checks fields, types, missing values, duplicate market-product-date keys, valid dates and values, treatment consistency, and the arithmetic relationship between revenue, costs, and gross profit. Cleaning and validation outputs are stored in the project data and reports directories.

Validation reports should be regenerated from the current data and code before a review. A saved report marked `PASS` is not, by itself, proof that the check was rerun against the latest files.

### 6.2 Causal design

The analysis must clearly define:

- The unit of observation and outcome.
- Which markets receive treatment and when treatment starts.
- Which markets are eligible as controls/donors.
- Pre-intervention and post-intervention periods.
- Potential confounders, concurrent events, spillovers, and market/time shocks.
- The assumptions required to interpret estimates causally.

A causal DAG and written assumptions should be reviewed before interpreting model outputs.

### 6.3 Synthetic Control

Synthetic Control constructs a weighted combination of donor markets intended to approximate the treated market before the intervention. Post-intervention differences between the treated market and its synthetic counterpart can then be examined.

Important diagnostics include:

- Pre-intervention fit and pre-period mean squared prediction error (MSPE).
- Donor eligibility and estimated donor weights.
- Post/pre MSPE ratios.
- Placebo or permutation comparisons where appropriate.
- Sensitivity to donor choices, time windows, and specifications.

A post/pre MSPE ratio is a fit diagnostic; it is **not a p-value** and does not by itself prove a causal effect. The current repository contains a Synthetic Control script that generates market series internally. Confirm that saved diagnostic and weight artifacts were generated from the intended canonical project dataset before reporting them as results for that dataset.

### 6.4 Double Machine Learning (DML)

The current DML pipeline includes input checks, preprocessing, date-block cross-fitting, outcome and treatment models, a partialling-out estimate, and an overlap screen. The stored exploratory output includes estimates for `gross_profit`, `revenue`, and `units_sold`.

DML relies on defensible treatment assignment assumptions, suitable covariates, overlap, and an appropriate inference strategy. The current outputs are labelled exploratory and unvalidated. The pipeline also warns that IID-only standard errors are not suitable for final inference when market, product, and time observations are dependent.

Before presenting DML results as evidence, review the treatment assignment mechanism, covariate timing, market and time dependence, overlap, standard-error strategy, robustness checks, and estimand definition. Do not assume DML and Synthetic Control estimates are directly comparable unless their estimands and assumptions are aligned.

## 7. Project Architecture

At a high level, the repository contains:

1. **Data layer** — raw, cleaned, and processed panel data.
2. **Preparation layer** — data cleaning and validation utilities.
3. **Analysis layer** — Synthetic Control and DML pipelines plus diagnostics.
4. **Artifact layer** — saved weights, diagnostics, estimates, and report outputs.
5. **Presentation layer** — Streamlit dashboard that displays data and saved analytical artifacts.
6. **Quality layer** — unit tests and documentation.

The dashboard currently reads precomputed model artifacts. Changing dashboard filters should not be described as rerunning or refitting the causal models unless that behavior is explicitly implemented and tested.

## 8. Streamlit Dashboard

The current Streamlit app contains six tabs:

1. **Overview** — high-level project and metric overview.
2. **Market & Product** — market/product exploration.
3. **Pricing & Promotions** — pricing and promotion patterns.
4. **Synthetic Control** — saved Synthetic Control outputs and diagnostics.
5. **DML Diagnostics** — saved DML estimates and diagnostic information.
6. **Data Quality** — data-quality indicators and validation information.

The sidebar provides filters for date range, markets, products, categories, metric, and daily/weekly/monthly grain. Because model outputs are precomputed, dashboard filtering primarily changes displayed data and views; it does not automatically rerun the SCM/DML analysis.

## 9. Repository Structure

The main project files identified in the supplied repository include:

```text
Zaalima-Development-Data-Analytics-Internship/
└── data preparation/
    ├── app/
    │   └── streamlit_app.py
    ├── src/
    │   ├── clean pricing data.py
    │   ├── dashboard_utils.py
    │   ├── dml_pipeline.py
    │   ├── dml_diagnostics.py
    │   └── run_synthetic_control.py
    ├── data/
    │   ├── raw/
    │   ├── processed/
    │   ├── scm_diagnostics_mspe.csv
    │   ├── estimated_scm_weights.csv
    │   └── dml_estimates_exploratory.csv
    ├── reports/
    │   ├── validation results.csv
    │   ├── dml_run/
    │   └── dml_week3_status.md
    ├── docs/
    │   ├── causal_design.md
    │   ├── donor_markets.md
    │   ├── dml_methodology.md
    │   ├── synthetic_control.md
    │   └── validation_diagnostics.md
    ├── tests/
    │   ├── test_dml_pipeline.py
    │   └── test_dashboard_utils.py
    └── requirements.txt
```

This is a guide to the key files identified during the project audit, not a guarantee that every branch or local copy has exactly this structure. Use the actual checked-out branch as the source of truth and remove or document duplicate/legacy files during repository cleanup.

## 10. Technology Stack

The project uses or references:

- Python
- Pandas and NumPy
- scikit-learn for preprocessing and machine-learning components
- SciPy/Statsmodels where used by analysis scripts
- Matplotlib and Seaborn for plots
- Streamlit for the dashboard
- Plotly for interactive charts
- pytest for automated tests
- Git and GitHub for version control and collaboration

**Dependency note:** the existing `requirements.txt` was found to omit some libraries imported by the app and analysis code. Verify imports in the current branch and update the dependency file before claiming that a fresh installation is reproducible. Pin or constrain versions consistently with the tested environment.

## 11. Setup and Execution

Run commands from the `data preparation` directory. The repository's dependency file may need to be completed before a fresh environment can run all components successfully.

### 11.1 Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- Windows PowerShell: `\.venv\Scripts\Activate.ps1`
- Windows Command Prompt: `.venv\Scripts\activate.bat`
- macOS/Linux: `source .venv/bin/activate`

### 11.2 Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If an import fails because a required package is absent, verify which project module imports it, add the correct dependency to `requirements.txt`, and test the setup again. Do not rely on a committed local `.venv`; virtual environments should be created locally and excluded from version control.

### 11.3 Run the dashboard

```bash
streamlit run app/streamlit_app.py
```

This command assumes Streamlit and all app dependencies are installed. A successful launch should be recorded only after it has actually been tested in the current environment.

### 11.4 Run the tests

```bash
python -m pytest -q
```

### 11.5 Run analysis scripts

Review each script's current CLI/options and input/output paths before execution. In particular, confirm that Synthetic Control reads the intended project dataset and that rerunning scripts will not silently overwrite reviewed artifacts. Record the exact command, environment, input data version, timestamp, and output paths in the experiment log.

## 12. Testing and Validation

During a previous audit of the supplied project, **10 unit tests passed** in the available audit environment. This result applies to those tests and that environment only; it does not establish that the complete dashboard, clean installation, all data checks, or causal methodology has been end-to-end validated.

Recommended validation layers:

- **Data tests:** schema, key uniqueness, missingness, date coverage, valid ranges, treatment consistency, and derived-metric arithmetic.
- **Unit tests:** individual preprocessing, diagnostics, and dashboard utility functions.
- **Integration tests:** data-to-model and model-to-dashboard artifact compatibility.
- **Reproducibility tests:** clean environment installation and repeatable outputs.
- **Causal validation:** pre-fit, placebo/sensitivity checks, overlap, assumptions, and appropriate uncertainty estimates.
- **UI tests:** verify the app launches and filters/plots behave as documented.

Record test results with the exact commit and data version. Do not claim tests passed unless they were run against the version being submitted.

## 13. Interpreting Results

When communicating results, separate:

1. **Observed descriptive patterns** — what the dataset shows.
2. **Model estimates** — outputs produced by a specified method.
3. **Diagnostic evidence** — checks about fit, overlap, or sensitivity.
4. **Causal conclusions** — claims that are justified only if assumptions and inference are credible.

The current DML estimates and Synthetic Control diagnostics should be described as exploratory development outputs until the data lineage and methodology are validated. Include outcome units, treatment definition, estimation window, uncertainty, assumptions, and limitations with every reported estimate. Do not invent business impact, statistical significance, or ROI.

## 14. Known Limitations and Risks

- The current dataset is simulated development data, not verified real market data.
- The documented period ends on 30 December 2024, not 31 December.
- The Synthetic Control script generates series internally; artifact lineage to the canonical panel needs confirmation.
- DML outputs are exploratory and explicitly not validated for final inference.
- The treatment assignment, covariate specification, overlap diagnostics, and panel-aware uncertainty approach require further review.
- Saved validation reports should be regenerated against the exact submission version.
- The dashboard displays precomputed model artifacts and does not automatically refit models when filters change.
- The dependency list requires review for a reproducible fresh setup.
- Duplicate datasets, duplicate documentation files, and a committed virtual environment may cause confusion and should be cleaned up carefully.

## 15. Recommended Next Steps

### Priority 0 — resolve before presenting results

- Obtain mentor confirmation on whether simulated data is acceptable for final evaluation.
- Trace Synthetic Control inputs and regenerate artifacts from the approved canonical dataset, if required.
- Review the causal DAG, treatment assignment, covariates, donor eligibility, overlap, and inference approach.
- Keep all estimates explicitly labelled exploratory until validation supports stronger claims.

### Priority 1 — reproducibility and delivery quality

- Complete and test `requirements.txt`.
- Remove `.venv` from version control and add it to `.gitignore`.
- Standardize canonical data and artifact paths; document any retained duplicates.
- Rerun data validation and tests on the final branch/commit.
- Test the dashboard from a clean environment and document actual results.
- Reconcile status reports with verifiable code, test, artifact, and commit evidence.

### Priority 2 — strengthen the final handover

- Add an architecture diagram and data-flow diagram.
- Add a data dictionary and experiment log with data/version provenance.
- Provide an executive summary with cautious, evidence-based insights.
- Document each member's actual contribution and reviewed deliverables.
- Add limitations, reproducibility instructions, and a short demo script.

## 16. Team Workflow and Contributions

Use the team's agreed Git workflow and the latest official mentor instructions. Keep work on the assigned member branch, commit meaningful changes, and merge through the agreed integration process after review. Do not commit generated files, local environments, or work that has not been checked.

A suggested contribution record is:

| Member | Responsibility area | Evidence to record |
|---|---|---|
| Fatima | Data sourcing, quality, cleaning, EDA | Source notes, cleaned data, data dictionary, validation output, commits/PRs |
| Shrusti | Causal design and Synthetic Control | DAG, donor selection, weights, pre-fit/MSPE and placebo/sensitivity diagnostics |
| Aniket | DML pipeline, diagnostics, integration support | Code, tests, experiment logs, reviewed estimates and commits/PRs |
| Harish | Testing, dashboard support, documentation/demo | Verified tests, dashboard checks, setup instructions, architecture and report |

This table is a proposed working map based on the team's discussed division of work, not proof that any task has been completed or an official assessment of individual performance. Update it using actual ownership, evidence, and the latest team agreement.

## 17. Documentation Guide

The following documents should be kept aligned with the code and data:

- `causal_design.md` — treatment/control definitions, DAG, assumptions, confounders, and estimand.
- `dml_methodology.md` — preprocessing, nuisance models, cross-fitting, diagnostics, inference, and limitations.
- `synthetic_control.md` — donor selection, weights, fit metrics, placebo/sensitivity analysis, and assumptions.
- `donor_markets.md` — donor inclusion/exclusion rules and rationale.
- `validation_diagnostics.md` — checks, results, run date, data version, and known failures.
- `reports/` — generated outputs and experiment/status records with reproducible provenance.

A documentation statement should be considered complete only when its supporting code, data, test, or output can be identified and reproduced.

## 18. Disclaimer

This repository is an internship development project and analytical prototype. Its simulated data and exploratory estimates are intended for learning and methodological development. They should not be used to make real pricing decisions or represented as validated causal evidence without approved data, reviewed assumptions, reproducible diagnostics, and an appropriate inference strategy.

---

**Before final submission:** confirm the official mentor requirements, approved dataset, current branch, complete dependencies, reproducible model inputs/outputs, test evidence, and final report status. This README describes the state identified during a project audit and should be updated whenever the implementation changes.
