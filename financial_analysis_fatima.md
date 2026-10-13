# Financial Analysis & Business Insights
**Project 1 – Causal Inference & Synthetic Control for Algorithmic Pricing**
**Author:** Fatima (Financial Analysis & Business Insights)

All numbers come from `notebooks/01_fatima_financial_analysis.ipynb`. Currency units are those of the dataset (not stated). Averages are per product per market per day.

---

## 1. Objective
To understand how a pricing change in one market (Market_A) affected sales, revenue and profit, and to check that the financial data is reliable before the team builds the Synthetic Control and Double Machine Learning (DML) models.

## 2. Data overview
- 2,700 rows, 14 columns: 5 markets (A–E) × 3 products (P001, P002, P003) × 180 days (1 Jan – 28 Jun 2024).
- **Treated market:** Market_A. **Comparison markets:** B, C, D, E.
- **Pricing change date:** 1 April 2024 (Jan–Mar is the pre-period with 91 days, Apr–Jun is the post-period with 89 days).
- Key fields: price, units_sold, unit_cost, competitor_price, promotion, revenue, total_cost, profit.

**Metric definitions:** revenue = price × units; profit = revenue − total cost; margin % = profit ÷ revenue; unit margin = price − unit cost; price gap = price − competitor price.

## 3. Financial consistency checks
| Check | Result |
|---|---|
| Missing values | None |
| Duplicate date-market-product rows | None |
| Complete panel (180 days × 5 markets × 3 products) | Yes, 2,700 rows |
| Price below unit cost | None |
| Zero or negative units / price | None |
| Revenue = price × units | Holds (max difference 0.30, rounding) |
| Total cost = unit cost × units | Holds (max difference 0.29, rounding) |
| Profit = revenue − total cost | Holds exactly |
| `treated_post` = treatment_market × post_period | Correct in every row |
| Unit cost stable across periods | Yes (about 21.99 before and after in all groups) |

**Conclusion:** the dataset is clean and financially consistent. The only differences are small rounding differences, which do not affect the analysis. Because unit costs did not change, profit changes come from price and volume, not from costs.

## 4. Key financial metrics
Average per market-product-day over the whole period:

| Market | Price | Units | Revenue | Profit | Margin % |
|---|---|---|---|---|---|
| Market_A | 39.43 | 36.57 | 1,310.11 | 582.79 | 44.6 |
| Market_B | 34.40 | 36.41 | 1,138.50 | 414.29 | 36.6 |
| Market_C | 35.80 | 37.10 | 1,201.91 | 468.26 | 39.1 |
| Market_D | 33.00 | 35.61 | 1,066.52 | 360.28 | 34.0 |
| Market_E | 35.08 | 37.17 | 1,183.64 | 446.11 | 37.9 |

Market_A was already the highest-priced and most profitable market before the change.

## 5. Impact of the pricing change

### Before vs after
| Group | Period | Price | Units | Revenue | Profit | Margin % |
|---|---|---|---|---|---|---|
| Other markets | Before | 34.55 | 35.51 | 1,113.84 | 409.21 | 36.9 |
| Other markets | After | 34.59 | 37.66 | 1,182.21 | 435.55 | 36.9 |
| Market_A | Before | 37.89 | 37.19 | 1,279.48 | 541.55 | 42.5 |
| Market_A | After | 40.99 | 35.94 | 1,341.42 | 624.96 | 46.8 |

Percentage change: Market_A price +8.2%, units −3.4%, revenue +4.8%, profit +15.4%. Other markets: price +0.1%, units +6.1%, revenue +6.1%, profit +6.4%.

### Difference-in-differences (quick estimate, per product-day)
| Metric | Effect |
|---|---|
| Price | +3.07 |
| Units sold | −3.41 |
| Revenue | −6.43 (about −0.5% of Market_A's pre-change revenue) |
| Total cost | −63.51 |
| **Profit** | **+57.08** |
| Margin | +4.2 percentage points |
| Price gap vs competitor | +3.21 (from +2.03 to +5.36) |

Over the 89-day post period (267 market-product-days in Market_A), this is an estimated **extra profit of about 15,240**, roughly 9% of Market_A's actual post-period profit (166,864). Revenue effect over the same period is about −1,717, so the gain comes from margin, not from higher sales.

### By product
| Product | Price effect | Units effect | Revenue effect | Profit effect |
|---|---|---|---|---|
| P001 (lowest price) | +1.75 | −5.23 | −24.05 | +38.62 |
| P002 | +3.01 | −2.87 | +1.94 | +62.79 |
| P003 (highest price) | +4.44 | −2.12 | +2.82 | +69.82 |

### Placebo test
Applying the same method to each untreated market gives profit effects of −7.96 to +6.41 (B −1.50, C +3.05, D −7.96, E +6.41). Market_A's +57.08 is far larger than all of them, so the result is unlikely to be random noise.

### Charts
See `reports/figures/`: `profit_trend.png`, `price_trend.png`, `units_trend.png`, `margin_trend.png`, `effect_by_product.png`, `placebo_test.png`.

## 6. Business interpretation
1. **The price increase worked financially.** Market_A raised price about 8%, lost only about 3% of units, and profit rose about 15%. Customers were not very sensitive to the higher price in this period.
2. **Profit rose through margin, not revenue.** Revenue was about flat relative to other markets, but fewer units cost less to supply, so profit improved.
3. **Higher-priced products gained most.** P002 and P003 produced larger profit gains. For P001, revenue fell relative to other markets (−24 per day) because volume dropped more (−5.2 units), although profit still rose. P001 is the most price-sensitive product.
4. **Market_A is now clearly more expensive than the competitor** (about 5 above, up from about 2). This is the main risk: a slow loss of customers may not appear in a three-month window.
5. **No cost explanation.** Unit costs and competitor prices did not change differently in Market_A, so they do not explain the gain.

## 7. Caveats and risks
- **Fewer promotions in Market_A after the change** (13% of rows before, 9% after, versus 14% to 11% in other markets). This may be part of the effect.
- **Market_A profit was already rising in March**, before the change, so part of the gain could be an existing trend. The monthly gap between Market_A and the others was 143 (Jan), 119 (Feb), 134 (Mar), then 193 (Apr), 192 (May), 182 (Jun). The step up after April is clear, but Synthetic Control should test this more carefully.
- **One treated market only.** A single market limits how confidently we can generalise.
- **Short post period** (about 3 months), so long-run effects are unknown.
- This is a simple difference-in-differences estimate. Shruti's Synthetic Control and Aniket's DML results should confirm or refine it.

## 8. Recommendations
1. Keep the higher price in Market_A and monitor units and competitor gap monthly.
2. Test the increase in one more market before wider rollout.
3. Be careful with P001 (low price, volume-sensitive); consider a smaller increase there.
4. Track promotions separately so their effect can be separated from the price effect.
5. Update this section with the Synthetic Control and DML estimates, and compare them with the quick estimate above (+57 profit per product-day).
