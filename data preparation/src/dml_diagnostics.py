"""Standalone data and treatment-assignment diagnostics for the DML module."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd


def build_diagnostics(path: Path) -> dict:
    df = pd.read_csv(path, parse_dates=["date"])
    required = ["market_id", "product_id", "date", "treatment", "treated_market"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    treatment_by_market = df.groupby("market_id").agg(
        treated_market_values=("treated_market", "nunique"),
        treatment_values=("treatment", "nunique"),
        treated_rows=("treatment", "sum"),
        rows=("treatment", "size"),
    ).reset_index()
    treatment_by_market["treatment_constant_within_market"] = treatment_by_market["treatment_values"].eq(1)
    dates = df.groupby(df["date"].dt.to_period("M"))["treatment"].mean().rename("treated_row_share").reset_index()
    dates["date"] = dates["date"].astype(str)
    result = {
        "rows": int(len(df)),
        "markets": int(df["market_id"].nunique()),
        "products": int(df["product_id"].nunique()),
        "date_min": str(df["date"].min().date()),
        "date_max": str(df["date"].max().date()),
        "missing_by_column": {k: int(v) for k, v in df.isna().sum().items()},
        "duplicate_market_product_date_rows": int(df.duplicated(["market_id", "product_id", "date"]).sum()),
        "treatment_counts": {str(k): int(v) for k, v in df["treatment"].value_counts(dropna=False).items()},
        "treatment_by_market": treatment_by_market.to_dict(orient="records"),
        "monthly_treatment_share": dates.to_dict(orient="records"),
        "warning": "Treatment is defined by treated market and post-intervention date. Evaluate identification and overlap before interpreting DML estimates causally.",
    }
    
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", default="reports/dml_input_diagnostics.json")
    a = p.parse_args()
    result = build_diagnostics(Path(a.input))
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["rows", "markets", "products", "date_min", "date_max", "duplicate_market_product_date_rows", "treatment_counts", "warning"]}, indent=2))
    print(f"Full diagnostics saved to {out}")

if __name__ == "__main__":
    main()
