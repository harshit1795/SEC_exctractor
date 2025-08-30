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

    # ---------- Company Header ---------- #
    tinfo = ticker_info(st.session_state.get("selected_ticker", "AAPL"))
    logo_path = _get_logo_path(st.session_state.get("selected_ticker", "AAPL"))
    
    _, col2 = st.columns([2, 3])
    with col2:
        l, r = st.columns([1, 3])
        with l:
            if logo_path:
                st.image(logo_path, width=100)
        with r:
            st.markdown(f"<div style='text-align: right;'><h2>{st.session_state.get('selected_ticker', 'AAPL')} – {tinfo['name']}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: right;'>{tinfo['sector']} • {tinfo['industry']}</div>", unsafe_allow_html=True)

    # ------------------------- Tabs ------------------------- #
    tab_options = {
        "Metrics Trend Analysis": "fa-chart-line",
        "Snapshot & Changes": "fa-camera",
        "Earning Summary": "fa-file-invoice-dollar",
        "Price Chart": "fa-chart-area",
        "Macroeconomic Data": "fa-globe",
        "FinQ 360": "fa-magnifying-glass-chart",
        "FinQ Bot": "fa-robot"
    }

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

    # --- Main Content Area with Chart and Filters ---
    chart_col, filter_col = st.columns([3, 1], gap="large")

    with filter_col:
        with st.expander("Filters", expanded=True):
            st.markdown("#### Global Filters")
            search_text = st.text_input("Search company or ticker", "", key="search_company")
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
            selected_ticker = st.selectbox("Company (Ticker)", filtered_tickers, index=default_ix, key="ticker_select")
            st.session_state.selected_ticker = selected_ticker

            categories_available = sorted(df[df["Ticker"] == selected_ticker]["Category"].unique())
            stmt_selected = st.selectbox("Metric Category", categories_available, key="stmt_cat")
            st.session_state.stmt_selected = stmt_selected

            st.markdown("#### Tab-Specific Options")
            active_tab = st.session_state.get('active_tab', "Metrics Trend Analysis")
            filters = {}

            ticker_df = df[(df["Ticker"] == selected_ticker) & (df["Category"] == stmt_selected)]
            all_metrics = sorted(ticker_df["Metric"].unique())

            if active_tab == "Metrics Trend Analysis":
                filters = trend_tab.render_filters(all_metrics)
            elif active_tab == "Snapshot & Changes":
                wide_df_for_filters = ticker_df.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
                if not wide_df_for_filters.empty:
                    filters = snapshot_tab.render_filters(all_metrics, wide_df_for_filters)
            elif active_tab == "Price Chart":
                filters = price_tab.render_filters()
            elif active_tab == "Earning Summary":
                earnings_dates, _ = earnings_tab.get_ticker_earnings_data(selected_ticker)
                if earnings_dates is not None and not earnings_dates.empty:
                    earnings_dates_df = earnings_dates.reset_index().rename(columns={'Earnings Date': 'Date'})
                    filters = earnings_tab.render_filters(earnings_dates_df)
            elif active_tab == "Macroeconomic Data":
                filters = fred_tab.render_filters()
            elif active_tab == "FinQ 360":
                filters = finq_360_tab.render_filters(ticker_df, selected_ticker)
            elif active_tab == "FinQ Bot":
                if 'chatbot_interface' not in st.session_state:
                    st.session_state.chatbot_interface = chatbot_tab.ChatbotInterface()
                st.session_state.chatbot_interface.render_filters()

    with chart_col:
        ticker_df = df[(df["Ticker"] == st.session_state.selected_ticker) & (df["Category"] == st.session_state.stmt_selected)]
        wide = ticker_df.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
        all_metrics = sorted(ticker_df["Metric"].unique())

        if wide.empty:
            st.warning("No data available for this ticker.")
            st.stop()

        if st.session_state.active_tab == "Metrics Trend Analysis":
            trend_tab.render(ticker_df, all_metrics, filters)
        elif st.session_state.active_tab == "Snapshot & Changes":
            if filters:
                snapshot_tab.render(ticker_df, all_metrics, filters)
        elif st.session_state.active_tab == "Earning Summary":
            if filters:
                earnings_tab.render(selected_ticker, filters)
        elif st.session_state.active_tab == "Price Chart":
            price_tab.render(selected_ticker, filters)
        elif st.session_state.active_tab == "Macroeconomic Data":
            fred_tab.render(filters)
        elif st.session_state.active_tab == "FinQ 360":
            finq_360_tab.render(ticker_df, selected_ticker, filters)
        elif st.session_state.active_tab == "FinQ Bot":
            st.session_state.chatbot_interface.render_content()
