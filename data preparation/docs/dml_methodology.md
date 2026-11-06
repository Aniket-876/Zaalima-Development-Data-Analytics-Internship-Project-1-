# Aniket — Week 3 DML Methodology and Validation

## Purpose
Build a reproducible, cross-fitted Double Machine Learning (DML) development pipeline for the algorithmic pricing simulation. The primary outcome is `gross_profit`; `revenue` and `units_sold` are secondary outcomes.





## Input and design
- Unit: `market_id × product_id × date`.
- Intervention: `treatment = 1` for treated markets M001–M004 from 2024-07-01 onward.
- Current dataset is simulated; results are demonstrations, not real business evidence.
- Features currently used for nuisance models: `competitor_price`, `promotion`, `seasonal_index`, `day_of_week`, `category`, `region`, and `product_id`.
- Selling `price`, `treated_market`, outcome-derived fields, and `treatment_date` are excluded from the feature matrix to avoid controlling directly for the intervention mechanism or leaking assignment information into nuisance models. This feature set must be reviewed against the approved DAG before substantive interpretation.




## Implementations

`src/dml_pipeline.py` performs input validation, date-block cross-fitting, fold-specific preprocessing, Ridge outcome prediction, logistic-regression treatment propensity prediction, residualization, and an exploratory partially linear DML point estimate. It writes out-of-fold predictions and diagnostics so the run can be inspected.




## Validation requirements
1. Confirm required columns, binary treatment, valid dates, and unique market-product-date keys.
2. Inspect missingness and verify imputation occurs inside each training fold.
3. Inspect propensity distributions and overlap; the threshold-based overlap check is only a screen.
4. Verify the treatment indicator is defined consistently with the documented rollout.
5. Review potential market/time shocks, spillovers, unobserved confounding, and repeated-panel dependence.
6. Compare specifications and document unstable or failed checks.
7. Keep Synthetic Control and DML estimands separate unless their definitions and assumptions are compatible.



## Important limitations
- Treatment is tied to treated-market membership and the post-July period, so identification and overlap require careful review.
- Cross-fitting by date blocks prevents all rows from the same date appearing in both train and test folds, but it does not by itself solve panel dependence or causal identification.
- The reported standard error is explicitly IID-only and must not be used as final panel inference. A mentor-approved panel-aware inference method is required before publishing confidence intervals.
- The overlap screen is not proof of positivity.
- The dataset is simulated. Never present estimates as real commercial effects.

## Run
From the `data preparation` directory:

```bash
pip install -r requirements.txt
python src/dml_diagnostics.py --input "data/processed/cleaned regional market transactions.csv"
python src/dml_pipeline.py --input "data/processed/cleaned regional market transactions.csv" --output-dir reports/dml_run --folds 5
pytest -q
```

## Output files
- `reports/dml_input_diagnostics.json`
- `reports/dml_run/dml_estimates_exploratory.csv`
- `reports/dml_run/dml_oof_predictions.csv`
- `reports/dml_run/dml_diagnostics.json`
- `reports/dml_run/dml_validation_report.md`

These outputs are only considered produced after commands have actually run successfully.
