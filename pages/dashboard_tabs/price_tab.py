import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf
from datetime import datetime, timedelta

def render_kpi_chart(main_value, comparison_value, history_df, title):
    col1, col2 = st.columns([1, 2])

    with col1:
        # Ensure main_value is a scalar
        if isinstance(main_value, pd.Series):
            if not main_value.empty:
                main_value = main_value.iloc[0]
            else:
                main_value = 0

        # Ensure comparison_value is a scalar
        if isinstance(comparison_value, pd.Series):
            if not comparison_value.empty:
                comparison_value = comparison_value.iloc[0]
            else:
                comparison_value = None

        if comparison_value is not None:
            delta = main_value - comparison_value
            if comparison_value != 0:
                delta_percent = (delta / comparison_value) * 100
            else:
                delta_percent = 0
        else:
            delta = 0
            delta_percent = 0
        
        st.metric(
            label=title,
            value=f"${main_value:,.2f}",
            delta=f"{delta_percent:,.2f}%"
        )

    with col2:
        chart_df = history_df.reset_index()
        
        # Determine the correct date column
        if 'Date' in chart_df.columns:
            date_column = 'Date'
        elif 'index' in chart_df.columns:
            date_column = 'index'
        else:
            st.error("Could not find a date column for the sparkline chart.")
            return

        # Create a sparkline chart
        sparkline = alt.Chart(chart_df).mark_line().encode(
            x=alt.X(f'{date_column}:T', title='Date'),
            y=alt.Y('Close:Q', axis=alt.Axis(labels=False, title=None)),
            tooltip=[alt.Tooltip(f'{date_column}:T', title='Date'), alt.Tooltip('Close:Q', title='Close')]
        ).properties(
            width=200,
            height=80
        ).configure_axis(
            grid=False
        ).configure_view(
            strokeWidth=0
        )
        st.altair_chart(sparkline)


@st.cache_data(show_spinner=True)
def get_price_history(ticker: str, start_date, end_date) -> pd.DataFrame:
    """Get historical price data from yfinance."""
    return yf.download(ticker, start=start_date, end=end_date)

def render(selected_ticker):
    st.markdown("### Price Chart")

    # --- FILTERS ---
    c1, c2 = st.columns(2)
    with c1:
        start_date_input = st.date_input("Start date", pd.to_datetime("today") - pd.DateOffset(months=1), key="price_start")
    with c2:
        end_date_input = st.date_input("End date", pd.to_datetime("today"), key="price_end")

    # --- DATA FETCHING ---
    # Fetch last year of data for all calculations
    price_df_full_year = get_price_history(selected_ticker, pd.to_datetime("today") - pd.DateOffset(years=1), pd.to_datetime("today"))

    if not price_df_full_year.empty:
        # --- KPI Section ---
        st.subheader("Key Performance Indicators")

        # Latest Price KPI
        latest_price = price_df_full_year['Close'].iloc[-1]
        previous_day_price = price_df_full_year['Close'].iloc[-2] if len(price_df_full_year) > 1 else latest_price
        render_kpi_chart(latest_price, previous_day_price, price_df_full_year.tail(30), "Latest Price (vs yesterday)")


        # Percentage Change KPIs
        change_period = st.radio(
            "Select Period for Percentage Change",
            ('Weekly', 'Monthly', 'Yearly'),
            horizontal=True
        )

        latest_price_for_change = price_df_full_year["Close"].iloc[-1]

        comparison_price = None
        if change_period == 'Weekly':
            comparison_date = datetime.now() - timedelta(weeks=1)
            period_label = "Weekly"
            history_for_kpi = price_df_full_year.tail(7)
        elif change_period == 'Monthly':
            comparison_date = datetime.now() - timedelta(days=30)
            period_label = "Monthly"
            history_for_kpi = price_df_full_year.tail(30)
        else:  # Yearly
            comparison_price = price_df_full_year["Close"].iloc[0]
            period_label = "Yearly"
            history_for_kpi = price_df_full_year

        if change_period != 'Yearly':
            # Find the closest available date in the history
            comparison_price_series = price_df_full_year.iloc[price_df_full_year.index.get_indexer([comparison_date], method='nearest')]
            if not comparison_price_series.empty:
                comparison_price = comparison_price_series["Close"].iloc[0]

        if comparison_price is not None:
            render_kpi_chart(latest_price_for_change, comparison_price, history_for_kpi, f"{period_label} Change")
        else:
            st.warning(f"Could not calculate {period_label} percentage change.")


    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        aggregation = st.selectbox("Aggregation", ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'], key="price_agg")
    with c2:
        chart_type = st.radio("Chart Type", ['Candlestick', 'Line'], key="price_chart_type")
    with c3:
        if chart_type == 'Line':
            line_metric = st.selectbox("Metric for Line Chart", ['Open', 'High', 'Low', 'Close'], index=3, key="price_line_metric").lower()
        else:
            line_metric = 'close' # Default for candlestick

    # --- DATA PROCESSING FOR CHART---
    price_df = price_df_full_year[(price_df_full_year.index.date >= start_date_input.date()) & (price_df_full_year.index.date <= end_date_input.date())]


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

        # --- AGGREGATION LOGIC ---
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

        # --- X-AXIS FORMATTING ---
        if aggregation == 'Yearly':
            price_df['Label'] = price_df['date'].dt.strftime('%Y')
            x_title = 'Year'
        elif aggregation == 'Quarterly':
            price_df['Label'] = price_df['date'].dt.to_period('Q').astype(str)
            x_title = 'Quarter'
        elif aggregation == 'Monthly':
            price_df['Label'] = price_df['date'].dt.strftime('%b %Y')
            x_title = 'Month'
        else: # Weekly or Daily
            price_df['Label'] = price_df['date'].dt.strftime('%Y-%m-%d')
            x_title = 'Date'
        
        x_axis = alt.X('Label:O', title=x_title, sort=None)

        # --- Y-AXIS SCALE ---
        # Calculate min/max for a tight y-axis domain
        min_val = price_df['low'].min()
        max_val = price_df['high'].max()
        padding = (max_val - min_val) * 0.05 # Add 5% padding
        y_domain = [min_val - padding, max_val + padding]
        y_scale = alt.Scale(domain=y_domain, zero=False)

        # --- CHARTING ---
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
