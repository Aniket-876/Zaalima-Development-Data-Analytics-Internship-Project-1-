"""Data loading and validation helpers for the causal pricing dashboard.

The current project dataset is simulated. Dashboard outputs must remain labelled as
simulation/demo outputs until the mentor approves the final data source.
"""
from pathlib import Path
from typing import Iterable
import pandas as pd

REQUIRED_COLUMNS = {
    "date", "market_id", "product_id", "treated_market", "treatment",
    "price", "units_sold", "revenue", "gross_profit"
}
NUMERIC_COLUMNS = ["price", "units_sold", "revenue", "gross_profit"]


def load_transactions(path: str | Path) -> pd.DataFrame:
    """Load a transaction CSV, parse dates, and validate required schema."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Transaction dataset not found: {path}")
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Dataset contains invalid or missing dates in 'date'.")
    for col in NUMERIC_COLUMNS + ["treated_market", "treatment"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def validate_transactions(df: pd.DataFrame) -> list[dict[str, object]]:
    """Return a small, inspectable validation report; does not mutate input."""
    checks: list[dict[str, object]] = []
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    checks.append({"check": "required_columns_present", "status": "PASS" if not missing_cols else "FAIL", "detail": "All required columns present" if not missing_cols else f"Missing: {sorted(missing_cols)}"})
    if "date" in df:
        invalid_dates = int(pd.to_datetime(df["date"], errors="coerce").isna().sum())
        checks.append({"check": "valid_dates", "status": "PASS" if invalid_dates == 0 else "FAIL", "detail": f"Invalid dates: {invalid_dates}"})
    key_cols = [c for c in ["market_id", "product_id", "date"] if c in df]
    if len(key_cols) == 3:
        duplicates = int(df.duplicated(key_cols).sum())
        checks.append({"check": "market_product_date_unique", "status": "PASS" if duplicates == 0 else "FAIL", "detail": f"Duplicate keys: {duplicates}"})
    for col in ["price", "units_sold", "revenue", "gross_profit"]:
        if col in df:
            bad = int((pd.to_numeric(df[col], errors="coerce") < 0).sum())
            checks.append({"check": f"nonnegative_{col}", "status": "PASS" if bad == 0 else "FAIL", "detail": f"Negative values: {bad}"})
    for col in ["treated_market", "treatment"]:
        if col in df:
            vals = set(pd.to_numeric(df[col], errors="coerce").dropna().unique())
            bad = vals - {0, 1}
            checks.append({"check": f"binary_{col}", "status": "PASS" if not bad else "FAIL", "detail": f"Unexpected values: {sorted(bad)}"})
    return checks




def filter_transactions(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    markets: Iterable[str] | None = None,
    products: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Filter without mutating the source dataframe."""
    out = df.copy()
    if start_date is not None:
        out = out[out["date"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        out = out[out["date"] <= pd.Timestamp(end_date)]
    if markets:
        out = out[out["market_id"].isin(list(markets))]
    if products and "product_id" in out:
        out = out[out["product_id"].isin(list(products))]
    return out
