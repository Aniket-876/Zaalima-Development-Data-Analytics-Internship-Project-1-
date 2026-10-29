# Architecture and Workflow

## End-to-end flow

1. **Data preparation (Fatima):** source/permission check, data dictionary, data quality report, reproducible cleaning and EDA.
2. **Causal design and Synthetic Control (Shrusti):** define intervention, outcome and period; document DAG and assumptions; select donor markets; estimate weights and evaluate pre-treatment fit/placebos where appropriate.
3. **DML and integration (Aniket):** define estimand and covariates with the team; implement preprocessing, nuisance models and cross-fitting; assess overlap, leakage, uncertainty and robustness; publish a documented model interface.
4. **Testing, dashboard and documentation (Harish):** validate inputs and model outputs; track bugs; display only available and traceable outputs; maintain run instructions and report.

## Dashboard data flow

CSV → schema/date validation → interactive filters → descriptive KPIs and charts → filtered CSV download.

The current dashboard does **not** independently estimate causal effects. Synthetic Control and DML outputs must be separately generated, validated by their owners, and integrated only through agreed input/output contracts.

## Suggested integration contract

- Input transaction grain: market × product × day.
- Required descriptive fields: `date`, `market_id`, `product_id`, `treated_market`, `treatment`, `price`, `units_sold`, `revenue`, `gross_profit`.
- Synthetic Control output (agree with Shrusti): date, treated outcome, synthetic outcome, treatment date, donor weights and fit diagnostics.
- DML output (agree with Aniket): estimand/outcome/treatment/covariates, point estimate, uncertainty if supported, sample size, diagnostic status, assumptions and limitations.
- All outputs should carry data source/version, run date, and simulated/demo label where applicable.
