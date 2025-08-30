import streamlit as st
import pandas as pd
from auth import _load_user_prefs, _save_user_prefs

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

def render_filters(all_metrics, wide_df):
    st.markdown("#### Snapshot Options")
    latest_period = wide_df.index.max()
    mode = st.radio(f"Display (Period: {latest_period})", ["Latest", "QoQ Δ", "YoY Δ"], horizontal=True, key="snap_mode")

    important_mets = [
        "Total Revenue", "Net Income", "Operating Income", "EBIT", "EBITDA", "Operating Cash Flow", "Free Cash Flow",
        "EPS", "Diluted EPS", "Total Assets", "Total Liabilities", "Shareholder Equity",
        "Gross Profit", "Gross Margin", "Operating Margin", "Debt To Equity Ratio", "Current Ratio",
        "Current Liabilities", "Total Liabilities Net Minority Interest",
        "Net Debt", "Total Debt", "Working Capital",
        "ROE", "ROA", "PE Ratio"
    ]
    user_defaults = st.session_state.get("user_prefs", {})
    saved_snap = user_defaults.get("snapshot_metrics", [])
    default_snapshot = [m for m in saved_snap if m in all_metrics] or [m for m in important_mets if m in all_metrics]
    snap_metrics = st.multiselect("Metrics to show", all_metrics, default=default_snapshot or all_metrics[:10], key="snap_met")

    if st.button("Save as default snapshot metrics", key="save_snap_btn"):
        all_prefs = _load_user_prefs()
        user = st.session_state.get("user")
        if user:
            all_prefs.setdefault(user, {})["snapshot_metrics"] = snap_metrics
            _save_user_prefs(all_prefs)
            st.session_state.user_prefs = all_prefs[user]
            st.success("Snapshot preferences saved!")

    return {"mode": mode, "snap_metrics": snap_metrics}

def render(ticker_df, all_metrics, filters):
    st.markdown("### Snapshot & Changes")
    
    wide = ticker_df.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
    if wide.empty:
        st.warning("No data available for this ticker.")
        st.stop()
    
    mode = filters["mode"]
    snap_metrics = filters["snap_metrics"]
    
    latest_period = wide.index.max()
    latest_vals = wide.loc[latest_period]

    if mode == "Latest":
        delta_vals = {m: None for m in snap_metrics}
        pct_vals = {m: None for m in snap_metrics}
    elif mode == "QoQ Δ":
        prev_period = wide.index[-2] if len(wide.index) >= 2 else None
        if prev_period is not None:
            delta_vals = latest_vals - wide.loc[prev_period]
            pct_vals = (latest_vals - wide.loc[prev_period]) / abs(wide.loc[prev_period]) * 100
        else:
            delta_vals = {m: None for m in snap_metrics}
            pct_vals = {m: None for m in snap_metrics}
    else:  # YoY Δ
        try:
            target_idx = wide.index.get_loc(latest_period) - 4
            prev_period = wide.index[target_idx] if target_idx >= 0 else None
        except (KeyError, IndexError):
            prev_period = None
        if prev_period is not None:
            delta_vals = latest_vals - wide.loc[prev_period]
            pct_vals = (latest_vals - wide.loc[prev_period]) / abs(wide.loc[prev_period]) * 100
        else:
            delta_vals = {m: None for m in snap_metrics}
            pct_vals = {m: None for m in snap_metrics}

    n_cols = 3
    rows = (len(snap_metrics) + n_cols - 1) // n_cols
    metric_iter = iter(snap_metrics)
    for _ in range(rows):
        row_cols = st.columns(n_cols)
        for c in row_cols:
            try:
                metric = next(metric_iter)
            except StopIteration:
                break
            val = latest_vals.get(metric)
            delta = delta_vals.get(metric) if isinstance(delta_vals, (pd.Series, dict)) else None
            pct = pct_vals.get(metric) if isinstance(pct_vals, (pd.Series, dict)) else None
            if delta is not None and pd.notna(delta):
                if pct is not None and pd.notna(pct):
                    delta_fmt = f"{human_format(delta)}  ({pct:+.1f}%)"
                else:
                    delta_fmt = human_format(delta)
            else:
                delta_fmt = "N/A"
            c.metric(metric, human_format(val), delta_fmt if mode != "Latest" else None)

    st.caption("Data source: Yahoo Finance via yfinance • App generated automatically")