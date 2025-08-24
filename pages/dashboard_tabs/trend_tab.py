import streamlit as st
import pandas as pd
import altair as alt
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

def human_format_for_axis(num):
    """Convert a number to human-readable for axis (e.g. 3.4, 'B')."""
    if num is None or pd.isna(num):
        return num, ""
    num = float(num)
    if abs(num) >= 1_000_000_000:
        return num / 1_000_000_000, "B"
    elif abs(num) >= 1_000_000:
        return num / 1_000_000, "M"
    elif abs(num) >= 1_000:
        return num / 1_000, "K"
    return num, ""

def render(ticker_df, all_metrics):
    st.markdown("### Metrics Trend Analysis")

    # ---------------- Default metrics (use user prefs if available) ---------------- #

    important_mets = [
        "Total Revenue", "Net Income", "Operating Income", "EBIT", "EBITDA", "Operating Cash Flow", "Free Cash Flow",
        "EPS", "Diluted EPS", "Total Assets", "Total Liabilities", "Shareholder Equity",
        "Gross Profit", "Gross Margin", "Operating Margin", "Debt To Equity Ratio", "Current Ratio",
        "Current Liabilities", "Total Liabilities Net Minority Interest",
        "Net Debt", "Total Debt", "Working Capital",
        "ROE", "ROA", "PE Ratio"
    ]
    user_defaults = st.session_state.get("user_prefs", {})
    saved_trend = user_defaults.get("trend_metrics", [])
    default_trend = [m for m in saved_trend if m in all_metrics] or [m for m in important_mets if m in all_metrics][:5]
    selected_metrics_trend = st.multiselect("Metrics to plot", all_metrics, default=default_trend or all_metrics[:5], key="trend_met")

    chart_type_trend = st.radio("Chart Type:", ["Line", "Bar"], key="trend_chart_type", horizontal=True)

    # Save preference button (placed right below selector)
    if st.button(" Save these as my default metrics", key="save_trend_btn"):
        all_prefs = _load_user_prefs()
        user = st.session_state.get("user")
        if user:
            all_prefs.setdefault(user, {})["trend_metrics"] = selected_metrics_trend
            _save_user_prefs(all_prefs)
            st.session_state.user_prefs = all_prefs[user]
            st.success("Preferences saved! They will load automatically next time you sign in.")

    plot_df = ticker_df[ticker_df["Metric"].isin(selected_metrics_trend)].copy()
    plot_df["FiscalPeriod"] = pd.Categorical(plot_df["FiscalPeriod"], ordered=True,
                                              categories=sorted(plot_df["FiscalPeriod"].unique()))

    for metric in selected_metrics_trend:
        mdf = plot_df[plot_df["Metric"] == metric].sort_values("FiscalPeriod")
        if mdf.empty:
            continue
        mdf = mdf.copy()
        mdf["Label"] = mdf["Value"].apply(human_format)

        # Apply custom scaling for axis
        mdf[["Value_Scaled", "Unit"]] = mdf["Value"].apply(lambda x: pd.Series(human_format_for_axis(x)))
        # Determine the most common unit for the current metric
        common_unit = mdf["Unit"].mode()[0] if not mdf["Unit"].empty else ""
        y_axis_title = f"Value ({common_unit})" if common_unit else "Value"

        base = (
            alt.Chart(mdf)
            .encode(
                x=alt.X("FiscalPeriod", sort=None, title="Fiscal Period"),
                y=alt.Y("Value_Scaled", title=y_axis_title),
                tooltip=[alt.Tooltip("FiscalPeriod", title="Period"), alt.Tooltip("Label", title="Value")]
            )
        )
        
        if chart_type_trend == "Line":
            chart_mark = base.mark_line(point=True)
        else: # Bar
            chart_mark = base.mark_bar()

        text = base.mark_text(dy=-10, align="left").encode(text="Label")
        chart = alt.layer(chart_mark, text).properties(height=300, width=900, title=metric)
        st.altair_chart(chart, use_container_width=True)