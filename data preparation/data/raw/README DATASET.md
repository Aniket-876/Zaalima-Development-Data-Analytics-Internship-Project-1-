# Causal Pricing Starter Dataset — SIMULATED DATA

IMPORTANT: This is simulated development data. It is NOT real company data, NOT an official Zaalima dataset, and NOT empirical evidence.

Files:
- regional_market_transactions.csv: daily market-product observations for 20 markets and 12 products in 2024.
- market_metadata.csv: market metadata, including simulated treatment assignment/date.
- product_metadata.csv: product metadata and baseline price/demand.

Key fields include date, market_id, product_id, price, competitor_price, promotion, units_sold, revenue, treated_market, treatment_date, treatment, region, unit_cost, and gross_profit.

Simulated intervention: four markets receive an 8% price increase from 2024-07-01. Promotions, seasonality, market size, and noise are also simulated. A small number of missing values are intentionally included for data-quality checks.

Any estimates from these data must be labelled simulation/demo results, not real-world causal findings. Confirm with the mentor whether simulated data is acceptable for the final project or replace it with an approved real dataset.
