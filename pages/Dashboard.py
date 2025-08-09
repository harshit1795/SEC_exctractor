import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf
from functools import lru_cache
import numpy as np
import google.generativeai as genai
import os
from fred_data import get_multiple_fred_series
from auth import load_api_keys

def render():
    load_api_keys()

    @st.cache_data
    def load_fundamentals_data():
        """Loads the core financial data from a Parquet file."""
        return pd.read_parquet("fundamentals_tall.parquet")

    @st.cache_data
    def load_ticker_metadata():
        """Loads ticker metadata from a CSV file."""
        return pd.read_csv("sp500_fundamentals.csv")[["Ticker", "Name", "Sector", "Industry"]].set_index("Ticker").to_dict("index")

    df = load_fundamentals_data()
    _TICKER_META = load_ticker_metadata()

    def human_format(num):
        if num is None or pd.isna(num):
            return "N/A"
        sign = "-" if num < 0 else ""
        num = abs(num)
        for unit in ["", "K", "M", "B", "T"]:
            if num < 1000:
                return f"{sign}${num:,.1f}{unit}" if unit else f"{sign}${num:,.0f}"
            num /= 1000
        return f"{sign}${num:.1f}P"

    def human_format_for_axis(num):
        if num is None or pd.isna(num):
            return num, ""
        num = float(num)
        if abs(num) >= 1_000_000_000:
            return num / 1_000_000_000, "B"
        if abs(num) >= 1_000_000:
            return num / 1_000_000, "M"
        if abs(num) >= 1_000:
            return num / 1_000, "K"
        return num, ""

    @lru_cache(maxsize=1024)
    def ticker_info(ticker: str) -> dict:
        return _TICKER_META.get(ticker, {})

    @st.cache_data(show_spinner=False)
    def get_logo_path(ticker: str) -> str | None:
        return f"assets/logos/{ticker}.png"

    @st.cache_data(show_spinner=False)
    def get_ticker_earnings_data(ticker_symbol):
        ticker_yf = yf.Ticker(ticker_symbol)
        return ticker_yf.earnings_dates, ticker_yf.info

    @st.cache_data(show_spinner=True)
    def get_price_history(ticker: str, start_date, end_date) -> pd.DataFrame:
        return yf.download(ticker, start=start_date, end=end_date)

    st.markdown("<h2 style='text-align: center;'>📊 Dashboard</h2>", unsafe_allow_html=True)

    filter_col, content_col = st.columns([1, 4], gap="large")

    with filter_col:
        st.subheader("Filters")
        search_text = st.text_input("Search company or ticker", "", key="search_company")
        all_tickers = sorted(df["Ticker"].unique())

        def matches(term: str, ticker: str) -> bool:
            meta = ticker_info(ticker)
            name = meta.get("Name", "").lower()
            return term.lower() in ticker.lower() or term.lower() in name

        filtered_tickers = [t for t in all_tickers if matches(search_text, t)] if search_text else all_tickers

        if not filtered_tickers:
            st.warning("No company matches search.")
            st.stop()

        default_ix = filtered_tickers.index("AAPL") if "AAPL" in filtered_tickers else 0
        selected_ticker = st.selectbox("Company (Ticker)", filtered_tickers, index=default_ix, key="ticker_select")
        st.session_state.selected_ticker = selected_ticker

        categories_available = sorted(df[df["Ticker"] == selected_ticker]["Category"].unique())
        stmt_selected = st.selectbox("Metric Category", categories_available, key="stmt_cat")

    with content_col:
        ticker_df = df[(df["Ticker"] == selected_ticker) & (df["Category"] == stmt_selected)]
        st.session_state.ticker_df = ticker_df

        if ticker_df.empty:
            st.warning("No data available for this ticker and category.")
            st.stop()

        tinfo = ticker_info(selected_ticker)
        logo_path = get_logo_path(selected_ticker)
        
        hcols = st.columns([1, 3])
        with hcols[0]:
            if os.path.exists(logo_path):
                st.image(logo_path)
        with hcols[1]:
            st.markdown(f"## {selected_ticker} – {tinfo.get('Name', '')}")
            st.caption(f"Sector: {tinfo.get('Sector', 'N/A')} • Industry: {tinfo.get('Industry', 'N/A')}")

        trend_tab, snapshot_tab, earnings_tab, price_tab, fred_tab, chatbot_tab = st.tabs(
            ["📈 Metrics Trend Analysis", "📊 Snapshot & Changes", "💰 Earning Summary", "💹 Price Chart", "📉 Macroeconomic Data", "🤖 FinQ Bot"]
        )