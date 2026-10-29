# DML exploratory run report

> **Simulated development data only. Not real commercial evidence.**
> Estimates are exploratory. IID-only standard errors are not valid final inference for this panel.

## Results

| Outcome | Rows | Exploratory estimate | Overlap screen | Status |
|---|---:|---:|---|---|
| gross_profit | 87600 | -19.0018 | PASS_SCREEN_ONLY | EXPLORATORY_NOT_VALIDATED |
| revenue | 87600 | -45.7928 | PASS_SCREEN_ONLY | EXPLORATORY_NOT_VALIDATED |
| units_sold | 87600 | -3.44654 | PASS_SCREEN_ONLY | EXPLORATORY_NOT_VALIDATED |

## Interpretation and required checks

- Do not call these estimates validated causal effects.
- Review propensity overlap and the deterministic market-by-post treatment assignment.
- Review missingness, pre-treatment covariates, market/time shocks, and possible spillovers.
- Do not report the IID-only standard error as a final confidence interval.
- Confirm the dataset is approved for the final project; current files describe it as simulated.
- Keep DML and Synthetic Control estimates distinct unless estimands and assumptions are demonstrably compatible.
