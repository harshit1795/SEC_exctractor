
import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf

@st.cache_data(show_spinner=True)
def get_price_history(ticker: str, start_date, end_date) -> pd.DataFrame:
    """Get historical price data from yfinance."""
    return yf.download(ticker, start=start_date, end=end_date)

def render(selected_ticker):
    st.markdown("### Price Chart")

    # Date range selection
    today = pd.to_datetime("today")
    start_date = st.date_input("Start date", today - pd.DateOffset(years=1), key="price_start")
    end_date = st.date_input("End date", today, key="price_end")

    # Fetch price data
    price_df = get_price_history(selected_ticker, start_date, end_date)

    if not price_df.empty:
        price_df = price_df.reset_index()
        if isinstance(price_df.columns, pd.MultiIndex):
            price_df.columns = price_df.columns.get_level_values(1)
        price_df.columns = [str(col).lower() for col in price_df.columns] # Standardize column names
        if 'date' in price_df.columns:
            price_df['date'] = pd.to_datetime(price_df['date'])

            # Candlestick chart
            base = alt.Chart(price_df).encode(
                x='date:T',
                color=alt.condition("datum.open <= datum.close", alt.value("#06982d"), alt.value("#ae1325")),
                tooltip=['date', 'open', 'high', 'low', 'close', 'volume']
            )

            chart = alt.layer(
                base.mark_rule().encode(
                    y='low:Q',
                    y2='high:Q'
                ),
                base.mark_bar().encode(
                    y='open:Q',
                    y2='close:Q'
                )
            ).interactive()

            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Date column not found in price data.")
    else:
        st.warning("Could not retrieve price data for the selected ticker and date range.")
