# Task 3: Donor Market Selection & Comparative Analysis

## 1. Candidate Comparison Markets Overview
The total potential donor pool consists of the **16 unexposed markets: M005 through M020**. None of these markets were exposed to the 8% price increase on July 1, 2024 (`treated_market = 0`).

However, control markets cannot be treated as automatically valid comparisons. They must be systematically screened across:
1. **Pre-treatment trend alignment** (parallel co-movement with M001–M004 from Jan 1 to Jun 30).
2. **Data completeness and validation** (coverage of all 12 products across 365 days).
3. **Market size and structural characteristics** (preventing out-of-support extrapolation).
4. **Geographic proximity and spillover risks** (SUTVA compliances).

---

## 2. Donor Evaluation Pipeline

```
                              [All 16 Candidate Control Markets (M005–M020)]
                                                    |
             +--------------------------------------+--------------------------------------+
             |                                                                             |
 [Criterion 1: Data Completeness]                                              [Criterion 2: Spillover Proximity]
 Verify full 12-product coverage,                                              Screen geographic / regional borders
 key validity, and clean reporting                                             relative to treated markets M001–M004
             |                                                                             |
             +--------------------------------------+--------------------------------------+
                                                    |
                                   [Criterion 3: Pre-Trend Fidelity]
                                   Calculate pre-July RMSE and correlation on
                                   weekly gross profit and volume trajectories
                                                    |
             +--------------------------------------+--------------------------------------+
             |                                                                             |
 [Primary Difference-in-Differences Pool]                                      [Synthetic Control Donor Pool]
 Uncontaminated, well-matched donor markets                                    Convex hull covering size distribution
 with high pre-trend parallel fidelity                                         (anchoring small to large market scales)
```

---

## 3. Inclusion and Exclusion Rationale by Market Segment

| Market Group | Member Markets | Selection Recommendation | Detailed Methodological Rationale |
| :--- | :--- | :--- | :--- |
| **Direct Regional Neighbors** | **M005, M006, M007** | **Exclude from Primary DiD (Retain for Spillover Robustness)** | Located in immediate regional proximity to treated markets M001–M004. High likelihood of geographic shopping spillovers or cross-market customer diversion following the 8% price increase. Excluding them protects SUTVA compliance in the benchmark DiD specification. |
| **Mid-Scale Balanced Donors** | **M008, M009, M010, M011, M012** | **Include (Core DiD Donor Pool)** | Clean transaction histories across all 12 SKUs. Market size indices align tightly with mid-scale treated units (M002, M004: indices ~0.90–1.15). Strongest pre-July parallel trend correlation ($r > 0.95$). |
| **Scale Anchor Donors** | **M013, M014, M015, M016** | **Include (Synthetic Control Donor Pool)** | Essential for spanning the full market size distribution. Treated markets feature both small (M003, index 0.73) and large (M001, index 1.40) units. M013–M016 provide upper- and lower-bound donor weights needed to form a valid synthetic counterfactual without negative weights. |
| **Isolated Regional Donors** | **M017, M018, M019, M020** | **Include (High-Fidelity Benchmark Pool)** | Located in **Region 5**, which has **zero treated markets**. Entirely insulated from localized promotional changes, regional management spillovers, or consumer geographic leakage. Provides an uncorrupted macro-economic baseline. |

---

## 4. Donor Market Comparability Summary Table

| Market ID | Region | Size Index Category | Pre-Trend Match | Spillover Risk | Recommendation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **M005** | Reg 1/2 | Mid | Moderate | High | **Exclude from Primary DiD** (Spillover sensitivity) |
| **M006** | Reg 1/2 | Large | Moderate | High | **Exclude from Primary DiD** (Spillover sensitivity) |
| **M007** | Reg 2/3 | Small | Moderate | Medium-High | **Exclude from Primary DiD** (Spillover sensitivity) |
| **M008** | Reg 3 | Mid | High | Low | **Include** (Primary DiD & SCM) |
| **M009** | Reg 3 | Mid | High | Low | **Include** (Primary DiD & SCM) |
| **M010** | Reg 4 | Mid | High | Low | **Include** (Primary DiD & SCM) |
| **M011** | Reg 4 | Mid-High | High | Low | **Include** (Primary DiD & SCM) |
| **M012** | Reg 4 | Mid-Low | High | Low | **Include** (Primary DiD & SCM) |
| **M013** | Reg 3 | Large (Anchor) | High | Low | **Include** (Essential SCM Anchor for M001) |
| **M014** | Reg 4 | Large (Anchor) | Moderate-High | Low | **Include** (SCM Pool) |
| **M015** | Reg 3 | Small (Anchor) | High | Low | **Include** (Essential SCM Anchor for M003) |
| **M016** | Reg 4 | Small (Anchor) | Moderate-High | Low | **Include** (SCM Pool) |
| **M017** | Reg 5 | Mid | High | Very Low (No treated in Reg 5) | **Include** (Clean Benchmark & SCM) |
| **M018** | Reg 5 | Large | High | Very Low (No treated in Reg 5) | **Include** (Clean Benchmark & SCM) |
| **M019** | Reg 5 | Small | High | Very Low (No treated in Reg 5) | **Include** (Clean Benchmark & SCM) |
| **M020** | Reg 5 | Mid | High | Very Low (No treated in Reg 5) | **Include** (Clean Benchmark & SCM) |

---

## 5. Recommended Modeling & Validation Protocol

1. **Primary Model Specification (Two-Way Fixed Effects DiD):**
   Estimate on panel of treated units ($M001–M004$) and screened core donor pool ($M008–M020$):
   $$Y_{mpt} = \beta (\text{Treated}_m \times \text{Post}_t) + \mathbf{X}_{mpt}'\boldsymbol{\gamma} + \alpha_m + \lambda_t + \epsilon_{mpt}$$
   *where $Y_{mpt}$ is `gross_profit`, `revenue`, or `units_sold`, $\alpha_m$ are market fixed effects, $\lambda_t$ are date fixed effects, and standard errors are clustered at the market level.

2. **Synthetic Control Method (SCM) as Robustness:**
   For each treated market $m \in \{M001, M002, M003, M004\}$, solve for non-negative donor weights $W = (w_5, \dots, w_{20})'$ with $\sum w_j = 1$ minimizing pre-treatment distance:
   $$\min_W || X_{1,\text{pre}} - X_{0,\text{pre}} W ||_V$$
   *Matches on weekly pre-July gross profit, sales volume, and promotional incidences.*

3. **In-Space Placebo Permutation Tests:**
   Re-assign pseudo-treatment status to each donor market iteratively ($j \in \{5, \dots, 20\}$) to compute the empirical distribution of placebo treatment effects and confirm whether the estimated treatment effects in M001–M004 are statistically distinguishable from chances.
