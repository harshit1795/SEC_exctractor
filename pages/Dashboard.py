import pandas as pd
import streamlit as st
import os
from functools import lru_cache

from auth import load_api_keys
from pages.dashboard_tabs import trend_tab, snapshot_tab, earnings_tab, price_tab, fred_tab, chatbot_tab, finq_360_tab

def render():
    load_api_keys()

    st.markdown("<h2 style='text-align: center;'> Dashboard</h2>", unsafe_allow_html=True)

    PARQUET_PATH = "fundamentals_tall.parquet"

    @st.cache_data(show_spinner=False)
    def _load_meta_csv(path: str = "sp500_fundamentals.csv") -> dict:
        """Load pre-scraped ticker metadata (name, sector, industry) into a dict."""
        if os.path.exists(path):
            meta_df = pd.read_csv(path)[["Ticker", "Name", "Sector", "Industry"]]
            return meta_df.set_index("Ticker").to_dict("index")
        return {}

    _TICKER_META = _load_meta_csv()

    @st.cache_data(show_spinner=True)
    def load_data(path: str = PARQUET_PATH) -> pd.DataFrame:
        return pd.read_parquet(path)

    with st.spinner("Loading fundamentals data…"):
        df = load_data()

    @lru_cache(maxsize=1024)
    def ticker_info(ticker: str) -> dict:
        """Lightweight metadata lookup that avoids network calls for bulk operations."""
        meta = _TICKER_META.get(ticker, {})
        return {
            "name": meta.get("Name") or ticker,
            "sector": meta.get("Sector", "N/A"),
            "industry": meta.get("Industry", "N/A"),
        }

    @st.cache_data(show_spinner=False)
    def _get_logo_path(ticker: str) -> str | None:
        """Return URL to company logo from Parqet assets."""
        return f"https://assets.parqet.com/logos/symbol/{ticker}?format=png"

    tab_options = {
        "Metrics Trend Analysis": "fa-chart-line",
        "Snapshot & Changes": "fa-camera",
        "Earning Summary": "fa-file-invoice-dollar",
        "Price Chart": "fa-chart-area",
        "Macroeconomic Data": "fa-globe",
        "FinQ 360": "fa-magnifying-glass-chart",
        "FinQ Bot": "fa-robot"
    }

    # --- Global Filters --- #
    search_text = st.text_input("Search company or ticker", "", key="search_company_global")
    all_tickers = sorted(df["Ticker"].unique())

    def matches(term: str, ticker: str) -> bool:
        meta = ticker_info(ticker)
        name = meta["name"].lower() if meta else ""
        return term in ticker.lower() or term in name

    if search_text:
        term = search_text.lower()
        filtered_tickers = [t for t in all_tickers if matches(term, t)]
    else:
        filtered_tickers = all_tickers

    if not filtered_tickers:
        st.warning("No company matches search.")
        st.stop()

    default_ix = filtered_tickers.index("AAPL") if "AAPL" in filtered_tickers else 0
    selected_ticker = st.selectbox("Company (Ticker)", filtered_tickers, index=default_ix, key="ticker_select_global")
    st.session_state.selected_ticker = selected_ticker

    categories_available = sorted(df[df["Ticker"] == selected_ticker]["Category"].unique())
    stmt_selected = st.selectbox("Metric Category", categories_available, key="stmt_cat_global")
    
    ticker_df = df[(df["Ticker"] == selected_ticker) & (df["Category"] == stmt_selected)]
    st.session_state.ticker_df = ticker_df
    all_metrics = sorted(ticker_df["Metric"].unique())

    # --- Layout --- #
    content_col, sidebar_col = st.columns([3, 1])

    with sidebar_col:
        with st.expander("Tab-Specific Filters", expanded=True):
            tab_filters = {}
            active_tab_name = st.session_state.get('active_tab', list(tab_options.keys())[0])

            if active_tab_name == "Metrics Trend Analysis":
                tab_filters = trend_tab.render_filters(all_metrics)
            elif active_tab_name == "Snapshot & Changes":
                tab_filters = snapshot_tab.render_filters(ticker_df, all_metrics)
            elif active_tab_name == "Earning Summary":
                tab_filters = earnings_tab.render_filters(selected_ticker)
            elif active_tab_name == "Price Chart":
                tab_filters = price_tab.render_filters()
            elif active_tab_name == "Macroeconomic Data":
                tab_filters = fred_tab.render_filters()
            elif active_tab_name == "FinQ 360":
                tab_filters = finq_360_tab.render_filters(ticker_df, selected_ticker)
            elif active_tab_name == "FinQ Bot":
                tab_filters = chatbot_tab.render_filters(all_tickers)

    with content_col:
        wide = ticker_df.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
        if wide.empty:
            st.warning("No data available for this ticker.")
            st.stop()

        tinfo = ticker_info(selected_ticker)
        logo_path = _get_logo_path(selected_ticker)
        
        hcols = st.columns([1,3])
        with hcols[0]:
            if logo_path:
                st.image(logo_path)
        with hcols[1]:
            st.markdown(f"## {selected_ticker} – {tinfo['name']}")
            st.caption(f"Sector: {tinfo['sector']} • Industry: {tinfo['industry']}")

        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = list(tab_options.keys())[0]

        cols = st.columns(len(tab_options))
        for i, (tab_name, icon) in enumerate(tab_options.items()):
            with cols[i]:
                is_active = (tab_name == st.session_state.active_tab)
                st.markdown(f'<div style="text-align: center;"><i class="fa-solid {icon}"></i></div>', unsafe_allow_html=True)
                if st.button(tab_name, key=f"tab_{i}", type="primary" if is_active else "secondary", use_container_width=True):
                    st.session_state.active_tab = tab_name
                    st.rerun()
        
        st.markdown("---")

        active_tab_name = st.session_state.active_tab
        if active_tab_name == "Metrics Trend Analysis":
            trend_tab.render_content(ticker_df, tab_filters)
        elif active_tab_name == "Snapshot & Changes":
            snapshot_tab.render_content(ticker_df, tab_filters)
        elif active_tab_name == "Earning Summary":
            earnings_tab.render_content(selected_ticker, tab_filters)
        elif active_tab_name == "Price Chart":
            price_tab.render_content(selected_ticker, tab_filters)
        elif active_tab_name == "Macroeconomic Data":
            fred_tab.render_content(tab_filters)
        elif active_tab_name == "FinQ 360":
            finq_360_tab.render_content(ticker_df, selected_ticker, tab_filters)
        elif active_tab_name == "FinQ Bot":
            chatbot_tab.render_content()
