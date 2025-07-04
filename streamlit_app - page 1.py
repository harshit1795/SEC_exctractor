import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="S&P 500 Fundamentals Explorer", layout="wide")

@st.cache_data(show_spinner=True)
def load_data(path: str = "fundamentals_tall.parquet") -> pd.DataFrame:
    """Load the tall fundamentals dataset from Parquet and cache it."""
    return pd.read_parquet(path)

st.title("📈 S&P 500 Fundamentals Explorer")

# 1️⃣ Load data
with st.spinner("Loading fundamentals data…"):
    df = load_data()

# 2️⃣ Sidebar controls
st.sidebar.header("Filters")
all_tickers = sorted(df["Ticker"].unique())
selected_ticker = st.sidebar.selectbox("Ticker", all_tickers, index=all_tickers.index("AAPL") if "AAPL" in all_tickers else 0)

# Filter for chosen ticker
ticker_df = df[df["Ticker"] == selected_ticker]

# Category selection (IncomeStatement, BalanceSheet, CashFlow)
categories = ticker_df["Category"].unique().tolist()
selected_category = st.sidebar.selectbox("Statement", categories)

cat_df = ticker_df[ticker_df["Category"] == selected_category]

# Metric multiselect with search
all_metrics = sorted(cat_df["Metric"].unique())
preselect = [m for m in ["Revenue", "Net Income", "Operating Cash Flow"] if m in all_metrics][:1]
selected_metrics = st.sidebar.multiselect("Metrics", all_metrics, default=preselect or all_metrics[:3])

if not selected_metrics:
    st.warning("Please select at least one metric.")
    st.stop()

# 3️⃣ Main area – line charts
st.subheader(f"{selected_ticker} – {selected_category} metrics")

# Convert FiscalPeriod to ordered categorical for nice x-axis ordering
cat_df = cat_df.copy()
cat_df["FiscalPeriod"] = pd.Categorical(cat_df["FiscalPeriod"], ordered=True,
                                         categories=sorted(cat_df["FiscalPeriod"].unique()))

for metric in selected_metrics:
    metric_df = cat_df[cat_df["Metric"] == metric].sort_values("FiscalPeriod")
    if metric_df.empty:
        st.info(f"No data for {metric}.")
        continue

    base = alt.Chart(metric_df).encode(
        x=alt.X("FiscalPeriod", sort=None, title="Fiscal Period"),
        y=alt.Y("Value", title=metric),
        tooltip=["FiscalPeriod", "Value"]
    )
    line = base.mark_line(point=True, interpolate="monotone", color="#1f77b4")
    st.altair_chart(line.properties(height=300, width=900), use_container_width=True)

# 4️⃣ Drill-down data table
with st.expander("🔍 Data Table – click to view / export"):
    pivot = cat_df[cat_df["Metric"].isin(selected_metrics)].pivot(index="FiscalPeriod", columns="Metric", values="Value")
    pivot = pivot.sort_index(ascending=False)
    st.dataframe(pivot, use_container_width=True)

st.caption("Data source: Yahoo Finance via yfinance • App generated automatically") 