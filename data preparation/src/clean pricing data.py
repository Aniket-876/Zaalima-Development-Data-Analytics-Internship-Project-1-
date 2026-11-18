#!/usr/bin/env python3
"""
clean_pricing_data.py
=====================
Reusable data-profiling, cleaning and validation script for the
"Causal Inference & Synthetic Control for Algorithmic Pricing" project.

NOTE: the starter dataset is SIMULATED (see README_DATASET.md). Results built on
it must be labelled simulation/demo results until the mentor confirms whether
simulated data is acceptable for the final project.

Input files (in --input-dir):
    regional_market_transactions.csv   (main dataset, one row per market x product x day)
    market_metadata.csv
    product_metadata.csv

Output files:
  in --output-dir (processed data):
    cleaned_regional_market_transactions.csv
    cleaned_market_metadata.csv
    cleaned_product_metadata.csv
  in --report-dir (evidence):
    dq_issue_log.csv          every check run, rows affected, and the action taken
    validation_results.csv    post-cleaning PASS/FAIL checks

The raw input folder is only ever read, never written to.

Design rules (agreed with the team):
  * No row is deleted unless it is an exact duplicate of another row.
  * Missing values are never filled with a guess. The only fill is `region`,
    which is a deterministic lookup from market_metadata (market -> region is 1:1).
  * Treatment-related columns (treated_market, treatment_date, treatment) are
    never modified; they are only checked against each other and the metadata.
  * Anything suspicious but plausible (e.g. statistical outliers) is reported, not changed.

Usage:
    python src/clean_pricing_data.py --input-dir data/raw --output-dir data/processed --report-dir reports
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

TXN_FILE = "regional_market_transactions.csv"
MKT_FILE = "market_metadata.csv"
PRD_FILE = "product_metadata.csv"

# Rounding tolerance: price and revenue are both rounded to 2 dp, so
# |price * units - revenue| can legitimately reach 0.005 * units.
REVENUE_ABS_TOL = 0.011
PRICE_ROUNDING = 0.005


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
class Log:
    """Collects one row per check: what was tested, how many rows, what we did."""

    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, file: str, check: str, n: int, action: str, detail: str = "") -> None:
        self.rows.append(
            {"file": file, "check": check, "rows_affected": int(n), "action": action, "detail": detail}
        )

    def frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)


def clean_id(s: pd.Series) -> pd.Series:
    """Strip whitespace and upper-case an ID column (keeps missing as missing)."""
    return s.astype("string").str.strip().str.upper()


def clean_text(s: pd.Series) -> pd.Series:
    out = s.astype("string").str.strip()
    return out.replace("", pd.NA)


# --------------------------------------------------------------------------- #
# market_metadata.csv
# --------------------------------------------------------------------------- #
def clean_market_metadata(raw: pd.DataFrame, log: Log) -> pd.DataFrame:
    f = MKT_FILE
    df = raw.copy()
    df["market_id"] = clean_id(df["market_id"])
    df["region"] = clean_text(df["region"])
    df["market_size_index"] = pd.to_numeric(df["market_size_index"], errors="coerce")
    df["treated_market"] = pd.to_numeric(df["treated_market"], errors="coerce").astype("Int8")
    df["treatment_date"] = pd.to_datetime(df["treatment_date"], errors="coerce")

    log.add(f, "missing market_id", df["market_id"].isna().sum(), "report only")
    log.add(f, "duplicate market_id", df["market_id"].duplicated(keep=False).sum(), "report only (none to drop)")
    log.add(f, "missing region", df["region"].isna().sum(), "report only")
    log.add(f, "missing / non-positive market_size_index", (~(df["market_size_index"] > 0)).sum(), "report only")
    log.add(f, "treated_market not in {0,1}", (~df["treated_market"].isin([0, 1])).sum(), "report only")
    treated_no_date = ((df["treated_market"] == 1) & df["treatment_date"].isna()).sum()
    control_with_date = ((df["treated_market"] == 0) & df["treatment_date"].notna()).sum()
    log.add(f, "treated market without treatment_date", treated_no_date, "report only")
    log.add(f, "control market with a treatment_date", control_with_date, "report only")
    log.add(
        f,
        "blank treatment_date for control markets",
        ((df["treated_market"] == 0) & df["treatment_date"].isna()).sum(),
        "kept blank (structural: controls are never treated)",
    )
    return df


# --------------------------------------------------------------------------- #
# product_metadata.csv
# --------------------------------------------------------------------------- #
def clean_product_metadata(raw: pd.DataFrame, log: Log) -> pd.DataFrame:
    f = PRD_FILE
    df = raw.copy()
    df["product_id"] = clean_id(df["product_id"])
    df["category"] = clean_text(df["category"])
    df["base_price"] = pd.to_numeric(df["base_price"], errors="coerce")
    df["base_demand"] = pd.to_numeric(df["base_demand"], errors="coerce")

    log.add(f, "missing product_id", df["product_id"].isna().sum(), "report only")
    log.add(f, "duplicate product_id", df["product_id"].duplicated(keep=False).sum(), "report only (none to drop)")
    log.add(f, "missing category", df["category"].isna().sum(), "report only")
    log.add(f, "missing / non-positive base_price", (~(df["base_price"] > 0)).sum(), "report only")
    log.add(f, "missing / non-positive base_demand", (~(df["base_demand"] > 0)).sum(), "report only")
    return df


# --------------------------------------------------------------------------- #
# regional_market_transactions.csv
# --------------------------------------------------------------------------- #
def clean_transactions(raw: pd.DataFrame, mkt: pd.DataFrame, prd: pd.DataFrame, log: Log) -> pd.DataFrame:
    f = TXN_FILE
    df = raw.copy()

    # --- 1. standardise text / ids / types -------------------------------- #
    for c in ("market_id", "product_id"):
        df[c] = clean_id(df[c])
    for c in ("region", "category"):
        df[c] = clean_text(df[c])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["treatment_date"] = pd.to_datetime(df["treatment_date"], errors="coerce")
    for c in ("treated_market", "treatment", "day_of_week"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int8")
    df["promotion"] = pd.to_numeric(df["promotion"], errors="coerce").astype("Int8")  # 0/1 flag, was float
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce").astype("Int64")
    for c in ("price", "competitor_price", "seasonal_index", "revenue", "unit_cost", "gross_profit"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Keep an untouched copy of the treatment columns to prove we never alter them.
    treat_cols = ["treated_market", "treatment_date", "treatment"]
    treat_before = df[treat_cols].copy()

    log.add(f, "unparseable date", df["date"].isna().sum(), "report only")
    log.add(f, "date range", 0, "info", f"{df['date'].min().date()} to {df['date'].max().date()}")

    # --- 2. duplicates ------------------------------------------------------ #
    exact_dups = df.duplicated(keep="first").sum()
    log.add(f, "exact duplicate rows", exact_dups, "dropped (keep first)" if exact_dups else "none found")
    df = df.drop_duplicates(keep="first")
    log.add(
        f, "duplicate market_id+product_id+date (after exact-dup removal)",
        df.duplicated(["market_id", "product_id", "date"], keep=False).sum(),
        "report only - conflicting duplicates need a human decision",
    )

    # --- 3. referential integrity vs metadata -------------------------------- #
    bad_m = ~df["market_id"].isin(mkt["market_id"])
    bad_p = ~df["product_id"].isin(prd["product_id"])
    log.add(f, "market_id not in market_metadata", bad_m.sum(), "report only")
    log.add(f, "product_id not in product_metadata", bad_p.sum(), "report only")
    log.add(f, "market_metadata ids absent from transactions",
            (~mkt["market_id"].isin(df["market_id"])).sum(), "report only")
    log.add(f, "product_metadata ids absent from transactions",
            (~prd["product_id"].isin(df["product_id"])).sum(), "report only")

    # --- 4. missing values --------------------------------------------------- #
    for c in df.columns:
        n = df[c].isna().sum()
        if n and c != "treatment_date":
            log.add(f, f"missing {c}", n, "see handling below")
    n_td = df["treatment_date"].isna().sum()
    only_controls = bool((df.loc[df["treatment_date"].isna(), "treated_market"] == 0).all())
    log.add(f, "blank treatment_date", n_td,
            "kept blank (structural: only treated markets have a date)",
            f"all blanks belong to control markets: {only_controls}")

    # region: deterministic lookup from market metadata (1 market -> 1 region)
    mkt_region = mkt.set_index("market_id")["region"]
    conflicts = (
        df["region"].notna() & df["market_id"].map(mkt_region).notna()
        & (df["region"] != df["market_id"].map(mkt_region))
    ).sum()
    log.add(f, "region disagrees with market_metadata", conflicts, "report only")
    miss_region = df["region"].isna()
    df["region_filled_from_metadata"] = (miss_region & df["market_id"].map(mkt_region).notna()).astype("Int8")
    df.loc[miss_region, "region"] = df.loc[miss_region, "market_id"].map(mkt_region)
    log.add(f, "region filled via market_metadata lookup", df["region_filled_from_metadata"].sum(),
            "filled (lookup, not a guess); flag column added")

    # category: same logic, only a consistency check
    prd_cat = prd.set_index("product_id")["category"]
    cat_conf = (df["category"].notna() & (df["category"] != df["product_id"].map(prd_cat))).sum()
    log.add(f, "category disagrees with product_metadata", cat_conf, "report only")

    # competitor_price & promotion: NOT imputed; flag only
    df["competitor_price_missing"] = df["competitor_price"].isna().astype("Int8")
    df["promotion_missing"] = df["promotion"].isna().astype("Int8")
    log.add(f, "competitor_price missing", df["competitor_price_missing"].sum(),
            "left missing + flag column (not imputed)")
    log.add(f, "promotion missing", df["promotion_missing"].sum(),
            "left missing + flag column (not imputed)")
    multi = (df[["region_filled_from_metadata", "competitor_price_missing", "promotion_missing"]]
             .fillna(0).sum(axis=1) > 1).sum()
    log.add(f, "rows with more than one missing/filled field", multi, "info")

    # --- 5. domain / range checks ------------------------------------------- #
    log.add(f, "price <= 0 or missing", (~(df["price"] > 0)).sum(), "report only")
    log.add(f, "competitor_price <= 0 (non-missing)", (df["competitor_price"] <= 0).sum(), "report only")
    log.add(f, "units_sold < 0 or missing", (~(df["units_sold"] >= 0)).sum(), "report only")
    log.add(f, "units_sold == 0", (df["units_sold"] == 0).sum(), "info (valid zero-sales days)")
    log.add(f, "revenue < 0 or missing", (~(df["revenue"] >= 0)).sum(), "report only")
    log.add(f, "unit_cost <= 0 or missing", (~(df["unit_cost"] > 0)).sum(), "report only")
    log.add(f, "unit_cost >= price (negative unit margin)", (df["unit_cost"] >= df["price"]).sum(), "report only")
    log.add(f, "gross_profit < 0", (df["gross_profit"] < 0).sum(), "report only")
    log.add(f, "promotion not in {0,1}", (~df["promotion"].dropna().isin([0, 1])).sum(), "report only")
    log.add(f, "treated_market/treatment not in {0,1}",
            (~df["treated_market"].isin([0, 1])).sum() + (~df["treatment"].isin([0, 1])).sum(), "report only")
    log.add(f, "day_of_week disagrees with date (0=Mon)",
            (df["date"].dt.dayofweek != df["day_of_week"]).sum(), "report only")
    log.add(f, "seasonal_index <= 0", (~(df["seasonal_index"] > 0)).sum(), "report only")

    # arithmetic consistency
    rev_diff = (df["price"] * df["units_sold"] - df["revenue"]).abs()
    tol = PRICE_ROUNDING * df["units_sold"].astype(float) + REVENUE_ABS_TOL
    log.add(f, "revenue != price*units beyond 2-dp rounding tolerance", (rev_diff > tol).sum(), "report only")
    log.add(f, "revenue != price*units exactly (rounding artefact)", (rev_diff > REVENUE_ABS_TOL).sum(),
            "kept as is", "price and revenue are each rounded to 2 dp, so exact equality is not expected")
    gp_diff = (df["revenue"] - df["unit_cost"] * df["units_sold"] - df["gross_profit"]).abs()
    log.add(f, "gross_profit != revenue - unit_cost*units", (gp_diff > REVENUE_ABS_TOL).sum(), "report only")

    # panel completeness
    full = pd.date_range(df["date"].min().normalize().replace(month=1, day=1),
                         df["date"].min().normalize().replace(month=12, day=31))
    missing_days = sorted(set(full) - set(df["date"].dropna().unique()))
    log.add(f, "calendar days missing from the year", len(missing_days), "report only",
            ", ".join(d.strftime("%Y-%m-%d") for d in missing_days))
    per_pair = df.groupby(["market_id", "product_id"]).size()
    log.add(f, "market x product pairs with a different number of days than the maximum",
            (per_pair != per_pair.max()).sum(), "report only (panel is balanced if 0)")

    # --- 6. treatment checks (NO modification) ------------------------------- #
    mk = mkt.set_index("market_id")
    log.add(f, "treated_market disagrees with market_metadata",
            (df["treated_market"] != df["market_id"].map(mk["treated_market"])).sum(), "report only")
    td_meta = df["market_id"].map(mk["treatment_date"])
    log.add(f, "treatment_date disagrees with market_metadata",
            (~((df["treatment_date"] == td_meta) | (df["treatment_date"].isna() & td_meta.isna()))).sum(),
            "report only")
    log.add(f, "control rows with treatment == 1",
            ((df["treated_market"] == 0) & (df["treatment"] == 1)).sum(), "report only")
    log.add(f, "treated rows with no treatment_date",
            ((df["treated_market"] == 1) & df["treatment_date"].isna()).sum(), "report only")
    treated = df["treated_market"] == 1
    expected = (df["date"] >= df["treatment_date"]).astype("Int8")
    log.add(f, "treatment != (date >= treatment_date) for treated markets",
            (treated & (expected != df["treatment"])).sum(), "report only")

    # --- 7. plausibility (report only) --------------------------------------- #
    for c in ("price", "competitor_price", "units_sold", "unit_cost", "revenue"):
        g = df.groupby("product_id")[c]
        z = (df[c].astype(float) - g.transform("mean")) / g.transform("std")
        log.add(f, f"{c}: |z|>4 within product (outlier candidates)", (z.abs() > 4).sum(),
                "kept, report only", "statistically unusual but plausible under promotions / treatment / noise")
    ratio = df["competitor_price"] / df["price"]
    log.add(f, "competitor_price/price outside [0.5, 2]", ((ratio < 0.5) | (ratio > 2)).sum(), "report only")

    # --- 8. proof that treatment columns were untouched ---------------------- #
    same = treat_before.reindex(df.index).equals(df[treat_cols])
    log.add(f, "treatment columns unchanged by cleaning", 0 if same else 1, "verified" if same else "FAILED")

    # tidy column order & sort
    cols = [c for c in raw.columns] + ["region_filled_from_metadata", "competitor_price_missing", "promotion_missing"]
    df = df[cols].sort_values(["market_id", "product_id", "date"]).reset_index(drop=True)
    return df


# --------------------------------------------------------------------------- #
# Validation of the cleaned output
# --------------------------------------------------------------------------- #
def validate(txn_raw: pd.DataFrame, txn: pd.DataFrame, mkt: pd.DataFrame, prd: pd.DataFrame) -> pd.DataFrame:
    checks: list[tuple[str, bool, str]] = []

    def chk(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    chk("row count preserved", len(txn) == len(txn_raw), f"raw={len(txn_raw):,} clean={len(txn):,}")
    chk("no duplicate market+product+date", not txn.duplicated(["market_id", "product_id", "date"]).any())
    chk("no missing region", txn["region"].notna().all())
    chk("all market_ids in market_metadata", txn["market_id"].isin(mkt["market_id"]).all())
    chk("all product_ids in product_metadata", txn["product_id"].isin(prd["product_id"]).all())
    chk("market_id unique in market_metadata", mkt["market_id"].is_unique)
    chk("product_id unique in product_metadata", prd["product_id"].is_unique)
    chk("date is datetime, no NaT", pd.api.types.is_datetime64_any_dtype(txn["date"]) and txn["date"].notna().all())
    chk("price > 0", (txn["price"] > 0).all())
    chk("units_sold >= 0", (txn["units_sold"] >= 0).all())
    chk("gross_profit = revenue - unit_cost*units",
        ((txn["revenue"] - txn["unit_cost"] * txn["units_sold"] - txn["gross_profit"]).abs() <= REVENUE_ABS_TOL).all())
    # compare treatment columns on the merge key against the raw file
    key = ["market_id", "product_id", "date"]
    r = txn_raw.copy()
    r["market_id"] = r["market_id"].astype(str).str.strip().str.upper()
    r["product_id"] = r["product_id"].astype(str).str.strip().str.upper()
    r["date"] = pd.to_datetime(r["date"])
    j = txn.merge(r[key + ["treated_market", "treatment"]], on=key, suffixes=("", "_raw"))
    chk("treated_market & treatment match raw file on the row key",
        len(j) == len(txn) and (j["treated_market"] == j["treated_market_raw"]).all()
        and (j["treatment"] == j["treatment_raw"]).all())
    chk("flags consistent with missing values",
        (txn["competitor_price_missing"].astype(bool) == txn["competitor_price"].isna()).all()
        and (txn["promotion_missing"].astype(bool) == txn["promotion"].isna()).all())
    chk("every treated market in metadata has a treatment_date",
        mkt.loc[mkt["treated_market"] == 1, "treatment_date"].notna().all())
    return pd.DataFrame(checks, columns=["check", "passed", "detail"]).assign(
        result=lambda d: np.where(d["passed"], "PASS", "FAIL")
    )[["check", "result", "detail"]]


# --------------------------------------------------------------------------- #





# Main




# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input-dir", default="data/raw", type=Path, help="folder with the 3 raw CSVs (read only)")
    ap.add_argument("--output-dir", default="data/processed", type=Path, help="where cleaned CSVs are written")
    ap.add_argument("--report-dir", default="reports", type=Path, help="where the issue log and validation results go")
    args = ap.parse_args(argv)

    if args.output_dir.resolve() == args.input_dir.resolve():
        ap.error("--output-dir must differ from --input-dir so the raw data is never overwritten")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    log = Log()

    txn_raw = pd.read_csv(args.input_dir / TXN_FILE, low_memory=False)
    mkt_raw = pd.read_csv(args.input_dir / MKT_FILE)
    prd_raw = pd.read_csv(args.input_dir / PRD_FILE)
    log.add(TXN_FILE, "rows x columns (raw)", len(txn_raw), "info", f"{txn_raw.shape[1]} columns")
    log.add(MKT_FILE, "rows x columns (raw)", len(mkt_raw), "info", f"{mkt_raw.shape[1]} columns")
    log.add(PRD_FILE, "rows x columns (raw)", len(prd_raw), "info", f"{prd_raw.shape[1]} columns")

    mkt = clean_market_metadata(mkt_raw, log)
    prd = clean_product_metadata(prd_raw, log)
    txn = clean_transactions(txn_raw, mkt, prd, log)

    results = validate(txn_raw, txn, mkt, prd)

    date_fmt = "%Y-%m-%d"
    txn.to_csv(args.output_dir / "cleaned_regional_market_transactions.csv", index=False, date_format=date_fmt)
    mkt.to_csv(args.output_dir / "cleaned_market_metadata.csv", index=False, date_format=date_fmt)
    prd.to_csv(args.output_dir / "cleaned_product_metadata.csv", index=False)
    log.add(TXN_FILE, "row count before -> after cleaning", len(txn_raw), "info",
            f"before={len(txn_raw):,} after={len(txn):,} excluded={len(txn_raw) - len(txn):,}")
    log.add(MKT_FILE, "row count before -> after cleaning", len(mkt_raw), "info",
            f"before={len(mkt_raw):,} after={len(mkt):,} excluded={len(mkt_raw) - len(mkt):,}")
    log.add(PRD_FILE, "row count before -> after cleaning", len(prd_raw), "info",
            f"before={len(prd_raw):,} after={len(prd):,} excluded={len(prd_raw) - len(prd):,}")
    log.frame().to_csv(args.report_dir / "dq_issue_log.csv", index=False)
    results.to_csv(args.report_dir / "validation_results.csv", index=False)

    print(results.to_string(index=False))
    failed = (results["result"] == "FAIL").sum()
    print(f"\n{len(results) - failed}/{len(results)} validation checks passed. Data in: {args.output_dir}, reports in: {args.report_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
