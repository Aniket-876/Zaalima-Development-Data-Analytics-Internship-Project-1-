from pathlib import Path
import sys
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dml_pipeline import load_panel, date_block_folds, overlap_diagnostics


def minimal_panel():
    rows = []
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    for market_i in range(4):
        for product_i in range(2):
            for date in dates:
                treated_market = int(market_i < 2)
                treatment = int(treated_market and date >= pd.Timestamp("2024-01-06"))
                rows.append({
                    "market_id": f"M{market_i:03d}", "product_id": f"P{product_i:03d}",
                    "date": date, "treatment": treatment, "treated_market": treated_market,
                    "promotion": 0, "competitor_price": 10.0, "seasonal_index": 1.0,
                    "day_of_week": date.dayofweek, "category": "A", "region": "R1",
                    "gross_profit": 2.0 + treatment, "revenue": 10.0 + treatment,
                    "units_sold": 5.0 - treatment,
                })
    return pd.DataFrame(rows)


def test_load_panel_rejects_missing_required_column(tmp_path):
    df = minimal_panel().drop(columns=["revenue"])
    p = tmp_path / "bad.csv"
    df.to_csv(p, index=False)
    with pytest.raises(ValueError, match="Required columns missing"):
        load_panel(p)


def test_load_panel_rejects_duplicate_panel_key(tmp_path):
    df = minimal_panel()
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    p = tmp_path / "duplicate.csv"
    df.to_csv(p, index=False)
    with pytest.raises(ValueError, match="Duplicate"):
        load_panel(p)


def test_date_block_folds_keep_same_date_together():
    dates = pd.Series(pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03"]))
    folds = date_block_folds(dates, n_splits=3)
    mapping = pd.DataFrame({"date": dates, "fold": folds}).groupby("date")["fold"].nunique()
    assert mapping.max() == 1


def test_overlap_diagnostics_flags_extreme_no_overlap():
    d = [0, 0, 1, 1]
    p = [0.05, 0.1, 0.9, 0.95]
    result = overlap_diagnostics(d, p)
    assert result["overlap_flag"] == "REVIEW_REQUIRED"
