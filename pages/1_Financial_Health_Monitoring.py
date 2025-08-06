import streamlit as st
import pandas as pd
import numpy as np
from auth import show_login_ui, _load_user_prefs, _save_user_prefs


def human_format(num):
    """Convert a number to human-readable USD (e.g. $3.4B, $120M, $950)."""
    if num is None or pd.isna(num):
        return "N/A"
    sign = "-" if num < 0 else ""
    num = abs(num)
    for unit in ["", "K", "M", "B", "T"]:
        if num < 1000:
            formatted = f"{num:,.1f}{unit}" if unit else f"{num:,.0f}"
            return f"{sign}${formatted}"
        num /= 1000
    return f"{sign}${num:.1f}P"


if not st.session_state.get("logged_in", False):
    show_login_ui()
    st.stop()

st.markdown("<h2 style='text-align: center;'>🩺 Financial Health Monitoring</h2>", unsafe_allow_html=True)

# Load data
df = pd.read_parquet("fundamentals_tall.parquet")
_TICKER_META = pd.read_csv("sp500_fundamentals.csv")[["Ticker", "Name", "Sector", "Industry"]].set_index("Ticker").to_dict("index")

# Build sector metadata dynamically (cached)
@st.cache_data(show_spinner=False)
def build_meta():
    """Construct ticker → name/sector dataframe using cached metadata (no network)."""
    if _TICKER_META:
        mdf = pd.DataFrame.from_dict(_TICKER_META, orient="index").reset_index()
        mdf = mdf.rename(columns={"index": "Ticker", "Name": "Name", "Sector": "Sector"})
        return mdf
    # Fallback (should be rare): derive from fundamentals table
    return pd.DataFrame({
        "Ticker": df["Ticker"].unique(),
        "Name": df["Ticker"].unique(),
        "Sector": "Unknown",
    })

meta = build_meta()

# Map to broader categories
sector_map = {
    "Information Technology": "Technology",
    "Technology": "Technology",
    "Communication Services": "Technology",
    "Consumer Discretionary": "Manufacturing",
    "Consumer Cyclical": "Manufacturing",
    "Industrials": "Manufacturing",
    "Materials": "Manufacturing",
    "Energy": "Manufacturing",
    "Health Care": "Public Sector",
    "Healthcare": "Public Sector",
    "Utilities": "Public Sector",
    "Real Estate": "Public Sector",
    "Financials": "Finance",
    "Financial Services": "Finance",
    "Consumer Staples": "Finance",
}

meta["Category"] = meta["Sector"].map(sector_map).fillna("Other")

finq_tab, custom_tab = st.tabs(["💡 FinQ Suggestions", "⚙️ Custom Health Score"])

