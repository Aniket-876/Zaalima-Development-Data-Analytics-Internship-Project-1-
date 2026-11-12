# Data Preparation: Causal Inference & Synthetic Control for Algorithmic Pricing

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
