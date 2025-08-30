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

    # Layout: filters at left within the page
    filter_col, content_col = st.columns([1, 4], gap="large")

    with filter_col:
        st.subheader("Filters")

        # --- Company search & selection --- #
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
        st.session_state.selected_ticker = selected_ticker # Update session state

        # Statement / metric category filter
        categories_available = sorted(df[df["Ticker"] == selected_ticker]["Category"].unique())
        stmt_selected = st.selectbox("Metric Category", categories_available, key="stmt_cat")

    # safe category fetch
    sel_cat = df[df["Ticker"] == selected_ticker]["Category"].iloc[0] if "Category" in df.columns else "N/A"

    with content_col:
        ticker_df = df[(df["Ticker"] == selected_ticker) & (df["Category"] == stmt_selected)]
        st.session_state.ticker_df = ticker_df

        wide = ticker_df.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
        if wide.empty:
            st.warning("No data available for this ticker.")
            st.stop()

        # ---------- Company Header ---------- #
        st.markdown("<div class='sticky-header-container'>", unsafe_allow_html=True)
        tinfo = ticker_info(selected_ticker)
        logo_path = _get_logo_path(selected_ticker)
        
        hcols = st.columns([1,3])
        with hcols[0]:
            if logo_path:
                st.image(logo_path)
        with hcols[1]:
            st.markdown("<div class='company-info-wrapper'>", unsafe_allow_html=True)
            st.markdown(f"## {selected_ticker} – {tinfo['name']}")
            st.caption(f"Sector: {tinfo['sector']} • Industry: {tinfo['industry']}")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Compute universe of metrics for the selected ticker
        all_metrics = sorted(ticker_df["Metric"].unique())

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
        
        st.markdown("---") # Add a separator

        # Render content based on active tab
        if st.session_state.active_tab == "Metrics Trend Analysis":
            trend_tab.render(ticker_df, all_metrics)
        elif st.session_state.active_tab == "Snapshot & Changes":
            snapshot_tab.render(ticker_df, all_metrics)
        elif st.session_state.active_tab == "Earning Summary":
            earnings_tab.render(selected_ticker)
        elif st.session_state.active_tab == "Price Chart":
            price_tab.render(selected_ticker)
        elif st.session_state.active_tab == "Macroeconomic Data":
            fred_tab.render()
        elif st.session_state.active_tab == "FinQ 360":
            finq_360_tab.render(ticker_df, selected_ticker)
        elif st.session_state.active_tab == "FinQ Bot":
            chatbot_tab.render()
