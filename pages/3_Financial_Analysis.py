
import pandas as pd
import streamlit as st
import altair as alt
import yfinance as yf
from functools import lru_cache
import numpy as np
import google.generativeai as genai
import os
import requests
import json
from fred_data import get_multiple_fred_series

# Configure the Gemini API key
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except Exception as e:
    st.error("Please set the GEMINI_API_KEY environment variable.")
    st.stop()

st.set_page_config(page_title="FinQ Bot", layout="wide")

st.markdown("""
<style>
.sticky-header-container {
    position: sticky;
    top: 0;
    background-color: white; /* Adjust to your app's background color */
    z-index: 999; /* Ensure it stays on top */
    padding-top: 1rem; /* Adjust as needed */
    padding-bottom: 1rem; /* Adjust as needed */
    border-bottom: 1px solid #eee; /* Optional: a subtle line */
    display: flex; /* Enable flexbox */
    align-items: center; /* Vertically center items */
}
.company-info-wrapper {
    display: flex;
    flex-direction: column;
    justify-content: center; /* Vertically center content within the wrapper */
    height: 100%; /* Ensure it takes full height of the column */
}
</style>
""", unsafe_allow_html=True)

# Initialize selected_ticker in session state if not already present
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "AAPL" # Default value

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

# ------------------------- Helpers ------------------------- #

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

# ------------------------- Authentication ------------------------- #

# In-memory users store (you can replace with DB later)
if "users" not in st.session_state:
    st.session_state.users = {"welcome": "finq"}

# default auth flag
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ------------------------- User Preferences ------------------------- #

PREFS_PATH = "user_prefs.json"

