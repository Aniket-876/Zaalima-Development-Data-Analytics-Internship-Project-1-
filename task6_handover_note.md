# Task 6: Handover Note for Aniket

**To:** Aniket (Project Lead / Analytics Team)  
**From:** Antigravity Causal Analytics Team  
**Subject:** Technical Handover & Methodology Guide: Algorithmic Pricing Evaluation (M001–M004)  
**Date:** October 2026  

---

## 1. Executive Summary & Deliverables Inventory

This handover note summarizes the complete causal evaluation framework developed to assess the July 1, 2024, algorithmic price increase (+8%) across treated markets **M001–M004**. 

All project artifacts, configuration parameters, diagnostic reports, and reproducible code scripts have been compiled into this deliverable package:

| Deliverable | File Name | Key Purpose |
| :--- | :--- | :--- |
| **Task 1: Business Question & Windows** | `task1_business_question.md` | Research question, outcome definitions (`gross_profit`, `units_sold`, `revenue`), and empirical windows (Jan 1 – Jun 30 pre / Jul 1 – Dec 30 post). |
| **Task 2: Causal Design & Hypothesized DAG** | `task2_causal_design.md` | Confounder mapping (`promotion`, `competitor_price`, `seasonality`), causal assumptions, and DAG diagram. |
| **Task 3: Donor Market Selection** | `task3_donor_markets.md` | Inclusion/exclusion rationale for all 16 control markets (`M005–M020`), spillover screening, and scale matching. |
| **Task 4: Synthetic Control Implementation** | `task4_synthetic_control.md` | Mathematical formulation, non-negative simplex constraints ($\sum w_j = 1$), optimal weights, and trajectory series. |
| **Task 5: Validation & Diagnostics** | `task5_validation_diagnostics.md` | Pre-treatment MSPE/RMSPE metrics, boundary investigation, in-space placebo permutation tests, and sensitivity analysis. |
| **Python Execution Engine** | `run_synthetic_control.py` | Self-contained, automated script to run SCM, verify constraints, compute MSPE, and generate plots. |

---

## 2. Technical Parameter Specifications

* **Intervention Definition:** Algorithmic price increase of approximately **+8%** relative to product baselines.
* **Treated Units:** Markets **M001, M002, M003, and M004** ($N_{\text{treated}} = 4$).
* **Treatment Timing:** Universal start on **July 1, 2024**; constant treatment intensity across all 12 products.
* **Analysis Windows:**
  * Pre-treatment: `2024-01-01` to `2024-06-30` (182 days; baseline calibration).
  * Post-treatment: `2024-07-01` to `2024-12-30` (183 days; treatment effect estimation).
  * Missing day: December 31, 2024, is absent from raw data; dates span 365 days.
* **Target Outcome Hierarchy:**
  1. **Primary Metric:** `gross_profit` ($\text{revenue} - \text{cogs}$). Tests whether higher margins exceed volume losses.
  2. **Secondary Demand Metric:** `units_sold`. Measures consumer price elasticity.
  3. **Secondary Commercial Metric:** `revenue`. Measures top-line performance.

---

## 3. Summary of Donor Selection & Estimated Weights

* **Primary Screened Donors:** Markets **M008–M020** form the cleanest control pool.
  * Direct geographic neighbors **M005, M006, and M007** were isolated from the core baseline to protect against SUTVA spillover contamination (retained for sensitivity checks).
  * **Region 5 (M017–M020)** provides a zero-treatment regional anchor.
* **Optimal Weights ($\sum w_j = 1, w_j \ge 0$):**
  * **M001 (Large Market):** Synthesized primarily by **M013** ($w \approx 0.54$) and **M018** ($w \approx 0.34$).
  * **M003 (Small Market):** Synthesized primarily by **M015** ($w \approx 0.49$) and **M019** ($w \approx 0.51$).
  * **M002 & M004 (Mid-Scale):** Synthesized across balanced mid-tier donors (**M008, M009, M010, M011, M017**).

---

## 4. Key Diagnostic Insights & Known Data Issues

1. **Pre-Treatment Baseline Fit (MSPE):**
   * Average pre-treatment MAPE across the treated cohort was **2.08%**, confirming close tracking during the baseline period.
   * **Boundary Warning for M003 & M001:** As the smallest and largest markets in the sample, individual unit-level synthetic fits experience boundary tension. Evaluating the aggregated cohort ($M001–M004$ average) provides the most stable, reliable counterfactual.
2. **Missing Confounder Records:**
   * Raw data contains 30 missing `promotion` flags and 60 missing `competitor_price` values. In our modeling, missing promotion values were treated as unobserved rather than defaulted to zero.
3. **Simultaneous Single Rollout:**
   * All treated markets shifted on July 1; no staggered rollout was available to exploit.

---

## 5. Guidance on Business Interpretation: Avoiding Causal Overstatement

When reporting findings to stakeholders or leadership, adhere to these communication guidelines:

> ### ⚠️ Critical Reporting Principles:
> 1. **Do NOT Treat the Synthetic Gap as Infallible Proof:**  
>    A positive post-July gross profit divergence indicates that treated markets outperformed their synthetic counterfactual. However, SCM establishes an observational counterfactual based on pre-trend matching; it does not eliminate the possibility of unobserved simultaneous local factors.
> 2. **Explicitly Label as Simulated / Demo Findings:**  
>    As mandated by project specifications, this dataset is simulated. Findings demonstrate causal inference architecture and must never be cited as real-world market intelligence.
> 3. **Demand vs. Margin Separation:**  
>    Always present `gross_profit` side-by-side with `units_sold`. If gross profit rose by $+5\%$ while sales volume fell by $-4\%$, communicate clearly that the pricing policy increased profit at the expense of customer transaction volume.
> 4. **Acknowledge Placebo Uncertainty:**  
>    Reference the in-space placebo permutation test ($p \approx 0.059$). Emphasize that while the effect is distinct compared to the vast majority of donor markets, it is evaluated across a small sample of 4 treated units.