with finq_tab:
    st.header("FinQ Suggestions")
    st.markdown("**Health Score Formula:** `(Growth_score + NetMargin_score + FCFMargin_score + (1 - DebtEquity_score)) / 4`")
    with st.expander("How are individual metrics scored?"):
        st.markdown("""
        Each metric (Growth, Net Margin, FCF Margin, Debt to Equity) is converted into a score between 0 and 1 
        using percentile ranking. A higher percentile rank indicates a better score.
        
        *   **Growth_score, NetMargin_score, FCFMargin_score:** These are directly the percentile ranks of the respective metrics. 
            For example, a company with a Growth_score of 0.9 means its revenue growth is better than 90% of other companies.
        *   **DebtEquity_score:** This is calculated as `1 - percentile_rank(Debt to Equity)`. This is because a lower Debt to Equity ratio is generally better, 
            so we invert the percentile rank to ensure a higher score indicates better financial health.
        
        The final Health Score is the average of these individual metric scores.
        """)

    # ---------------- Health score computation ---------------- #
    @st.cache_data(show_spinner=True)
    def compute_health_scores() -> pd.DataFrame:
        records = []
        for tkr in df["Ticker"].unique():
            tdf = df[df["Ticker"] == tkr]
            # pivot_table tolerates duplicate FiscalPeriod/Metric combinations
            wide = tdf.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
            if wide.empty or wide.shape[0] < 5:
                continue
            latest = wide.iloc[-1]
            # --- Key metrics --- #
            # Use 'Total Revenue' metric from Yahoo Finance fundamentals
            revenue_col = "Total Revenue" if "Total Revenue" in wide.columns else None
            if revenue_col is None:
                continue  # skip if revenue not available
            try:
                rev_latest = latest[revenue_col]
                rev_prev = wide.iloc[-5][revenue_col]
            except Exception:
                rev_latest = np.nan
                rev_prev = np.nan

            growth = (rev_latest - rev_prev) / abs(rev_prev) if pd.notna(rev_latest) and pd.notna(rev_prev) and rev_prev != 0 else np.nan

            try:
                net_margin = latest.get("Net Income", np.nan) / rev_latest if rev_latest else np.nan
            except Exception:
                net_margin = np.nan

            try:
                fcf_margin = latest.get("Free Cash Flow", np.nan) / rev_latest if rev_latest else np.nan
            except Exception:
                fcf_margin = np.nan

            try:
                debt_equity = latest["Total Liabilities"] / latest["Shareholder Equity"] if latest["Shareholder Equity"] else np.nan
            except Exception:
                debt_equity = np.nan

            # --- Build quick insights text --- #
            insight_parts = []
            if pd.notna(growth):
                insight_parts.append("Revenue " + ("grew" if growth > 0 else "declined") + f" {growth*100:,.1f}% YoY")
            if pd.notna(net_margin):
                insight_parts.append(f"Net margin {net_margin*100:,.1f}%")
            if pd.notna(fcf_margin):
                insight_parts.append(f"FCF margin {fcf_margin*100:,.1f}%")
            if pd.notna(debt_equity):
                insight_parts.append(f"D/E {debt_equity:,.2f}")

            risk_flags = []
            if pd.notna(growth) and growth < 0:
                risk_flags.append("Revenue contraction")
            if pd.notna(net_margin) and net_margin < 0:
                risk_flags.append("Negative profitability")
            if pd.notna(fcf_margin) and fcf_margin < 0:
                risk_flags.append("Cash burn")
            if pd.notna(debt_equity) and debt_equity > 1.5:
                risk_flags.append("High leverage")

            insight = "; ".join(insight_parts)
            if risk_flags:
                insight += " • Risk: " + ", ".join(risk_flags)

            records.append({
                "Ticker": tkr,
                "Growth": growth,
                "NetMargin": net_margin,
                "FCFMargin": fcf_margin,
                "DebtEquity": debt_equity,
                "Insight": insight,
            })
        score_df = pd.DataFrame(records)
        # Percentile ranks (skip NaNs)
        for col in ["Growth", "NetMargin", "FCFMargin"]:
            score_df[col + "_score"] = score_df[col].rank(pct=True, na_option="bottom")
        # DebtEquity lower better
        score_df["DebtEquity_score"] = 1 - score_df["DebtEquity"].rank(pct=True, na_option="bottom")
        score_df["HealthScore"] = score_df[[c for c in score_df.columns if c.endswith("_score")]].mean(axis=1, skipna=True)
        score_df = score_df.dropna(subset=["HealthScore"])
        return score_df

    score_df = compute_health_scores()
    meta_finq = meta.merge(score_df[["Ticker", "HealthScore", "Insight"]], on="Ticker", how="left")

    categories_finq = sorted(meta_finq["Category"].unique())
    selected_cat_finq = st.selectbox("Select Category", categories_finq, key="fh_category_finq")

    cat_df_finq = meta_finq[meta_finq["Category"] == selected_cat_finq].dropna(subset=["HealthScore"])
    top_df_finq = cat_df_finq.sort_values("HealthScore", ascending=False).head(10)

    if top_df_finq.empty:
        st.info("No sufficient data to compute health scores for this category yet.")
    else:
        st.markdown(f"### Top Stocks in {selected_cat_finq}")
        display_cols_finq = ["Ticker", "Name", "Sector", "HealthScore", "Insight"]
        if "Insight" not in top_df_finq.columns:
            top_df_finq["Insight"] = "Data insufficient"
        # Round HealthScore
        top_df_finq["HealthScore"] = top_df_finq["HealthScore"].round(2)
        st.dataframe(top_df_finq[display_cols_finq].reset_index(drop=True), use_container_width=True)

