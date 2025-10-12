import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf
from fred_data import get_multiple_fred_series
from .charting_utils import render_filter_bar, render_altair_chart

@st.cache_data
def get_earnings_data(ticker_symbol):
    """Fetches historical earnings data for a given ticker."""
    earnings_dates = yf.Ticker(ticker_symbol).earnings_dates
    if earnings_dates is None or earnings_dates.empty:
        return pd.DataFrame()
    
    earnings_dates.index = pd.to_datetime(earnings_dates.index, utc=True)
    return earnings_dates[['Reported EPS', 'EPS Estimate']]

@st.cache_data
def prepare_fundamentals_data(ticker_df):
    """Prepares and cleans the fundamental metrics data."""
    if ticker_df.empty:
        return pd.DataFrame(), []

    def robust_period_to_date(period):
        try:
            if 'Q' in str(period):
                year, quarter = period.split('Q')
                date = pd.to_datetime(f'{year}-{int(quarter) * 3}-01') + pd.offsets.QuarterEnd(0)
                return date
            else:
                return pd.to_datetime(f'{period}-12-31')
        except (ValueError, TypeError):
            return pd.NaT

    ticker_df['Date'] = ticker_df['FiscalPeriod'].apply(robust_period_to_date)
    ticker_df.dropna(subset=['Date'], inplace=True)

    if ticker_df.empty:
        return pd.DataFrame(), []

    pivot_df = ticker_df.pivot_table(index='Date', columns='Metric', values='Value', aggfunc='first')
    pivot_df.index = pivot_df.index.tz_localize('UTC')
    all_metrics = sorted(pivot_df.columns.tolist())
    return pivot_df, all_metrics

def render_filters(ticker_df, selected_ticker):
    st.markdown("#### 360 Filters")
    
    fundamentals_df, fundamental_metrics = prepare_fundamentals_data(ticker_df.copy())
    earnings_df = get_earnings_data(selected_ticker)

    with st.expander("Company Fundamentals", expanded=True):
        selected_fundamentals = st.multiselect("Select fundamental metrics:", options=fundamental_metrics, default=fundamental_metrics[:1] if fundamental_metrics else [])
    with st.expander("Earnings", expanded=True):
        selected_earnings = st.multiselect("Select earnings metrics:", options=['Reported EPS', 'EPS Estimate'], default=['Reported EPS'])
    with st.expander("Macroeconomic Data", expanded=True):
        INDICATORS = {
            "Real GDP": {"id": "GDPC1", "freq": "q"},
            "Inflation (CPI)": {"id": "CPIAUCSL", "freq": "m"},
            "Unemployment Rate": {"id": "UNRATE", "freq": "m"},
            "10-Year Treasury Yield": {"id": "DGS10", "freq": "d"},
        }
        selected_fred_keys = st.multiselect("Select macroeconomic indicators:", options=list(INDICATORS.keys()))

    combined_df = pd.concat([fundamentals_df[selected_fundamentals], earnings_df[selected_earnings]], axis=1).sort_index()
    
    start_date, end_date, aggregation_period, chart_type, chart_view = render_filter_bar(combined_df, "360", ['Monthly', 'Quarterly', 'Yearly'], ["Line", "Bar", "Scatter"], default_agg_index=1)

    return {
        "selected_fundamentals": selected_fundamentals,
        "selected_earnings": selected_earnings,
        "selected_fred_keys": selected_fred_keys,
        "start_date": start_date,
        "end_date": end_date,
        "aggregation_period": aggregation_period,
        "chart_type": chart_type,
        "chart_view": chart_view,
        "INDICATORS": INDICATORS
    }

def render_content(ticker_df, selected_ticker, filters):
    st.markdown("### FinQ 360")
    st.write("Create custom charts by combining company fundamentals, earnings, and macroeconomic data.")

    selected_fundamentals = filters.get("selected_fundamentals", [])
    selected_earnings = filters.get("selected_earnings", [])
    selected_fred_keys = filters.get("selected_fred_keys", [])
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    aggregation_period = filters.get("aggregation_period", "Quarterly")
    chart_type = filters.get("chart_type", "Line")
    chart_view = filters.get("chart_view", "Combined")
    INDICATORS = filters.get("INDICATORS", {})

    all_selected_metrics = selected_fundamentals + selected_earnings + selected_fred_keys
    if not all_selected_metrics:
        st.info("Please select at least one metric to plot.")
        return

    fundamentals_df, _ = prepare_fundamentals_data(ticker_df.copy())
    earnings_df = get_earnings_data(selected_ticker)
    
    fred_df = pd.DataFrame()
    if selected_fred_keys:
        series_info_to_fetch = {INDICATORS[key]["id"]: INDICATORS[key]["freq"] for key in selected_fred_keys}
        fred_df = get_multiple_fred_series(series_info_to_fetch, "2000-01-01", pd.to_datetime("today").strftime('%Y-%m-%d'))
        fred_df.columns = [key for key, val in INDICATORS.items() if val['id'] in fred_df.columns]

    combined_df = pd.concat([fundamentals_df[selected_fundamentals], earnings_df[selected_earnings], fred_df], axis=1).sort_index()
    combined_df.dropna(how='all', inplace=True)

    if combined_df.empty:
        st.warning("No data available for the selected metrics.")
        return

    filtered_df = combined_df[(combined_df.index >= pd.to_datetime(start_date, utc=True)) & (combined_df.index <= pd.to_datetime(end_date, utc=True))]
    period_map = {'Monthly': 'M', 'Quarterly': 'Q', 'Yearly': 'A'}
    agg_df = filtered_df.resample(period_map[aggregation_period]).mean(numeric_only=True)

    if agg_df.empty:
        st.warning("No data available for the selected filters.")
        return

    st.markdown(f"#### {aggregation_period} Chart")
    st.button("💡 Tips", help="* To Zoom: Place your mouse over the chart and use your mouse wheel to scroll.\n* To Pan: Click and drag the chart to move it up, down, left, or right.\n* To Reset: Double-click on the chart to return to the default view.", disabled=True)

    if chart_type == "Scatter":
        if len(all_selected_metrics) != 2:
            st.warning("Please select exactly two metrics for a scatter plot.")
        else:
            scatter_df = agg_df[all_selected_metrics].dropna()
            chart = alt.Chart(scatter_df).mark_point().encode(
                x=alt.X(all_selected_metrics[0], type='quantitative'),
                y=alt.Y(all_selected_metrics[1], type='quantitative'),
                tooltip=all_selected_metrics
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
    else:
        agg_df.index.name = 'Date'
        melted_df = agg_df.reset_index().melt(id_vars='Date', var_name='Metric', value_name='Value')
        render_altair_chart(
            df=melted_df,
            aggregation_period=aggregation_period,
            chart_type=chart_type,
            chart_view=chart_view,
            x_col='Date',
            y_col='Value',
            color_col='Metric',
            chart_title="Combined Metric Analysis"
        )
