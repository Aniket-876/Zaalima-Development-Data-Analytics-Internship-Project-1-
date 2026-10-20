# EDA Summary

Full code and outputs: `notebooks/01_eda.ipynb`. Charts are in `docs/figures/`.

> All results describe **simulated** data and **associations only**. A chart does not prove that the price change caused a change in sales.

## Key observations

**1. Strong seasonality.** Monthly revenue peaks in March (about 20.1 million) and bottoms out in September (about 15.4 million). Daily average sales track the simulated `seasonal_index` almost perfectly (correlation about 1.00), so much of the year's movement is seasonality, not price.
![Monthly totals](figures/fig01_monthly_totals.png)

**2. Weekday pattern.** Average units are highest on Monday (77.0) and lowest on Thursday and Friday (70.2).
![Units vs seasonality](figures/fig02_units_vs_seasonality.png)

**3. Treated and control markets look alike before 1 July.** The monthly treated-to-control ratio of average units stays between 1.00 and 1.01 from January to June. After 1 July the price in treated markets steps up by about 8% (price relative to baseline about 0.99 → 1.07) while the controls stay flat. Units fall in both groups; treated markets fall further (about −17.8 units against −11.3 for controls). The raw gap of about 6.5 units (8% of the treated pre-period level) is a **descriptive before/after difference, not a causal estimate**. For revenue the gap is only about 1.8%, because the higher price offsets the lost units.
![Treated vs control](figures/fig03_treated_vs_control.png)

**4. Markets differ mainly by size.** Correlation between `market_size_index` and average units is 0.997. The treated markets are mixed: M001 (1.40) and M004 (1.29) are large, M002 (1.01) medium, M003 (0.73) small.
![Markets](figures/fig04_markets.png)

**5. Products differ mainly by price level.** The five most expensive products (P006, P008, P011, P007, P005) are also the five biggest revenue earners. Gross margin is about 38% for every product.
![Products](figures/fig05_products.png)

**6. Price versus sales is confounded.** Raw correlation of price relative to baseline with units is −0.27. Within a market-product series, the estimated slope is about −2.5 with all rows, −1.9 without promotion days and −1.3 without promotion days or treated markets, so it cannot be read as a price elasticity. Promoted days are about 7% cheaper than non-promoted days and sell about 34% more units (96.0 vs 71.6).
![Price vs units](figures/fig06_price_vs_units.png)

**7. Competitor gap.** Our price is on average about 1.7% below the competitor's. Sales are slightly higher when the competitor is relatively more expensive (correlation 0.12), but the gap depends on our own price, so this is a rough association.
![Competitor gap](figures/fig07_competitor_gap.png)

**8. Promotions** run on about 8% of rows, evenly across months, regions and products, with no obvious pile-up in treated markets or after July.
![Promotions](figures/fig08_promotions.png)

**9. Distributions.** Prices and revenue are right-skewed because of the product mix. Only 27 values are more than 4 standard deviations from their product's mean; all are plausible and were kept.
![Distributions](figures/fig09_distributions.png)

## Limitations

- Simulated data; no real-world evidence.
- Only 4 treated markets, all starting on one date, and none in Region_5.
- 60 competitor prices and 30 promotion values are missing (flagged, not imputed); 31 Dec 2024 is missing for every market.
- Raw comparisons ignore promotions, market size and product mix.