with custom_tab:
    st.header("Your Selections")

    # Get the list of available metrics
    available_metrics = df["Metric"].unique()

    # Load user preferences
    user_prefs = _load_user_prefs().get(st.session_state.get("user", ""), {})
    
    selected_metrics = st.multiselect(
        "Select your preferred metrics for health score calculation:",
        available_metrics,
        default=user_prefs.get("health_metrics", [])
    )

    if st.button("Save Preferences"):
        all_prefs = _load_user_prefs()
        user = st.session_state.get("user")
        if user:
            all_prefs.setdefault(user, {})["health_metrics"] = selected_metrics
            _save_user_prefs(all_prefs)
            st.success("Preferences saved!")

    if selected_metrics:
        # Display dynamic formula
        formula_str = " + ".join([f"`{m}_score`" for m in selected_metrics])
        st.markdown(f"""**Custom Health Score Formula:** `({formula_str}) / {len(selected_metrics)}`""")
        with st.expander("How are individual metrics scored?"):
            st.markdown("""
            Each selected metric is converted into a score between 0 and 1 using percentile ranking. 
            A higher percentile rank indicates a better score. 
            
            **Note:** For simplicity, this calculation assumes that a higher value for each selected metric is always better. 
            If you select metrics where a lower value is preferable (e.g., Debt-to-Equity Ratio), 
            you may need to manually invert its contribution to the overall score for accurate results.
            """)
        
        st.subheader("Custom Health Score Analysis")

        # Filter the DataFrame to include only the selected metrics
        filtered_df = df[df["Metric"].isin(selected_metrics)]

        # Normalize the metrics (example: percentile ranking)
        normalized_df = filtered_df.copy()
        for metric in selected_metrics:
            # Assuming higher is better for all metrics for simplicity.
            # A real implementation would need to handle metrics where lower is better.
            normalized_df[metric + "_score"] = normalized_df.groupby("Metric")["Value"].rank(pct=True)

        # Calculate the health score (average of normalized values)
        score_cols = [m + "_score" for m in selected_metrics]
        health_scores = normalized_df.groupby("Ticker")[score_cols].mean().mean(axis=1).reset_index(name="HealthScore")
        
        # Generate insights based on the selected metrics
        def generate_insight(row):
            ticker = row['Ticker']
            ticker_metrics = filtered_df[filtered_df['Ticker'] == ticker]
            if ticker_metrics.empty:
                return "N/A"
            
            parts = []
            for metric in selected_metrics:
                # Use .get(0, None) to avoid index errors if a metric is missing for a ticker
                val_series = ticker_metrics[ticker_metrics['Metric'] == metric]['Value']
                val = val_series.iloc[0] if not val_series.empty else None
                parts.append(f"{metric}: {human_format(val)}")
            return "; ".join(parts)

        # Merge with meta data and health scores
        meta_custom = meta.merge(health_scores, on="Ticker", how="left")
        
        # Apply insight generation
        meta_custom['Insight'] = meta_custom.apply(generate_insight, axis=1)

        categories_custom = sorted(meta_custom["Category"].unique())
        selected_cat_custom = st.selectbox("Select Category", categories_custom, key="fh_category_custom")

        cat_df_custom = meta_custom[meta_custom["Category"] == selected_cat_custom].dropna(subset=["HealthScore"])
        top_df_custom = cat_df_custom.sort_values("HealthScore", ascending=False).head(10)

        if top_df_custom.empty:
            st.info("No sufficient data to compute health scores for this category and selection.")
        else:
            st.write("**Top Companies by Custom Health Score:**")
            display_cols_custom = ["Ticker", "Name", "Sector", "HealthScore", "Insight"]
            st.dataframe(top_df_custom[display_cols_custom].reset_index(drop=True).round(2), use_container_width=True)