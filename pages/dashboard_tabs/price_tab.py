import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf
from auth import _load_user_prefs, _save_user_prefs

@st.cache_data(show_spinner=True)
def get_price_history(ticker: str, start_date, end_date) -> pd.DataFrame:
    """Get historical price data from yfinance."""
    return yf.download(ticker, start=start_date, end=end_date)

def render_filters():
    """Renders filters for the price chart and returns their values."""
    st.markdown("#### Chart Options")
    user_prefs = st.session_state.get("user_prefs", {})
    price_prefs = user_prefs.get("price_tab", {})

    start_date = st.date_input("Start date", pd.to_datetime("today") - pd.DateOffset(years=1), key="price_start")
    end_date = st.date_input("End date", pd.to_datetime("today"), key="price_end")
    
    agg_options = ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly']
    default_agg = price_prefs.get("aggregation", "Daily")
    agg_index = agg_options.index(default_agg) if default_agg in agg_options else 0
    aggregation = st.selectbox("Aggregation", agg_options, index=agg_index, key="price_agg")

    chart_type_options = ['Candlestick', 'Line']
    default_chart_type = price_prefs.get("chart_type", "Candlestick")
    chart_type_index = chart_type_options.index(default_chart_type) if default_chart_type in chart_type_options else 0
    chart_type = st.radio("Chart Type", chart_type_options, index=chart_type_index, key="price_chart_type")
    
    line_metric = 'close'
    if chart_type == 'Line':
        metric_options = ['Open', 'High', 'Low', 'Close']
        default_metric = price_prefs.get("line_metric", "Close")
        metric_index = metric_options.index(default_metric) if default_metric in metric_options else 3
        line_metric = st.selectbox("Metric for Line Chart", metric_options, index=metric_index, key="price_line_metric").lower()

    if st.button("Save Chart Settings", key="save_price_prefs"):
        all_prefs = _load_user_prefs()
        user = st.session_state.get("user")
        if user:
            user_prefs = all_prefs.setdefault(user, {})
            user_prefs["price_tab"] = {
                "aggregation": aggregation,
                "chart_type": chart_type,
                "line_metric": line_metric
            }
            _save_user_prefs(all_prefs)
            st.session_state.user_prefs = user_prefs
            st.success("Price chart preferences saved!")
        
    return {
        "start_date": start_date,
        "end_date": end_date,
        "aggregation": aggregation,
        "chart_type": chart_type,
        "line_metric": line_metric
    }

def render(selected_ticker, filters):
    st.markdown("### Price Chart")

    start_date = filters['start_date']
    end_date = filters['end_date']
    aggregation = filters['aggregation']
    chart_type = filters['chart_type']
    line_metric = filters['line_metric']

    price_df = get_price_history(selected_ticker, start_date, end_date)

    if not price_df.empty:
        price_df.index.name = 'Date'
        price_df = price_df.reset_index()

        if isinstance(price_df.columns, pd.MultiIndex):
            price_df.columns = price_df.columns.get_level_values(0)

        price_df.columns = [str(col).lower() for col in price_df.columns]

        if 'date' not in price_df.columns:
            st.warning("Date column not found in price data after processing.")
            return

        price_df['date'] = pd.to_datetime(price_df['date'])

        if aggregation != 'Daily':
            agg_logic = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }
            period_map = {'Weekly': 'W', 'Monthly': 'M', 'Quarterly': 'Q', 'Yearly': 'A'}
            price_df = price_df.set_index('date').resample(period_map[aggregation]).agg(agg_logic).dropna()
            price_df = price_df.reset_index()

        if price_df.empty:
            st.warning("No data available for the selected aggregation.")
            return

        if aggregation == 'Yearly':
            price_df['Label'] = price_df['date'].dt.strftime('%Y')
            x_title = 'Year'
        elif aggregation == 'Quarterly':
            price_df['Label'] = price_df['date'].dt.to_period('Q').astype(str)
            x_title = 'Quarter'
        elif aggregation == 'Monthly':
            price_df['Label'] = price_df['date'].dt.strftime('%b %Y')
            x_title = 'Month'
        else:
            price_df['Label'] = price_df['date'].dt.strftime('%Y-%m-%d')
            x_title = 'Date'
        
        x_axis = alt.X('Label:O', title=x_title, sort=None)

        min_val = price_df['low'].min()
        max_val = price_df['high'].max()
        padding = (max_val - min_val) * 0.05
        y_domain = [min_val - padding, max_val + padding]
        y_scale = alt.Scale(domain=y_domain, zero=False)

        st.subheader(f"{aggregation} {chart_type} Chart")
        st.button("💡 Tips", help="* To Zoom: Place your mouse over the chart and use your mouse wheel to scroll.\n* To Pan: Click and drag the chart to move it up, down, left, or right.\n* To Reset: Double-click on the chart to return to the default view.", disabled=True)

        if chart_type == 'Candlestick':
            base = alt.Chart(price_df).encode(
                x=x_axis,
                color=alt.condition("datum.open <= datum.close", alt.value("#06982d"), alt.value("#ae1325")),
                tooltip=[
                    alt.Tooltip('Label', title='Date'),
                    alt.Tooltip('open', title='Open', format='.2f'),
                    alt.Tooltip('high', title='High', format='.2f'),
                    alt.Tooltip('low', title='Low', format='.2f'),
                    alt.Tooltip('close', title='Close', format='.2f'),
                    alt.Tooltip('volume', title='Volume', format=',.0f')
                ]
            )
            chart = alt.layer(
                base.mark_rule().encode(y=alt.Y('low:Q', scale=y_scale, title='Price')), 
                base.mark_bar().encode(y='open:Q', y2='close:Q')
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        
        elif chart_type == 'Line':
            line_y_scale = alt.Scale(domain=[price_df[line_metric].min() * 0.95, price_df[line_metric].max() * 1.05], zero=False)
            chart = alt.Chart(price_df).mark_line().encode(
                x=x_axis,
                y=alt.Y(f'{line_metric}:Q', title=f'{line_metric.capitalize()} Price', scale=line_y_scale),
                tooltip=[
                    alt.Tooltip('Label', title='Date'),
                    alt.Tooltip(line_metric, title='Price', format='.2f')
                ]
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Could not retrieve price data for the selected ticker and date range.")