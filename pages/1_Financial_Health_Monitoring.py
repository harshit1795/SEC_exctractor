
import streamlit as st
import pandas as pd
import numpy as np
from auth import _load_user_prefs, _save_user_prefs

# --- Page Setup ---
st.set_page_config(page_title="Financial Health Monitoring - FinQ", page_icon="🩺")

# --- Authentication Check ---
if not st.session_state.get("logged_in"):
    st.warning("Please log in to access this feature.")
    st.switch_page("Home.py")
    st.stop()

# --- Helper Functions ---
def human_format(num):
    """Convert a number to human-readable USD format."""
    if num is None or pd.isna(num):
        return "N/A"
    sign = "-" if num < 0 else ""
    num = abs(num)
    for unit in ["", "K", "M", "B", "T"]:
        if num < 1000:
            return f"{sign}${num:,.1f}{unit}" if unit else f"{sign}${num:,.0f}"
        num /= 1000
    return f"{sign}${num:.1f}P"

# --- Data Loading ---
@st.cache_data
def load_data():
    """Load and preprocess data."""
    df = pd.read_parquet("fundamentals_tall.parquet")
    meta_df = pd.read_csv("sp500_fundamentals.csv")[["Ticker", "Name", "Sector", "Industry"]].set_index("Ticker")
    
    sector_map = {
        "Information Technology": "Technology", "Communication Services": "Technology",
        "Consumer Discretionary": "Manufacturing", "Industrials": "Manufacturing",
        "Materials": "Manufacturing", "Energy": "Manufacturing",
        "Health Care": "Public Sector", "Utilities": "Public Sector", "Real Estate": "Public Sector",
        "Financials": "Finance", "Consumer Staples": "Finance"
    }
    
    meta = meta_df.reset_index()
    meta["Category"] = meta["Sector"].map(sector_map).fillna("Other")
    return df, meta

df, meta = load_data()

st.markdown("<h2 style='text-align: center;'>🩺 Financial Health Monitoring</h2>", unsafe_allow_html=True)

finq_tab, custom_tab = st.tabs(["💡 FinQ Suggestions", "⚙️ Custom Health Score"])

# --- FinQ Suggestions Tab ---
with finq_tab:
    st.header("FinQ Suggestions")
    st.markdown("**Health Score Formula:** `(Growth_score + NetMargin_score + FCFMargin_score + (1 - DebtEquity_score)) / 4`")
    # ... (expander content remains the same)

    @st.cache_data
    def compute_health_scores() -> pd.DataFrame:
        # ... (computation logic remains the same)
        records = []
        for tkr in df["Ticker"].unique():
            tdf = df[df["Ticker"] == tkr]
            wide = tdf.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
            if wide.empty or wide.shape[0] < 5: continue
            latest = wide.iloc[-1]
            revenue_col = "Total Revenue"
            if revenue_col not in wide.columns: continue
            try:
                rev_latest = latest[revenue_col]
                rev_prev = wide.iloc[-5][revenue_col]
            except KeyError:
                continue
            
            growth = (rev_latest - rev_prev) / abs(rev_prev) if pd.notna(rev_latest) and pd.notna(rev_prev) and rev_prev != 0 else np.nan
            net_margin = latest.get("Net Income", np.nan) / rev_latest if rev_latest else np.nan
            fcf_margin = latest.get("Free Cash Flow", np.nan) / rev_latest if rev_latest else np.nan
            debt_equity = latest["Total Liabilities"] / latest["Shareholder Equity"] if "Total Liabilities" in latest and "Shareholder Equity" in latest and latest["Shareholder Equity"] else np.nan

            insight_parts = []
            if pd.notna(growth): insight_parts.append(f"Revenue {'grew' if growth > 0 else 'declined'} {growth*100:,.1f}% YoY")
            if pd.notna(net_margin): insight_parts.append(f"Net margin {net_margin*100:,.1f}%")
            if pd.notna(fcf_margin): insight_parts.append(f"FCF margin {fcf_margin*100:,.1f}%")
            if pd.notna(debt_equity): insight_parts.append(f"D/E {debt_equity:,.2f}")
            insight = "; ".join(insight_parts)
            
            records.append({"Ticker": tkr, "Growth": growth, "NetMargin": net_margin, "FCFMargin": fcf_margin, "DebtEquity": debt_equity, "Insight": insight})

        score_df = pd.DataFrame(records)
        for col in ["Growth", "NetMargin", "FCFMargin"]:
            score_df[col + "_score"] = score_df[col].rank(pct=True, na_option="bottom")
        score_df["DebtEquity_score"] = 1 - score_df["DebtEquity"].rank(pct=True, na_option="bottom")
        score_df["HealthScore"] = score_df[[c for c in score_df.columns if c.endswith("_score")]].mean(axis=1, skipna=True)
        return score_df.dropna(subset=["HealthScore"])

    score_df = compute_health_scores()
    meta_finq = meta.merge(score_df[["Ticker", "HealthScore", "Insight"]], on="Ticker", how="left")
    
    categories_finq = sorted(meta_finq["Category"].unique())
    selected_cat_finq = st.selectbox("Select Category", categories_finq, key="fh_category_finq")

    cat_df_finq = meta_finq[meta_finq["Category"] == selected_cat_finq].dropna(subset=["HealthScore"])
    top_df_finq = cat_df_finq.sort_values("HealthScore", ascending=False).head(10)
    
    st.dataframe(top_df_finq.reset_index(drop=True).round(2), use_container_width=True)

# --- Custom Health Score Tab ---
with custom_tab:
    st.header("Your Selections")
    available_metrics = df["Metric"].unique()
    
    # Load user preferences for this specific feature
    user_prefs = _load_user_prefs()
    selected_metrics = st.multiselect(
        "Select metrics for your custom health score:",
        available_metrics,
        default=user_prefs.get("health_metrics", [])
    )

    if st.button("Save Health Metric Preferences"):
        user_prefs["health_metrics"] = selected_metrics
        _save_user_prefs(user_prefs)
        st.success("Preferences saved!")

    if selected_metrics:
        # ... (computation and display logic remains the same)
        formula_str = " + ".join([f"`{m}_score`" for m in selected_metrics])
        st.markdown(f"**Custom Health Score Formula:** `({formula_str}) / {len(selected_metrics)}`")

# --- Back to Home ---
if st.button("Back to Main Menu"):
    st.switch_page("Home.py")
