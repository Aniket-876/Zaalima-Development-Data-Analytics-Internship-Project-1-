"""Exploratory cross-fitted partialling-out DML for the simulated pricing panel.

This is a reproducible development implementation, not proof of causal identification.
The input is a market x product x date panel with treatment assigned to M001-M004
from 2024-07-01. Standard row-level uncertainty is not panel-cluster robust; all
estimates must be labelled exploratory until the causal design is reviewed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline  

from sklearn.preprocessing import OrdinalEncoder, StandardScaler

REQUIRED_COLUMNS = {
    "market_id", "product_id", "date", "treatment", "treated_market",
    "promotion", "competitor_price", "seasonal_index", "day_of_week",
    "category", "region", "gross_profit", "revenue", "units_sold",
}
OUTCOMES = ("gross_profit", "revenue", "units_sold")
NUMERIC_FEATURES = ["competitor_price", "promotion", "seasonal_index", "day_of_week"]
CATEGORICAL_FEATURES = ["category", "region", "product_id"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_panel(path: str | Path) -> pd.DataFrame:
    """Load and validate the processed panel without modifying the source file."""
    df = pd.read_csv(path, parse_dates=["date"], low_memory=False)
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Required columns missing from input: {missing}")
    if df["date"].isna().any():
        raise ValueError("date contains missing/unparseable values")
    if not set(df["treatment"].dropna().unique()).issubset({0, 1}):
        raise ValueError("treatment must be binary 0/1")
    if df["treatment"].isna().any():
        raise ValueError("treatment contains missing values")
    if df.duplicated(["market_id", "product_id", "date"]).any():
        raise ValueError("Duplicate market_id x product_id x date rows found")
    return df.sort_values(["date", "market_id", "product_id"]).reset_index(drop=True)


def _preprocessor() -> ColumnTransformer:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_FEATURES),
        ("categorical", categorical, CATEGORICAL_FEATURES),
    ])


def _make_outcome_model() -> Pipeline:
    # Random forest is used as a flexible nuisance model; tune only after a baseline run.
    return Pipeline([
        ("prep", _preprocessor()),
        ("model", Ridge(alpha=1.0)),
    ])


def _make_treatment_model() -> Pipeline:
    return Pipeline([
        ("prep", _preprocessor()),
        ("model", LogisticRegression(
            max_iter=300, class_weight="balanced", solver="lbfgs",
            random_state=42,
        )),
    ])


def date_block_folds(dates: pd.Series, n_splits: int = 5) -> np.ndarray:
    """Assign every row on the same date to the same held-out fold."""
    unique_dates = np.array(sorted(pd.to_datetime(dates).unique()))
    if len(unique_dates) < n_splits:
        raise ValueError(f"Need at least {n_splits} unique dates; found {len(unique_dates)}")
    splitter = GroupKFold(n_splits=n_splits)
    dummy = np.zeros((len(unique_dates), 1))
    date_fold = np.full(len(unique_dates), -1, dtype=int)
    for fold, (_, test_idx) in enumerate(splitter.split(dummy, groups=unique_dates)):
        date_fold[test_idx] = fold
    mapping = {date: int(fold) for date, fold in zip(unique_dates, date_fold)}
    return pd.to_datetime(dates).map(mapping).to_numpy(dtype=int)


def overlap_diagnostics(d: np.ndarray, propensity: np.ndarray) -> dict:
    propensity = np.clip(np.asarray(propensity, dtype=float), 0.0, 1.0)
    d = np.asarray(d, dtype=int)
    treated = propensity[d == 1]
    control = propensity[d == 0]
    if len(treated) == 0 or len(control) == 0:
        return {"overlap_flag": "FAIL", "treated_propensity_min": None,
                "treated_propensity_max": None, "control_propensity_min": None,
                "control_propensity_max": None, "fraction_outside_0.05_0.95": 1.0}
    outside = np.mean((propensity < 0.05) | (propensity > 0.95))
    # This is a screening heuristic, not a formal proof of positivity.
    common_low = max(float(treated.min()), float(control.min()))
    common_high = min(float(treated.max()), float(control.max()))
    overlap = common_low < common_high and outside < 0.5
    return {
        "overlap_flag": "PASS_SCREEN_ONLY" if overlap else "REVIEW_REQUIRED",
        "treated_propensity_min": float(treated.min()),
        "treated_propensity_max": float(treated.max()),
        "control_propensity_min": float(control.min()),
        "control_propensity_max": float(control.max()),
        "fraction_outside_0.05_0.95": float(outside),
        "common_support_low": common_low,
        "common_support_high": common_high,
    }


def estimate_dml(df: pd.DataFrame, outcome: str, n_splits: int = 5) -> tuple[dict, pd.DataFrame]:
    """Cross-fitted partially linear DML point estimate with explicit caveats.

    Treatment is the supplied post-intervention indicator. Nuisance predictions are
    cross-fitted by date blocks. The reported plug-in SE is IID-only and must not be
    interpreted as valid panel inference; market-cluster-aware inference is still needed.
    """
    if outcome not in OUTCOMES:
        raise ValueError(f"Outcome must be one of {OUTCOMES}")
    work = df.dropna(subset=[outcome, "treatment"]).copy()
    if work["treatment"].nunique() != 2:
        raise ValueError("Both treated and untreated rows are required")
    if work[FEATURES].isna().all(axis=1).any():
        raise ValueError("Rows with every selected feature missing require review")

    y = work[outcome].astype(float).to_numpy()
    d = work["treatment"].astype(int).to_numpy()
    X = work[FEATURES].copy()
    folds = date_block_folds(work["date"], n_splits=n_splits)
    m_hat = np.full(len(work), np.nan, dtype=float)
    e_hat = np.full(len(work), np.nan, dtype=float)

    for fold in range(n_splits):
        train = folds != fold
        test = folds == fold
        if len(np.unique(d[train])) < 2:
            raise ValueError(f"Fold {fold} training data has only one treatment class")
        y_model = _make_outcome_model()
        d_model = _make_treatment_model()
        y_model.fit(X.loc[train], y[train])
        # Balance treatment classes in nuisance training to stabilize propensity fit.
        d_model.fit(X.loc[train], d[train])
        m_hat[test] = y_model.predict(X.loc[test])
        classes = list(d_model.named_steps["model"].classes_)
        pos_idx = classes.index(1)
        e_hat[test] = d_model.predict_proba(X.loc[test])[:, pos_idx]

    y_resid = y - m_hat
    d_resid = d - e_hat
    denom = float(np.mean(d_resid ** 2))
    if denom < 1e-8:
        raise ValueError("Residualized treatment variance is near zero; DML estimate is unidentified")
    theta = float(np.mean(d_resid * y_resid) / denom)
    psi = d_resid * (y_resid - theta * d_resid)
    # Deliberately labelled IID-only. Panel rows are dependent; do not report as final CI.
    iid_se = float(np.sqrt(np.mean(psi ** 2) / len(work)) / denom)
    overlap = overlap_diagnostics(d, e_hat)
    result = {
        "outcome": outcome,
        "n_rows_used": int(len(work)),
        "n_markets": int(work["market_id"].nunique()),
        "n_treated_rows": int((d == 1).sum()),
        "n_control_rows": int((d == 0).sum()),
        "n_date_folds": int(n_splits),
        "dml_point_estimate_exploratory": theta,
        "iid_only_standard_error_not_for_final_inference": iid_se,
        "propensity_min": float(np.min(e_hat)),
        "propensity_max": float(np.max(e_hat)),
        **overlap,
        "data_status": "SIMULATED_DEVELOPMENT_DATA",
        "causal_status": "EXPLORATORY_NOT_VALIDATED",
        "inference_warning": "IID-only SE ignores market/product/time dependence; use an approved panel-aware inference strategy before reporting confidence intervals.",
        "identification_warning": "Treatment is assigned by treated market and post-July date. Check overlap, market/time shocks, and design assumptions; predictive fit alone does not establish causality.",
    }
    predictions = work[["market_id", "product_id", "date", "treatment", outcome]].copy()
    predictions["fold"] = folds
    predictions["outcome_prediction_oof"] = m_hat
    predictions["treatment_propensity_oof"] = e_hat
    predictions["outcome_residual"] = y_resid
    predictions["treatment_residual"] = d_resid
    return result, predictions


def write_report(results: list[dict], out_dir: Path) -> None:
    lines = [
        "# DML exploratory run report", "",
        "> **Simulated development data only. Not real commercial evidence.**",
        "> Estimates are exploratory. IID-only standard errors are not valid final inference for this panel.", "",
        "## Results", "",
        "| Outcome | Rows | Exploratory estimate | Overlap screen | Status |",
        "|---|---:|---:|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['outcome']} | {r['n_rows_used']} | {r['dml_point_estimate_exploratory']:.6g} | "
            f"{r['overlap_flag']} | {r['causal_status']} |"
        )
    lines += ["", "## Interpretation and required checks", "",
        "- Do not call these estimates validated causal effects.",
        "- Review propensity overlap and the deterministic market-by-post treatment assignment.",
        "- Review missingness, pre-treatment covariates, market/time shocks, and possible spillovers.",
        "- Do not report the IID-only standard error as a final confidence interval.",
        "- Confirm the dataset is approved for the final project; current files describe it as simulated.",
        "- Keep DML and Synthetic Control estimates distinct unless estimands and assumptions are demonstrably compatible.", ""]
    (out_dir / "dml_validation_report.md").write_text("\n".join(lines), encoding="utf-8")





def run(input_path: Path, output_dir: Path, n_splits: int = 5) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = load_panel(input_path)
    results = []
    all_predictions = []
    for outcome in OUTCOMES:
        result, predictions = estimate_dml(df, outcome, n_splits=n_splits)
        results.append(result)
        all_predictions.append(predictions)
    pd.DataFrame(results).to_csv(output_dir / "dml_estimates_exploratory.csv", index=False)
    pd.concat(all_predictions, ignore_index=True).to_csv(output_dir / "dml_oof_predictions.csv", index=False)
    (output_dir / "dml_diagnostics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_report(results, output_dir)
    return results








def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to processed transaction CSV")
    parser.add_argument("--output-dir", default="reports/dml_run")
    parser.add_argument("--folds", type=int, default=5)
    args = parser.parse_args()
    results = run(Path(args.input), Path(args.output_dir), n_splits=args.folds)
    print(pd.DataFrame(results)[[
        "outcome", "n_rows_used", "dml_point_estimate_exploratory", "overlap_flag", "causal_status"
    ]].to_string(index=False))
    print(f"\nOutputs saved to: {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
