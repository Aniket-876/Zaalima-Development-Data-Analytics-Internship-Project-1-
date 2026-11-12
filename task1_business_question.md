# Task 1: Business Question and Analysis Period

## 1. Project Context & Background
This project evaluates the causal impact of an algorithmic pricing intervention implemented across regional retail markets. The central business trade-off in price interventions is the tension between margin expansion and demand contraction:
* Raising prices increases gross margin and revenue per unit sold.
* However, higher prices can induce consumer price resistance and depress unit sales volume (`units_sold`).
* Therefore, pricing interventions cannot be evaluated solely on gross revenue; **profitability (`gross_profit`) and volume demand elasticity must be evaluated jointly**.

> **Note on Data Provenance:** As documented in the project specifications, this analysis is performed on a simulated dataset (`87,600` rows across 20 markets and 12 products). Results demonstrate causal methodology and counterfactual evaluation frameworks rather than real-world commercial findings.

---

## 2. Core Business Research Question
> **Primary Research Question:**  
> *"Did the approximately 8% algorithmic price increase introduced on **July 1, 2024**, in markets **M001, M002, M003, and M004** causally change **gross profit**, **revenue**, and **units sold** compared to what would have occurred under the counterfactual scenario without the intervention?"*

---

## 3. Intervention Specification & Target Units

| Dimension | Specification | Notes & Validation |
| :--- | :--- | :--- |
| **Intervention** | Algorithmic selling price increase (~+8%) | In treated markets, price relative to baseline rose from ~0.99 pre-July to ~1.07 post-July, while remaining flat in controls. |
| **Treated Markets** | **M001, M002, M003, M004** | 4 out of 20 total markets received the intervention simultaneously (`treated_market = 1`). |
| **Candidate Controls** | **M005 through M020** | 16 untreated regional markets maintained baseline pricing rules (`treated_market = 0`). |
| **Intervention Date** | **July 1, 2024** | The binary treatment indicator `treatment = 1` activates exclusively for treated markets on or after this date. |
| **Observation Level** | `market_id` × `product_id` × `date` | High-frequency panel encompassing 12 distinct products across 4 merchandise categories. |

---

## 4. Empirical Outcome Metrics

### Primary Outcome Metric
* **`gross_profit`**: Calculated as:
  $$\text{gross\_profit} = \text{revenue} - (\text{unit\_cost} \times \text{units\_sold})$$
  *Represents the ultimate business bottom-line objective to determine if margin expansion offsets volume reductions.*

### Secondary Outcome Metrics
* **`units_sold`**: Total daily units purchased per product. Direct empirical proxy for demand response and price elasticity.
* **`revenue`**: Total daily sales value ($\text{price} \times \text{units\_sold}$, subject to recorded rounding differences). Measures top-line performance.

---

## 5. Analysis Time Horizon & Empirical Windows

The transaction log encompasses daily records for calendar year 2024 (with December 31 absent from the dataset).

```
Pre-Treatment Period (182 Days)                  Post-Treatment Period (183 Days)
[2024-01-01 -------------------- 2024-06-30] | [2024-07-01 -------------------- 2024-12-30]
<------------- Baseline / Training ---------> | <------------- Treatment Effect Evaluation -->
                                              ^
                                    Treatment Enacted (July 1)
```

### 1. Pre-Treatment Period
* **Date Range:** **January 1, 2024 – June 30, 2024** (182 calendar days).
* **Operational Purpose:**
  1. Measure baseline pre-intervention trends across treated and donor markets.
  2. Verify parallel trends and pre-July co-movement across candidate control groups.
  3. Fit predictive weights for Synthetic Control Method (SCM) benchmarks.

### 2. Post-Treatment Period
* **Date Range:** **July 1, 2024 – December 30, 2024** (183 calendar days).
* **Operational Purpose:**
  1. Quantify the immediate and medium-term Average Treatment Effect on the Treated (ATT).
  2. Measure price elasticity decay, promotional interaction effects, and bottom-line gross profit changes.

docs: define causal inference problem statement
docs: define causal inference problem statement
