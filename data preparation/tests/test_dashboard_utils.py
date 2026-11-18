import pandas as pd
import pytest
from src.dashboard_utils import load_transactions, validate_transactions, filter_transactions

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "market_id": ["M001", "M002"], "product_id": ["P001", "P001"],
        "treated_market": [1, 0], "treatment": [0, 0],
        "price": [10.0, 11.0], "units_sold": [5, 6],
        "revenue": [50.0, 66.0], "gross_profit": [20.0, 30.0]
    })

def test_validation_passes_for_valid_sample(sample_df):
    checks = validate_transactions(sample_df)
    assert all(c["status"] == "PASS" for c in checks)

def test_duplicate_market_product_date_fails(sample_df):
    dup = pd.concat([sample_df, sample_df.iloc[[0]]], ignore_index=True)
    checks = {c["check"]: c for c in validate_transactions(dup)}
    assert checks["market_product_date_unique"]["status"] == "FAIL"

def test_negative_price_fails(sample_df):
    bad = sample_df.copy()
    bad.loc[0, "price"] = -1
    checks = {c["check"]: c for c in validate_transactions(bad)}
    assert checks["nonnegative_price"]["status"] == "FAIL"

def test_filter_does_not_mutate_input(sample_df):
    original_len = len(sample_df)
    out = filter_transactions(sample_df, start_date="2024-01-02")
    assert len(out) == 1
    assert len(sample_df) == original_len

def test_load_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_transactions("this_file_does_not_exist.csv")

def test_load_missing_columns_raises(tmp_path):
    p = tmp_path / "bad.csv"
    pd.DataFrame({"date": ["2024-01-01"]}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load_transactions(p)
