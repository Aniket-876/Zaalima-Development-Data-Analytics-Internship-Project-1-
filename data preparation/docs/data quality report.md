# Data Quality Report — Causal Pricing Starter Dataset (SIMULATED)

**Files reviewed:** `regional_market_transactions.csv` (87,600 rows × 17 cols), `market_metadata.csv` (20 × 5), `product_metadata.csv` (12 × 4)
**Status:** Development use only. The data is simulated, so this is not the final dataset until the mentor confirms.
**Reproduce:** `python src/clean_pricing_data.py --input-dir data/raw --output-dir data/processed --report-dir reports`

## 1. Summary

The data is in good shape. There are **no duplicates, no ID mismatches, no invalid prices or sales values and no unparseable dates**, and the treatment columns are internally consistent. Six findings are recorded below; none required deleting a row.

| # | Issue | Rows | Impact if ignored | Handling decision | Remaining limitation |
|---|---|---|---|---|---|
| 1 | `region` blank | 30 (0.03%) | Rows would drop out of region-level grouping | **Filled** by lookup from `market_metadata` (1 market = 1 region, 0 conflicts); flagged | None; the fill is deterministic |
| 2 | `competitor_price` missing | 60 (0.07%) | Models using it would fail or silently drop rows; a guess could bias control-variable estimates | **Left missing**, `competitor_price_missing` flag added | 60 rows unusable in models that need competitor price unless the team chooses a rule |
| 3 | `promotion` missing | 30 (0.03%) | Filling with 0 would mislabel promoted high-sales days | **Left missing**, `promotion_missing` flag added | 30 rows cannot be classified as promoted or not |
| 4 | 2024-12-31 absent (365 of 366 days) | 240 rows' worth | Wrong "full-year" totals | Reported, no action | December has 30 days; same for every market, so no group bias |
| 5 | Type and format problems | all rows | Dates sorted as text; promotion float; blanks coerced | Converted (see §3) | None |
| 6 | `revenue` ≠ `price × units_sold` exactly | 83,504 (95%) | None: rounding only | **No action**, verified within tolerance | Do not recompute revenue from price |

### Row counts before and after cleaning

| File | Rows before | Rows after | Excluded | Columns before → after |
|---|---|---|---|---|
| regional_market_transactions.csv | 87,600 | 87,600 | 0 | 17 → 20 (3 flag columns added) |
| market_metadata.csv | 20 | 20 | 0 | 5 → 5 |
| product_metadata.csv | 12 | 12 | 0 | 4 → 4 |

Transformations applied: type conversion (dates, `promotion`), trimming/upper-casing of IDs and text (no values changed on this data), one lookup fill (`region`), three flag columns added, rows sorted by market, product, date. No exclusions.

## 2. Checks by file

### 2.1 regional_market_transactions.csv (main)

| Check | Result |
|---|---|
| Exact duplicate rows | 0 |
| Duplicate `market_id + product_id + date` | 0 |
| Panel balance (each market × product has same number of days) | Balanced, 365 days each |
| Date parsing / range | All valid, 2024-01-01 to 2024-12-30 |
| `day_of_week` matches `date` (0 = Monday) | 0 mismatches |
| Missing values | `region` 30, `competitor_price` 60, `promotion` 30. No row has more than one |
| `price`, `competitor_price` ≤ 0 | 0 |
| `units_sold` < 0 or = 0 | 0 (minimum is 21) |
| `revenue` < 0 | 0 |
| `unit_cost` ≥ `price` / `gross_profit` < 0 | 0 / 0 |
| `gross_profit = revenue − unit_cost × units` | Exact in every row |
| `category` vs product metadata, `region` vs market metadata | 0 conflicts |
| Statistical outliers (\|z\| > 4 within product) | price 10, competitor_price 8, units_sold 8, revenue 1, unit_cost 0. **Kept**, see §4 |

### 2.2 market_metadata.csv

| Check | Result |
|---|---|
| Missing / duplicate `market_id` | 0 / 0 |
| IDs in transactions but not metadata, and vice versa | None, 20 of 20 match |
| Treated markets without a date, controls with a date | 0 / 0 |
| `treated_market` and `treatment_date` vs transactions | Fully consistent |
| Blank `treatment_date` | 16 rows, all control markets (expected) |

### 2.3 product_metadata.csv

