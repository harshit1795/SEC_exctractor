import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf
from functools import lru_cache
import numpy as np
import google.generativeai as genai
import os
from fred_data import get_multiple_fred_series
from auth import show_login_ui, _load_user_prefs, _save_user_prefs, load_api_keys


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

if not st.session_state.get("logged_in", False):
    show_login_ui()
else:
    load_api_keys()
    st.sidebar.success("You are logged in.")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.experimental_rerun()
    # Main content of the page starts here


# Load data
df = pd.read_parquet("fundamentals_tall.parquet")
_TICKER_META = pd.read_csv("sp500_fundamentals.csv")[["Ticker", "Name", "Sector", "Industry"]].set_index("Ticker").to_dict("index")

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

@st.cache_data(show_spinner=False)
def get_ticker_earnings_data(ticker_symbol):
    ticker_yf = yf.Ticker(ticker_symbol)
    return ticker_yf.earnings_dates, ticker_yf.info

@st.cache_data(show_spinner=True)
def get_price_history(ticker: str, start_date, end_date) -> pd.DataFrame:
    """Get historical price data from yfinance."""
    return yf.download(ticker, start=start_date, end=end_date)

st.markdown("<h2 style='text-align: center;'>📊 Dashboard</h2>", unsafe_allow_html=True)

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
    latest_period = wide.index.max()
    latest_vals = wide.loc[latest_period]

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
    trend_tab, snapshot_tab, earnings_tab, price_tab, fred_tab, chatbot_tab = st.tabs(["📈 Metrics Trend Analysis", "📊 Snapshot & Changes", "💰 Earning Summary", "💹 Price Chart", "📉 Macroeconomic Data", "🤖 FinQ Bot"])

    # ------------------------- Chatbot Tab ------------------------- #
    with chatbot_tab:
        st.markdown("### FinQ Bot")

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("What is your question?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate response from Gemini API
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')

                # System instruction for the financial analyst AI
                system_instruction = """You are a highly skilled financial analyst AI. Your primary goal is to provide insightful and accurate financial analysis based on the provided data.
You should:
- Analyze trends and patterns.
- Identify key financial metrics and their implications.
- Highlight potential risks or opportunities.
- Answer questions directly related to the financial data provided.
- If a question cannot be answered from the provided data, state that clearly.
- Do not make up information or provide analysis beyond the scope of the given data.
- Present your analysis in a clear, concise, and professional manner.
- Use consistent financial currency notations (e.g., $1.2B, $500M, $25M) instead of scientific notation for all monetary values.-
"""
                
                # Get the financial data from session state
                current_ticker_df = st.session_state.get("ticker_df")
                if current_ticker_df is not None and not current_ticker_df.empty:
                    financial_data_str = current_ticker_df.to_markdown(index=False)
                else:
                    financial_data_str = "No specific financial data available for analysis in the current context."

                # Construct the full prompt
                full_prompt = f"""{system_instruction}

Here is the financial data for the selected company and category:
{financial_data_str}

User's question: {prompt}
"""
                response = model.generate_content(full_prompt)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # ------------------------- Trend Analysis ------------------------- #
    with trend_tab:
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

        # Save preference button (placed right below selector)
        if st.button("💾 Save these as my default metrics", key="save_trend_btn"):
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
            line = base.mark_line(point=True)
            text = base.mark_text(dy=-10, align="left").encode(text="Label")
            chart = alt.layer(line, text).properties(height=300, width=900, title=metric)
            st.altair_chart(chart, use_container_width=True)

    # ------------------------- Snapshot & Changes ------------------------- #
    with snapshot_tab:
        st.markdown("### Snapshot & Changes")
        mode = st.radio(f"Display (Period: {latest_period})", ["Latest", "QoQ Δ", "YoY Δ"], horizontal=True)

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
        saved_snap = user_defaults.get("snapshot_metrics", [])
        default_snapshot = [m for m in saved_snap if m in all_metrics] or [m for m in important_mets if m in all_metrics]
        snap_metrics = st.multiselect("Metrics to show", all_metrics, default=default_snapshot or all_metrics[:10], key="snap_met")

        wide = ticker_df.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
        if wide.empty:
            st.warning("No data available for this ticker.")
            st.stop()
        latest_period = wide.index.max()
        latest_vals = wide.loc[latest_period]

        # Determine deltas
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

        # Display metrics in a responsive grid
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

        # Save snapshot prefs
        if st.button("💾 Save these as my default snapshot metrics", key="save_snap_btn"):
            all_prefs = _load_user_prefs()
            user = st.session_state.get("user")
            if user:
                all_prefs.setdefault(user, {})["snapshot_metrics"] = snap_metrics
                _save_user_prefs(all_prefs)
                st.session_state.user_prefs = all_prefs[user]
                st.success("Snapshot preferences saved!")

    # ------------------------- Earning Summary ------------------------- #
    with earnings_tab:
        st.markdown("### Earning Summary")

        earnings_dates, ticker_info_yf = get_ticker_earnings_data(selected_ticker)

        if not earnings_dates.empty:
            # Last Quarter's Earnings
            st.subheader("Last Quarter's Earnings")
            # Ensure the index is a datetime object for comparison
            earnings_dates.index = pd.to_datetime(earnings_dates.index)
            
            # Get the most recent past earnings date
            past_earnings = earnings_dates[
                (earnings_dates.index < pd.Timestamp.now(tz='America/New_York')) &
                (earnings_dates['Event Type'] == 'Earnings') &
                (earnings_dates['Reported EPS'].notna())
            ].sort_index(ascending=False)
            
            if not past_earnings.empty:
                last_earnings = past_earnings.iloc[0]
                st.write(f"**Date:** {last_earnings.name.strftime('%Y-%m-%d')}")
                st.write(f"**Reported EPS:** {last_earnings.get('Reported EPS', 'N/A')}")
                st.write(f"**Estimated EPS:** {last_earnings.get('EPS Estimate', 'N/A')}")
                st.write(f"**Surprise (%):** {last_earnings.get('Surprise(%)', 'N/A')}")
            else:
                st.info("No past earnings data available.")

            # Next Earnings Prediction (from yfinance)
            # This section is now integrated with the simple prediction model below
            # so we remove the redundant subheader here.
            # st.subheader("Next Earnings Prediction")
            # Find the next earnings date that is in the future and is an 'Earnings' event
            next_earnings = earnings_dates[
                (earnings_dates.index > pd.Timestamp.now(tz='America/New_York')) &
                (earnings_dates['Event Type'] == 'Earnings') &
                (earnings_dates['EPS Estimate'].notna())
            ].sort_index()

            if not next_earnings.empty:
                next_earnings = next_earnings.iloc[0]
                st.write(f"**Next Earnings Date:** {next_earnings.name.strftime('%Y-%m-%d')}")
                st.write(f"**Estimated EPS:** {next_earnings.get('EPS Estimate', 'N/A')}")
                # You can add more predictions if available in ticker_info_yf
                if ticker_info_yf and 'earningsHigh' in ticker_info_yf:
                    st.write(f"**High Estimate:** {ticker_info_yf['earningsHigh']}")
                if ticker_info_yf and 'earningsLow' in ticker_info_yf:
                    st.write(f"**Low Estimate:** {ticker_info_yf['earningsLow']}")
                if ticker_info_yf and 'earningsAvg' in ticker_info_yf:
                    st.write(f"**Average Estimate:** {ticker_info_yf['earningsAvg']}")

        st.subheader("Historical EPS Trend")
        # Filter for earnings events and valid EPS data
        historical_eps_df = earnings_dates[
            (earnings_dates['Event Type'] == 'Earnings') &
            (earnings_dates['Reported EPS'].notna()) &
            (earnings_dates['EPS Estimate'].notna())
        ].reset_index().rename(columns={'Earnings Date': 'Date'})

        if not historical_eps_df.empty:
            # Melt the DataFrame for Altair
            melted_eps_df = historical_eps_df.melt(
                id_vars=['Date'], 
                value_vars=['Reported EPS', 'EPS Estimate'], 
                var_name='EPS Type', 
                value_name='EPS Value'
            )

            chart = alt.Chart(melted_eps_df).mark_line(point=True).encode(
                x=alt.X('Date', type='temporal', title='Earnings Date', axis=alt.Axis(format='%b %Y', labelAngle=-90)),
                y=alt.Y('EPS Value', title='EPS'),
                color='EPS Type',
                tooltip=[
                    alt.Tooltip('Date', title='Period'),
                    alt.Tooltip('EPS Type', title='Type'),
                    alt.Tooltip('EPS Value', title='EPS')
                ]
            ).properties(
                title=f'{selected_ticker} Historical EPS Trend'
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No sufficient historical EPS data available for charting.")

        # --- Simple EPS Prediction Model --- #
        st.subheader("Next Earning Prediction")
        
        # Get reported EPS data for prediction
        reported_eps_data = earnings_dates[
            (earnings_dates['Event Type'] == 'Earnings') &
            (earnings_dates['Reported EPS'].notna())
        ].sort_index(ascending=False) # Sort to get most recent first

        if not reported_eps_data.empty and len(reported_eps_data) >= 4: # Need at least 4 quarters for a basic trend
            # Take the last 4 reported EPS values
            eps_values = reported_eps_data['Reported EPS'].head(4).values
            
            predicted_eps = np.mean(eps_values)
            st.write(f"**Predicted EPS for Next Quarter:** {predicted_eps:.2f}")
            st.caption("Prediction based on the average of the last 4 reported EPS values.")
        else:
            st.info("Not enough historical data to make a prediction (need at least 4 reported EPS values).")

    # ------------------------- Macroeconomic Data Tab ------------------------- #
    with fred_tab:
        st.markdown("### Macroeconomic Data")

        INDICATORS = {
            "GDP": "GDP",
            "Real GDP": "GDPC1",
            "Inflation (CPI)": "CPIAUCSL",
            "Unemployment Rate": "UNRATE",
            "10-Year Treasury Yield": "DGS10",
            "Federal Funds Rate": "FEDFUNDS",
        }

        selected_indicators = st.multiselect(
            "Select economic indicators to display:",
            options=list(INDICATORS.keys()),
            default=["Real GDP", "Inflation (CPI)", "Unemployment Rate"]
        )

        if selected_indicators:
            series_to_fetch = [INDICATORS[key] for key in selected_indicators]
            
            today = pd.to_datetime("today")
            start = st.date_input("Start date", today - pd.DateOffset(years=10), key="fred_start")
            end = st.date_input("End date", today, key="fred_end")

            if st.button("Fetch FRED Data"):
                fred_df = get_multiple_fred_series(series_to_fetch, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
                
                if not fred_df.empty:
                    st.subheader("Data Preview")
                    st.dataframe(fred_df.head())

                    st.subheader("Charts")
                    for col in fred_df.columns:
                        st.line_chart(fred_df[col].dropna(), use_container_width=True)
                        st.markdown(f"**{col}** - {selected_indicators[series_to_fetch.index(col)]}")
                else:
                    st.warning("No data returned. Please check the series IDs and date range.")

    # ------------------------- Price Chart Tab ------------------------- #
    with price_tab:
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