def _load_user_prefs() -> dict:
    """Load all users' saved metric preferences from disk."""
    if os.path.exists(PREFS_PATH):
        try:
            with open(PREFS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_user_prefs(pref_dict: dict):
    """Persist full preferences dict to disk."""
    try:
        with open(PREFS_PATH, "w") as f:
            json.dump(pref_dict, f, indent=2)
    except Exception:
        pass

# ------------------------- Nexus Community Data Helpers ------------------------- #

NEXUS_PATH = "nexus_store.json"

def _load_nexus() -> dict:
    """Load Nexus community store from disk, validating user profiles and messages."""
    if os.path.exists(NEXUS_PATH):
        try:
            with open(NEXUS_PATH, "r") as f:
                data = json.load(f)
                # Validate each user's profile to ensure it's a dictionary
                for user_key, profile in data.items():
                    if user_key != "_messages" and not isinstance(profile, dict):
                        data[user_key] = {
                            "friends": [],
                            "followers": [],
                            "following": [],
                            "requests": [],
                            "posts": []
                        }
                # Validate messages
                if "_messages" in data and isinstance(data["_messages"], list):
                    data["_messages"] = [m for m in data["_messages"] if isinstance(m, dict) and "from" in m and "to" in m and "text" in m]
                else:
                    data["_messages"] = []
                return data
        except Exception:
            return {}
    return {}


def _save_nexus(data: dict):
    """Persist Nexus store to disk."""
    try:
        with open(NEXUS_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def login_page():
    st.markdown("## 🔐 FinQ Bot Login")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.authenticated = True
                st.session_state.user = username
                # Load or initialize user preferences
                all_prefs = _load_user_prefs()
                st.session_state.user_prefs = all_prefs.get(username, {})

                # Ensure nexus profile exists
                nx = _load_nexus()
                if username not in nx:
                    nx[username] = {
                        "friends": [],
                        "followers": [],
                        "following": [],
                        "requests": [],  # incoming friend requests
                        "posts": []      # list of {"content": str, "comments": [{"user":..., "text":...}]}
                    }
                    _save_nexus(nx)
                st.session_state.nexus = nx
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            if new_user in st.session_state.users:
                st.error("Username already exists")
            elif new_user and new_pass:
                st.session_state.users[new_user] = new_pass
                st.success("Registration successful. Please login.")

# Check authentication
if not st.session_state.get("authenticated", False):
    login_page()
    st.stop()

# ------------------------- Main App ------------------------- #

# Display application logo
st.markdown("<style> .css-1d3f8as { display: flex; flex-direction: column; align-items: center; } </style>", unsafe_allow_html=True)


# Display company logo in sidebar
selected_ticker_for_sidebar = st.session_state.get("selected_ticker", "AAPL")
st.sidebar.markdown(f"**{selected_ticker_for_sidebar}**") # Display ticker if no logo

# ------------------------- Page Navigation ------------------------- #

st.markdown("<style>div.stRadio > label { text-align: center; }</style>", unsafe_allow_html=True)

# ------------------------- Page Navigation ------------------------- #

page = st.sidebar.radio("Navigate", ["Dashboard", "Financial Health Monitoring", "Nexus"], key="main_nav")




# Add a logout button to the sidebar
if st.sidebar.button("Log Out"):
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["user_prefs"] = {}
    st.session_state["nexus"] = {}
    st.rerun()

# ------------------------- Welcome Page ------------------------- #

if page == "Welcome":
    st.markdown("## 👋 Welcome to FinQ Bot")
    user = st.session_state.get("current_user", "Guest")
    st.write(f"Hello, **{user}**! Use the navigation menu on the left to explore the dashboard or check financial health rankings.")
    st.stop()

# ------------------------- Dashboard Page ------------------------- #

if page == "Dashboard":
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

# ------------------------- Financial Health Monitoring Page ------------------------- #

if page == "Financial Health Monitoring":
    st.markdown("<h2 style='text-align: center;'>🩺 Financial Health Monitoring</h2>", unsafe_allow_html=True)

    # Build sector metadata dynamically (cached)
    @st.cache_data(show_spinner=False)
    def build_meta():
        """Construct ticker → name/sector dataframe using cached metadata (no network)."""
        if _TICKER_META:
            mdf = pd.DataFrame.from_dict(_TICKER_META, orient="index").reset_index()
            mdf = mdf.rename(columns={"index": "Ticker", "Name": "Name", "Sector": "Sector"})
            return mdf
        # Fallback (should be rare): derive from fundamentals table
        return pd.DataFrame({
            "Ticker": df["Ticker"].unique(),
            "Name": df["Ticker"].unique(),
            "Sector": "Unknown",
        })

    meta = build_meta()

    # Map to broader categories
    sector_map = {
        "Information Technology": "Technology",
        "Technology": "Technology",
        "Communication Services": "Technology",
        "Consumer Discretionary": "Manufacturing",
        "Consumer Cyclical": "Manufacturing",
        "Industrials": "Manufacturing",
        "Materials": "Manufacturing",
        "Energy": "Manufacturing",
        "Health Care": "Public Sector",
        "Healthcare": "Public Sector",
        "Utilities": "Public Sector",
        "Real Estate": "Public Sector",
        "Financials": "Finance",
        "Financial Services": "Finance",
        "Consumer Staples": "Finance",
    }

    meta["Category"] = meta["Sector"].map(sector_map).fillna("Other")

    finq_tab, custom_tab = st.tabs(["💡 FinQ Suggestions", "⚙️ Custom Health Score"])

    with finq_tab:
        st.header("FinQ Suggestions")
        st.markdown("**Health Score Formula:** `(Growth_score + NetMargin_score + FCFMargin_score + (1 - DebtEquity_score)) / 4`")
        with st.expander("How are individual metrics scored?"):
            st.markdown("""
            Each metric (Growth, Net Margin, FCF Margin, Debt to Equity) is converted into a score between 0 and 1 
            using percentile ranking. A higher percentile rank indicates a better score.
            
            *   **Growth_score, NetMargin_score, FCFMargin_score:** These are directly the percentile ranks of the respective metrics. 
                For example, a company with a Growth_score of 0.9 means its revenue growth is better than 90% of other companies.
            *   **DebtEquity_score:** This is calculated as `1 - percentile_rank(Debt to Equity)`. This is because a lower Debt to Equity ratio is generally better, 
                so we invert the percentile rank to ensure a higher score indicates better financial health.
            
            The final Health Score is the average of these individual metric scores.
            """)

        # ---------------- Health score computation ---------------- #
        @st.cache_data(show_spinner=True)
        def compute_health_scores() -> pd.DataFrame:
            records = []
            for tkr in df["Ticker"].unique():
                tdf = df[df["Ticker"] == tkr]
                # pivot_table tolerates duplicate FiscalPeriod/Metric combinations
                wide = tdf.pivot_table(index="FiscalPeriod", columns="Metric", values="Value", aggfunc="first").sort_index()
                if wide.empty or wide.shape[0] < 5:
                    continue
                latest = wide.iloc[-1]
                # --- Key metrics --- #
                # Use 'Total Revenue' metric from Yahoo Finance fundamentals
                revenue_col = "Total Revenue" if "Total Revenue" in wide.columns else None
                if revenue_col is None:
                    continue  # skip if revenue not available
                try:
                    rev_latest = latest[revenue_col]
                    rev_prev = wide.iloc[-5][revenue_col]
                except Exception:
                    rev_latest = np.nan
                    rev_prev = np.nan

                growth = (rev_latest - rev_prev) / abs(rev_prev) if pd.notna(rev_latest) and pd.notna(rev_prev) and rev_prev != 0 else np.nan

                try:
                    net_margin = latest.get("Net Income", np.nan) / rev_latest if rev_latest else np.nan
                except Exception:
                    net_margin = np.nan

                try:
                    fcf_margin = latest.get("Free Cash Flow", np.nan) / rev_latest if rev_latest else np.nan
                except Exception:
                    fcf_margin = np.nan

                try:
                    debt_equity = latest["Total Liabilities"] / latest["Shareholder Equity"] if latest["Shareholder Equity"] else np.nan
                except Exception:
                    debt_equity = np.nan

                # --- Build quick insights text --- #
                insight_parts = []
                if pd.notna(growth):
                    insight_parts.append("Revenue " + ("grew" if growth > 0 else "declined") + f" {growth*100:,.1f}% YoY")
                if pd.notna(net_margin):
                    insight_parts.append(f"Net margin {net_margin*100:,.1f}%")
                if pd.notna(fcf_margin):
                    insight_parts.append(f"FCF margin {fcf_margin*100:,.1f}%")
                if pd.notna(debt_equity):
                    insight_parts.append(f"D/E {debt_equity:,.2f}")

                risk_flags = []
                if pd.notna(growth) and growth < 0:
                    risk_flags.append("Revenue contraction")
                if pd.notna(net_margin) and net_margin < 0:
                    risk_flags.append("Negative profitability")
                if pd.notna(fcf_margin) and fcf_margin < 0:
                    risk_flags.append("Cash burn")
                if pd.notna(debt_equity) and debt_equity > 1.5:
                    risk_flags.append("High leverage")

                insight = "; ".join(insight_parts)
                if risk_flags:
                    insight += " • Risk: " + ", ".join(risk_flags)

                records.append({
                    "Ticker": tkr,
                    "Growth": growth,
                    "NetMargin": net_margin,
                    "FCFMargin": fcf_margin,
                    "DebtEquity": debt_equity,
                    "Insight": insight,
                })
            score_df = pd.DataFrame(records)
            # Percentile ranks (skip NaNs)
            for col in ["Growth", "NetMargin", "FCFMargin"]:
                score_df[col + "_score"] = score_df[col].rank(pct=True, na_option="bottom")
            # DebtEquity lower better
            score_df["DebtEquity_score"] = 1 - score_df["DebtEquity"].rank(pct=True, na_option="bottom")
            score_df["HealthScore"] = score_df[[c for c in score_df.columns if c.endswith("_score")]].mean(axis=1, skipna=True)
            score_df = score_df.dropna(subset=["HealthScore"])
            return score_df

        score_df = compute_health_scores()
        meta_finq = meta.merge(score_df[["Ticker", "HealthScore", "Insight"]], on="Ticker", how="left")

        categories_finq = sorted(meta_finq["Category"].unique())
        selected_cat_finq = st.selectbox("Select Category", categories_finq, key="fh_category_finq")

        cat_df_finq = meta_finq[meta_finq["Category"] == selected_cat_finq].dropna(subset=["HealthScore"])
        top_df_finq = cat_df_finq.sort_values("HealthScore", ascending=False).head(10)

        if top_df_finq.empty:
            st.info("No sufficient data to compute health scores for this category yet.")
        else:
            st.markdown(f"### Top Stocks in {selected_cat_finq}")
            display_cols_finq = ["Ticker", "Name", "Sector", "HealthScore", "Insight"]
            if "Insight" not in top_df_finq.columns:
                top_df_finq["Insight"] = "Data insufficient"
            # Round HealthScore
            top_df_finq["HealthScore"] = top_df_finq["HealthScore"].round(2)
            st.dataframe(top_df_finq[display_cols_finq].reset_index(drop=True), use_container_width=True)

    with custom_tab:
        st.header("Your Selections")

        # Get the list of available metrics
        available_metrics = df["Metric"].unique()

        # Load user preferences
        user_prefs = _load_user_prefs().get(st.session_state.get("user", ""), {})
        
        selected_metrics = st.multiselect(
            "Select your preferred metrics for health score calculation:",
            available_metrics,
            default=user_prefs.get("health_metrics", [])
        )

        if st.button("Save Preferences"):
            all_prefs = _load_user_prefs()
            user = st.session_state.get("user")
            if user:
                all_prefs.setdefault(user, {})["health_metrics"] = selected_metrics
                _save_user_prefs(all_prefs)
                st.success("Preferences saved!")

        if selected_metrics:
            # Display dynamic formula
            formula_str = " + ".join([f"`{m}_score`" for m in selected_metrics])
            st.markdown(f"""**Custom Health Score Formula:** `({formula_str}) / {len(selected_metrics)}`""")
            with st.expander("How are individual metrics scored?"):
                st.markdown("""
                Each selected metric is converted into a score between 0 and 1 using percentile ranking. 
                A higher percentile rank indicates a better score. 
                
                **Note:** For simplicity, this calculation assumes that a higher value for each selected metric is always better. 
                If you select metrics where a lower value is preferable (e.g., Debt-to-Equity Ratio), 
                you may need to manually invert its contribution to the overall score for accurate results.
                """)
            
            st.subheader("Custom Health Score Analysis")

            # Filter the DataFrame to include only the selected metrics
            filtered_df = df[df["Metric"].isin(selected_metrics)]

            # Normalize the metrics (example: percentile ranking)
            normalized_df = filtered_df.copy()
            for metric in selected_metrics:
                # Assuming higher is better for all metrics for simplicity.
                # A real implementation would need to handle metrics where lower is better.
                normalized_df[metric + "_score"] = normalized_df.groupby("Metric")["Value"].rank(pct=True)

            # Calculate the health score (average of normalized values)
            score_cols = [m + "_score" for m in selected_metrics]
            health_scores = normalized_df.groupby("Ticker")[score_cols].mean().mean(axis=1).reset_index(name="HealthScore")
            
            # Generate insights based on the selected metrics
            def generate_insight(row):
                ticker = row['Ticker']
                ticker_metrics = filtered_df[filtered_df['Ticker'] == ticker]
                if ticker_metrics.empty:
                    return "N/A"
                
                parts = []
                for metric in selected_metrics:
                    # Use .get(0, None) to avoid index errors if a metric is missing for a ticker
                    val_series = ticker_metrics[ticker_metrics['Metric'] == metric]['Value']
                    val = val_series.iloc[0] if not val_series.empty else None
                    parts.append(f"{metric}: {human_format(val)}")
                return "; ".join(parts)

            # Merge with meta data and health scores
            meta_custom = meta.merge(health_scores, on="Ticker", how="left")
            
            # Apply insight generation
            meta_custom['Insight'] = meta_custom.apply(generate_insight, axis=1)

            categories_custom = sorted(meta_custom["Category"].unique())
            selected_cat_custom = st.selectbox("Select Category", categories_custom, key="fh_category_custom")

            cat_df_custom = meta_custom[meta_custom["Category"] == selected_cat_custom].dropna(subset=["HealthScore"])
            top_df_custom = cat_df_custom.sort_values("HealthScore", ascending=False).head(10)

            if top_df_custom.empty:
                st.info("No sufficient data to compute health scores for this category and selection.")
            else:
                st.write("**Top Companies by Custom Health Score:**")
                display_cols_custom = ["Ticker", "Name", "Sector", "HealthScore", "Insight"]
                st.dataframe(top_df_custom[display_cols_custom].reset_index(drop=True).round(2), use_container_width=True)

# ------------------------- Nexus Community Page ------------------------- #

if page == "Nexus":
    st.markdown("<h2 style='text-align: center;'>🌐 Nexus – Community</h2>", unsafe_allow_html=True)

    nx = st.session_state.get("nexus", {})
    user = st.session_state.get("user")
    if user not in nx:
        st.error("Profile not found.")
        st.stop()

    prof = nx[user]

    # If viewing another user's profile
    if st.session_state.get("profile_user") and st.session_state["profile_user"] != user:
        view_user = st.session_state["profile_user"]
        if view_user not in nx:
            st.error("User not found.")
        else:
            vp = nx[view_user]
            st.markdown(f"### 👤 {view_user}'s Page")
            st.markdown(f"**Followers:** {len(vp['followers'])} • **Following:** {len(vp['following'])} • **Friends:** {len(vp['friends'])}")
            if st.button("🔙 Back", key="back_btn"):
                st.session_state.pop("profile_user")
                st.experimental_rerun()

            st.markdown("---")
            st.markdown("#### Threads")
            for post in reversed(vp["posts"]):
                st.markdown(post["content"])
                st.markdown("**Comments:**")
                for c in post["comments"]:
                    st.markdown(f"- *{c['user']}*: {c['text']}")
                st.markdown("---")
            st.stop()

    tab_people, tab_messages, tab_my_page = st.tabs(["People", "Messages", "My Page"])

    # ---------------- People Tab ---------------- #
    with tab_people:
        st.subheader("Community Members")
        search_term = st.text_input("Search users", "", key="user_search")
        others_all = [u for u in nx.keys() if u != user]
        if search_term:
            term = search_term.lower()
            others = [u for u in others_all if term in u.lower()]
        else:
            others = others_all

        if not others:
            st.info("No other users yet.")
        for ou in others:
            op = nx[ou]
            cols = st.columns([2,1,1,1])
            cols[0].markdown(f"**{ou}**")
            if ou in prof["friends"]:
                cols[1].markdown("✅ Friend")
            elif ou in prof["requests"]:
                if cols[1].button("Accept", key=f"acc_{ou}"):
                    prof["friends"].append(ou)
                    prof["requests"].remove(ou)
                    nx[ou]["friends"].append(user)
                    _save_nexus(nx)
                    st.experimental_rerun()
            else:
                if cols[1].button("Add Friend", key=f"req_{ou}"):
                    if user not in nx[ou]["requests"]:
                        nx[ou]["requests"].append(user)
                        _save_nexus(nx)
                        st.success("Request sent!")

            # follow / unfollow
            if user in nx[ou]["followers"]:
                if cols[2].button("Unfollow", key=f"unf_{ou}"):
                    nx[ou]["followers"].remove(user)
                    prof["following"].remove(ou)
                    _save_nexus(nx)
                    st.experimental_rerun()
            else:
                if cols[2].button("Follow", key=f"fol_{ou}"):
                    nx[ou]["followers"].append(user)
                    prof["following"].append(ou)
                    _save_nexus(nx)
                    st.experimental_rerun()

            # View page
            if cols[3].button("View Page", key=f"view_{ou}"):
                st.session_state["profile_user"] = ou
                st.experimental_rerun()

    # ---------------- Messages Tab ---------------- #
    with tab_messages:
        st.subheader("Direct Messages")
        friends = prof["friends"]
        if not friends:
            st.info("Add friends to start messaging.")
        else:
            chat_target = st.selectbox("Chat with", friends, key="msg_target")
            # load messages store
            msg_store = nx.get("_messages", [])
            history = [m for m in msg_store if (m["from"]==user and m["to"]==chat_target) or (m["from"]==chat_target and m["to"]==user)]
            for m in history[-20:]:
                align = "▶" if m["from"]==user else "◀"
                st.markdown(f"{align} **{m['from']}**: {m['text']}")
            new_msg = st.text_input("Type a message", key="msg_input")
            if st.button("Send", key="msg_send") and new_msg.strip():
                msg_store.append({"from":user,"to":chat_target,"text":new_msg})
                nx["_messages"] = msg_store
                _save_nexus(nx)
                st.experimental_rerun()

    # ---------------- My Page Tab ---------------- #
    with tab_my_page:
        st.subheader("My Page / Threads")
        post_text = st.text_area("Write a post (max 500 words)", max_chars=3000, key="post_text")
        if st.button("Publish", key="post_pub") and post_text.strip():
            words = len(post_text.split())
            if words>500:
                st.error("Post exceeds 500 words.")
            else:
                prof["posts"].append({"content": post_text, "comments": []})
                _save_nexus(nx)
                st.success("Posted!")

        st.markdown("---")
        st.markdown("### My Posts")
        for idx,p in enumerate(reversed(prof["posts"])):
            st.markdown(p["content"])
            st.markdown("**Comments:**")
            for c in p["comments"]:
                st.markdown(f"- *{c['user']}*: {c['text']}")
            comment_key = f"com_{idx}"
            new_c = st.text_input("Add comment", key=comment_key)
            if st.button("Comment", key=comment_key+"btn") and new_c.strip():
                p["comments"].append({"user":user, "text":new_c})
                _save_nexus(nx)
                st.experimental_rerun()