| Check | Result |
|---|---|
| Missing / duplicate `product_id` | 0 / 0 |
| IDs in transactions but not metadata, and vice versa | None, 12 of 12 match |
| Non-positive `base_price` / `base_demand` | 0 |
| `category` vs transactions | Fully consistent |

## 3. Issues in detail and how they were handled

**Issue 1: blank `region` (30 rows).** Each market belongs to exactly one region in `market_metadata`, and the 87,570 non-blank values agree with it with zero exceptions. Filling from the lookup is therefore a deterministic recovery, not a guess. The 30 rows are marked with `region_filled_from_metadata = 1`.

**Issue 2: missing `competitor_price` (60 rows).** The gaps are isolated single days (no two consecutive days are missing in any series) spread across all 20 markets, 11 products and both periods (13 rows in treated markets, 7 post-intervention). They look random, but I did not impute them because competitor price is a candidate control variable and a guessed value could bias estimates. Options for the team to choose from, in order of caution: (a) exclude these 60 rows from models that use `competitor_price`; (b) linear interpolation within the market × product series, using `competitor_price_missing` to run a sensitivity check; (c) leave as is for models that don't use the variable.

**Issue 3: missing `promotion` (30 rows).** Promotions matter here: promoted rows have prices about 7% lower and sell about 34% more units (96.0 vs 71.6 on average). Filling these with 0 would silently misclassify some promoted days, so they are **not** filled. 30 rows is only 0.03% of the data, so excluding them from promotion-adjusted models costs almost nothing. 9 are in treated markets, 2 are post-intervention.

**Issue 4: 2024-12-31 is missing.** The data covers 365 days, ending 2024-12-30, while 2024 has 366. This is the same for every market and product, so it does not bias the comparison. It is worth knowing if anyone computes "full-year" totals.




**Issue 5: types and formats.**
- `date` and `treatment_date` converted from text to proper dates (ISO format).
- `promotion` converted from float (0.0/1.0) to integer flag (needed so missing values are not silently coerced).
- ID and text columns trimmed and upper-cased (no changes were needed on this data, but the script handles it).
- `treatment_date` is blank in 70,080 rows (80%). This is **structural**, not missing data: those rows belong to control markets. It was deliberately left blank.

**Issue 6: revenue vs price × units.** Exact equality fails in 83,504 rows, but the largest gap is 0.95, and every gap is within the half-cent rounding of `price` multiplied by units. `revenue` was clearly computed from unrounded prices and then rounded. Nothing needs correcting. Don't recompute `revenue` from `price`, because that would change `gross_profit` reconciliation.

## 4. Things reviewed and deliberately not changed

- **Outliers (27 flagged value-cells).** These are statistical extremes within a product. They sit within the plausible range (no negative or implausible values), and a simulated price jump, promotions and noise can all produce them. Removing them would distort the treatment effect, so they were only reported.
- **Treatment columns** (`treated_market`, `treatment_date`, `treatment`). Not modified. They were checked for meaning:
  - `treated_market = 1` only for M001–M004, always with `treatment_date = 2024-07-01`.
  - `treatment = 1` exactly when `treated_market = 1` and `date ≥ treatment_date`: 8,784 rows, 0 exceptions.
  - Control markets never have `treatment = 1`.
  - The price data agrees with the README: in treated markets, price relative to `base_price` goes from 0.994 before 1 July to 1.074 after (about +8%), while controls stay at 0.994.

## 5. Validation of cleaned output

14 of 14 checks pass (`reports/validation_results.csv`): row count preserved (87,600), no duplicate keys, no missing `region`, all IDs match metadata, dates valid, price > 0, `gross_profit` reconciles, treatment columns identical to the raw file, and flags match the remaining missing values.

## 6. Points for the team and the mentor

1. **Mentor confirmation (blocking for the final project):** is simulated data acceptable, or is a real dataset required? All results must be labelled simulation/demo until then.
2. **Modelling design (not data errors, but worth noting for the synthetic control step):** only 4 of 20 markets are treated (M001–M004, one each from Regions 1–4; Region_5 has none), and treated rows are 10% of the data. Treated markets include small and large ones (market size index 0.73–1.40), so the donor-pool choice will matter.
3. **Team decision on issues 2 and 3:** exclude, interpolate, or ignore the flagged rows, ideally the same way for every analysis.
4. Currency and units are not documented in the dataset; worth asking if reported figures need units.
