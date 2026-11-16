from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV_PATH = DATA / "cleaned_regional_market_transactions.csv"
INTERVENTION_DATE = pd.Timestamp("2024-07-01")

st.set_page_config(page_title="Causal Pricing | Intelligence Studio", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# ---------- Theme & reusable helpers ----------
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .block-container {padding-top: 1.5rem; padding-bottom: 2.5rem; max-width: 1600px;}
  h1, h2, h3 {font-family: 'Manrope', sans-serif; letter-spacing: -0.03em;}
  .hero {padding: 1.35rem 1.5rem; border-radius: 20px; background: linear-gradient(120deg,#101828 0%,#173b5e 55%,#176b72 100%); color: white; margin-bottom: 1rem;}
  .hero-kicker {font-size:.76rem; letter-spacing:.14em; text-transform:uppercase; color:#b9e6e8; font-weight:700;}
  .hero-title {font-size:2rem; font-weight:800; margin:.35rem 0 .25rem 0;}
  .hero-sub {color:#d8e7f2; font-size:.95rem;}
  .small-note {color:#64748b; font-size:.82rem;}
  div[data-testid="stMetric"] {background:var(--secondary-background-color); border:1px solid rgba(128,128,128,.18); padding:14px 16px; border-radius:16px;}
  div[data-testid="stMetricLabel"] {font-weight:600;}
  div[data-testid="stTabs"] button {font-weight:650;}
  .pill {display:inline-block;padding:.22rem .55rem;border-radius:99px;background:#fff3cd;color:#815a00;font-size:.75rem;font-weight:700;}
</style>
<div class="hero">
  <div class="hero-kicker">Decision intelligence · Pricing analytics</div>
  <div class="hero-title">Causal Pricing Intelligence Studio</div>
  <div class="hero-sub">Explore market performance, pricing signals, synthetic-control diagnostics and DML outputs in one workspace.</div>
</div>
""", unsafe_allow_html=True)
st.warning("SIMULATED DEVELOPMENT DATA. Charts and estimates are for software development and demonstration only; they are not real-world business evidence or validated causal conclusions.")

@st.cache_data(show_spinner="Loading transaction panel…")
def load_data(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    if "treatment_date" in frame:
        frame["treatment_date"] = pd.to_datetime(frame["treatment_date"], errors="coerce")
    for col in ["price", "competitor_price", "promotion", "treated_market", "treatment", "units_sold", "revenue", "gross_profit", "seasonal_index", "unit_cost", "day_of_week"]:
        if col in frame:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    return frame






def money(value):
    return f"{value:,.0f}" if pd.notna(value) else "—"

def layout(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=12,r=12,t=58,b=12), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans, sans-serif", size=12), legend_title_text="")
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,.18)", zeroline=False)
    return fig

def safe_mean(frame, col):
    return float(frame[col].mean()) if col in frame and frame[col].notna().any() else float("nan")

if not CSV_PATH.exists():
    st.error(f"Transaction file not found: {CSV_PATH}. Keep the CSV in the package's data folder.")
    st.stop()
try:
    df = load_data(str(CSV_PATH))
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

required = {"date", "market_id", "product_id", "treated_market", "treatment", "price", "units_sold", "revenue", "gross_profit"}
missing_cols = sorted(required - set(df.columns))
if missing_cols:
    st.error(f"Required columns missing: {missing_cols}")
    st.stop()
df = df.dropna(subset=["date"]).copy()




# ---------- Interactive filters ----------
with st.sidebar:
    st.markdown("## Explore the data")
    st.caption("All views update from the filters below.")
    date_min, date_max = df.date.min().date(), df.date.max().date()
    date_range = st.date_input("Analysis period", value=(date_min, date_max), min_value=date_min, max_value=date_max, key="date_range")
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    else:
        start, end = pd.Timestamp(date_min), pd.Timestamp(date_max) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    market_options = sorted(df.market_id.dropna().astype(str).unique())
    product_options = sorted(df.product_id.dropna().astype(str).unique())
    category_options = sorted(df.category.dropna().astype(str).unique()) if "category" in df else []
    markets = st.multiselect("Markets", market_options, default=market_options)
    products = st.multiselect("Products", product_options, default=product_options)
    categories = st.multiselect("Product categories", category_options, default=category_options) if category_options else []
    metric = st.selectbox("Trend metric", ["revenue", "gross_profit", "units_sold", "price", "competitor_price"], index=0)
    grain = st.radio("Trend granularity", ["Daily", "Weekly", "Monthly"], horizontal=True)
    st.divider()
    if st.button("Reset all filters", use_container_width=True):
        st.session_state.clear()
        st.rerun()

f = df[(df.date >= start) & (df.date <= end)]
f = f[f.market_id.astype(str).isin(markets) & f.product_id.astype(str).isin(products)]
if categories and "category" in f:
    f = f[f.category.astype(str).isin(categories)]
if f.empty:
    st.info("No observations match these filters. Widen the date range or select more markets/products.")
    st.stop()

# period aggregation
freq = {"Daily":"D", "Weekly":"W-MON", "Monthly":"MS"}[grain]
f["period"] = f["date"].dt.to_period("D") if grain == "Daily" else f["date"].dt.to_period("W") if grain == "Weekly" else f["date"].dt.to_period("M")
# Use timestamps for plotly axes; weekly labels are period starts.
f["period_start"] = f["date"].dt.floor("D") if grain == "Daily" else f["date"].dt.to_period("W-MON").dt.start_time if grain == "Weekly" else f["date"].dt.to_period("M").dt.start_time

# ---------- KPI row ----------
st.markdown("### Performance snapshot")
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Revenue", money(f.revenue.sum()), help="Sum for the selected filters; currency was not specified in the dataset.")
k2.metric("Gross profit", money(f.gross_profit.sum()))
k3.metric("Units sold", f"{f.units_sold.sum(skipna=True):,.0f}")
k4.metric("Avg. selling price", f"{safe_mean(f, 'price'):,.2f}")
k5.metric("Observations", f"{len(f):,}")
st.caption(f"Showing {f.date.min():%d %b %Y} – {f.date.max():%d %b %Y} · {f.market_id.nunique()} markets · {f.product_id.nunique()} products. Financial currency/unit is unspecified.")

# ---------- Main navigation ----------
tabs = st.tabs(["✨ Overview", "🧭 Market & Product", "🏷️ Pricing & Promotions", "🧪 Synthetic Control", "🧠 DML Diagnostics", "🛡️ Data Quality"])

with tabs[0]:
    left, right = st.columns([1.65, 1])
    with left:
        st.subheader(f"{grain} {metric.replace('_',' ').title()} trend")
        trend = f.groupby(["period_start", "treated_market"], as_index=False).agg(value=(metric, "mean" if metric in ["price", "competitor_price"] else "sum"))
        trend["Market group"] = trend.treated_market.map({0:"Untreated markets",1:"Treated markets"}).fillna("Unknown")
        fig = px.line(trend, x="period_start", y="value", color="Market group", markers=grain != "Daily", color_discrete_map={"Treated markets":"#0F766E","Untreated markets":"#64748B"}, labels={"period_start":"Period","value":metric.replace('_',' ').title()})
        if start <= INTERVENTION_DATE <= end:
            fig.add_vline(x=INTERVENTION_DATE, line_dash="dash", line_color="#D97706", annotation_text="Simulated price intervention")
        st.plotly_chart(layout(fig, 390), use_container_width=True)
    with right:
        st.subheader("Outcome mix")
        mix = f.groupby("treated_market", as_index=False).agg(revenue=("revenue","sum"), gross_profit=("gross_profit","sum"))
        mix["Market group"] = mix.treated_market.map({0:"Untreated",1:"Treated"}).fillna("Unknown")
        fig = px.bar(mix, x="Market group", y=["revenue","gross_profit"], barmode="group", color_discrete_sequence=["#2563EB","#14B8A6"], labels={"value":"Total","variable":"Measure"})
        st.plotly_chart(layout(fig, 390), use_container_width=True)
    st.subheader("How price and demand move together")
    sample = f.sample(min(6000, len(f)), random_state=42) if len(f) > 6000 else f
    fig = px.scatter(sample, x="price", y="units_sold", color="treated_market", symbol="promotion" if "promotion" in sample else None, hover_data=["market_id","product_id","date"], opacity=.55, color_discrete_sequence=["#64748B","#0F766E"], labels={"price":"Selling price","units_sold":"Units sold","treated_market":"Treated market"})
    st.plotly_chart(layout(fig, 410), use_container_width=True)
    st.caption("These are descriptive relationships. The charts do not by themselves establish a causal pricing effect.")

with tabs[1]:
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("Market performance")
        market_summary = f.groupby(["market_id","treated_market"], as_index=False).agg(revenue=("revenue","sum"), gross_profit=("gross_profit","sum"), units=("units_sold","sum"), avg_price=("price","mean"), rows=("date","size"))
        market_summary["Group"] = market_summary.treated_market.map({0:"Untreated",1:"Treated"})
        fig = px.bar(market_summary.sort_values("revenue"), x="revenue", y="market_id", color="Group", orientation="h", color_discrete_map={"Treated":"#0F766E","Untreated":"#94A3B8"}, hover_data=["gross_profit","units","avg_price","rows"], labels={"revenue":"Revenue","market_id":"Market"})
        st.plotly_chart(layout(fig, 460), use_container_width=True)
    with c2:
        st.subheader("Product/category performance")
        group_cols = ["product_id"] + (["category"] if "category" in f else [])
        product_summary = f.groupby(group_cols, as_index=False, dropna=False).agg(revenue=("revenue","sum"), units=("units_sold","sum"), avg_price=("price","mean"), gross_profit=("gross_profit","sum"))
        fig = px.treemap(product_summary, path=group_cols, values="revenue", color="gross_profit", color_continuous_scale="Tealgrn", hover_data={"units":":,.0f","avg_price":":.2f"})
        st.plotly_chart(layout(fig, 460), use_container_width=True)
    st.subheader("Market detail — sortable and searchable")
    st.dataframe(market_summary.sort_values("revenue", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download market summary", market_summary.to_csv(index=False).encode(), "market_summary.csv", "text/csv")

with tabs[2]:
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("Selling price vs competitor price")
        price_df = f.dropna(subset=["price","competitor_price"]).copy()
        price_df["Price gap"] = price_df["price"] - price_df["competitor_price"]
        fig = px.histogram(price_df, x="Price gap", color="treated_market", nbins=45, barmode="overlay", opacity=.72, color_discrete_sequence=["#94A3B8","#0F766E"], labels={"Price gap":"Our price − competitor price","treated_market":"Treated market"})
        st.plotly_chart(layout(fig, 370), use_container_width=True)
    with c2:
        st.subheader("Promotion comparison")
        if "promotion" in f:
            promo = f.groupby("promotion", as_index=False).agg(avg_units=("units_sold","mean"), avg_revenue=("revenue","mean"), observations=("date","size"))
            promo["Promotion status"] = promo.promotion.map({0:"No promotion",1:"Promotion"}).fillna("Unknown")
            fig = px.bar(promo, x="Promotion status", y=["avg_units","avg_revenue"], barmode="group", color_discrete_sequence=["#2563EB","#14B8A6"], labels={"value":"Mean per record","variable":"Measure"}, hover_data=["observations"])
            st.plotly_chart(layout(fig, 370), use_container_width=True)
        else:
            st.info("Promotion field is unavailable in this dataset.")
    st.subheader("Price distribution by market group")
    fig = px.box(f, x="treated_market", y="price", color="treated_market", points=False, color_discrete_sequence=["#94A3B8","#0F766E"], labels={"treated_market":"Treated market (0/1)","price":"Selling price"})
    st.plotly_chart(layout(fig, 380), use_container_width=True)
    st.caption("Price gaps and promotion comparisons are descriptive; selection and confounding can explain differences.")

with tabs[3]:
    st.subheader("Synthetic Control diagnostics")
    st.info("Existing project artifacts are shown as supplied. Recheck the design, fit and placebo assumptions before interpreting a post-treatment gap causally.")
    diag_path = DATA / "scm_diagnostics_mspe.csv"
    if diag_path.exists():
        diag = pd.read_csv(diag_path)
        st.dataframe(diag, use_container_width=True, hide_index=True)
        if {"market","ratio"}.issubset(diag.columns):
            fig = px.bar(diag, x="market", y="ratio", color="ratio", color_continuous_scale="Tealgrn", labels={"ratio":"Post-/pre-treatment MSPE ratio","market":"Market"})
            st.plotly_chart(layout(fig, 350), use_container_width=True)
    for filename, label in [("actual_vs_synthetic_gross_profit.png","Gross profit: actual vs synthetic"),("actual_vs_synthetic_units.png","Units sold: actual vs synthetic")]:
        path = DATA / filename
        if path.exists():
            st.subheader(label)
            st.image(str(path), use_container_width=True)
    weights_path = DATA / "estimated_scm_weights.csv"
    if weights_path.exists():
        with st.expander("Inspect estimated donor weights"):
            weights = pd.read_csv(weights_path)
            st.dataframe(weights, use_container_width=True, hide_index=True)
            st.download_button("Download donor weights", weights.to_csv(index=False).encode(), "estimated_scm_weights.csv", "text/csv")

with tabs[4]:
    st.subheader("Double Machine Learning outputs")
    est_path = DATA / "dml_estimates_exploratory.csv"
    if est_path.exists():
        estimates = pd.read_csv(est_path)
        st.warning("Exploratory estimates on simulated data. IID-only standard errors do not account for market/product/time dependence and must not be presented as final confidence intervals.")
        display_cols = [c for c in ["outcome","n_rows_used","dml_point_estimate_exploratory","iid_only_standard_error_not_for_final_inference","propensity_min","propensity_max","fraction_outside_0.05_0.95","causal_status"] if c in estimates.columns]
        st.dataframe(estimates[display_cols], use_container_width=True, hide_index=True)
        if {"outcome","dml_point_estimate_exploratory"}.issubset(estimates.columns):
            fig = px.bar(estimates, x="outcome", y="dml_point_estimate_exploratory", color="causal_status" if "causal_status" in estimates else None, hover_data=[c for c in ["n_rows_used","propensity_min","propensity_max","fraction_outside_0.05_0.95"] if c in estimates], labels={"dml_point_estimate_exploratory":"Exploratory estimate","outcome":"Outcome","causal_status":"Status"}, color_discrete_sequence=["#0F766E","#D97706","#64748B"])
            st.plotly_chart(layout(fig, 370), use_container_width=True)
        for _, row in estimates.iterrows():
            with st.expander(f"Review warnings · {row.get('outcome','outcome')}"):
                st.write("**Identification:**", row.get("identification_warning", "Not supplied"))
                st.write("**Inference:**", row.get("inference_warning", "Not supplied"))
    else:
        st.info("No DML output file found. Run the DML pipeline before displaying estimates.")

with tabs[5]:
    st.subheader("Data quality & downloadable extracts")
    checks = []
    checks.append({"Check":"Required columns present","Status":"PASS" if not missing_cols else "FAIL","Details":str(missing_cols) if missing_cols else "All required columns found"})
    invalid_dates = int(pd.to_datetime(df.date, errors="coerce").isna().sum())
    checks.append({"Check":"Valid dates","Status":"PASS" if invalid_dates == 0 else "FAIL","Details":f"Invalid dates: {invalid_dates}"})
    dup = int(df.duplicated(["market_id","product_id","date"]).sum())
    checks.append({"Check":"Market-product-date key unique","Status":"PASS" if dup == 0 else "REVIEW","Details":f"Duplicate keys: {dup}"})
    for col in ["price","units_sold","revenue","gross_profit"]:
        nneg = int((df[col] < 0).sum())
        checks.append({"Check":f"Non-negative {col}","Status":"PASS" if nneg == 0 else "REVIEW","Details":f"Negative values: {nneg}"})
    st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)
    m = df.isna().sum().rename("Missing values").to_frame()
    m["Missing %"] = (m["Missing values"] / len(df) * 100).round(2)
    c1,c2 = st.columns([1,1.4])
    with c1:
        st.subheader("Missingness profile")
        miss = m.reset_index(names="Column").sort_values("Missing %", ascending=True)
        fig = px.bar(miss, x="Missing %", y="Column", orientation="h", color="Missing %", color_continuous_scale="Tealgrn")
        st.plotly_chart(layout(fig, 400), use_container_width=True)
    with c2:
        st.subheader("Missingness detail")
        st.dataframe(m.sort_values("Missing %", ascending=False), use_container_width=True)
    st.subheader("Filtered record explorer")
    st.dataframe(f.drop(columns=["period","period_start"], errors="ignore").head(1000), use_container_width=True, hide_index=True)
    st.download_button("Download filtered records (CSV)", f.drop(columns=["period","period_start"], errors="ignore").to_csv(index=False).encode("utf-8"), "filtered_pricing_records.csv", "text/csv")
    st.download_button("Download quality checks (CSV)", pd.DataFrame(checks).to_csv(index=False).encode("utf-8"), "data_quality_checks.csv", "text/csv")

st.divider()
st.caption("Causal Pricing Intelligence Studio · Demo only · All visuals respond to the selected filters · Validate assumptions before causal interpretation.")
