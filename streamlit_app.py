import pandas as pd
import streamlit as st
import altair as alt
import yfinance as yf
from functools import lru_cache
import numpy as np
import os, requests, json

st.set_page_config(page_title="FinQ Bot", layout="wide")

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
    """Load Nexus community store from disk."""
    if os.path.exists(NEXUS_PATH):
        try:
            with open(NEXUS_PATH, "r") as f:
                return json.load(f)
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
try:
    st.image("assets/finq_logo.svg", use_column_width=False, width=320)
except Exception:
    st.markdown("# 🧮 FinQ Bot")
st.caption("Simplified Info at fingertips")

PARQUET_PATH = "fundamentals_tall.parquet"

# ------------------------- Ticker Metadata & Logo Cache ------------------------- #

@st.cache_data(show_spinner=False)
def _load_meta_csv(path: str = "sp500_fundamentals.csv") -> dict:
    """Load pre-scraped ticker metadata (name, sector, industry) into a dict."""
    if os.path.exists(path):
        meta_df = pd.read_csv(path)[["Ticker", "Name", "Sector", "Industry"]]
        return meta_df.set_index("Ticker").to_dict("index")
    return {}

# Load once for the whole session
_TICKER_META = _load_meta_csv()


@st.cache_data(show_spinner=False)
def _get_logo_path(ticker: str) -> str | None:
    """Return local path to cached company logo, downloading once via yfinance if needed."""
    local_dir = "assets/logos"
    os.makedirs(local_dir, exist_ok=True)
    local_path = f"{local_dir}/{ticker}.png"
    if os.path.exists(local_path):
        return local_path
    # Try to fetch from Yahoo once
    try:
        logo_url = yf.Ticker(ticker).info.get("logo_url")
        if logo_url:
            resp = requests.get(logo_url, timeout=10)
            if resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                return local_path
    except Exception:
        pass
    return None

# ------------------------- Helpers ------------------------- #

@st.cache_data(show_spinner=True)
def load_data(path: str = PARQUET_PATH) -> pd.DataFrame:
    return pd.read_parquet(path)

@lru_cache(maxsize=1024)
def ticker_info(ticker: str) -> dict:
    """Lightweight metadata lookup that avoids network calls for bulk operations."""
    meta = _TICKER_META.get(ticker, {})
    return {
        "name": meta.get("Name") or ticker,
        "sector": meta.get("Sector", "N/A"),
        "industry": meta.get("Industry", "N/A"),
    }

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

# ------------------------- Load & Sidebar ------------------------- #

with st.spinner("Loading fundamentals data…"):
    df = load_data()

# ------------------------- Page Navigation ------------------------- #

page = st.sidebar.radio("Navigate", ["Dashboard", "Financial Health Monitoring", "Nexus"], key="main_nav")

# ------------------------- Welcome Page ------------------------- #

if page == "Welcome":
    st.markdown("## 👋 Welcome to FinQ Bot")
    user = st.session_state.get("current_user", "Guest")
    st.write(f"Hello, **{user}**! Use the navigation menu on the left to explore the dashboard or check financial health rankings.")
    st.stop()

# ------------------------- Dashboard Page ------------------------- #

if page == "Dashboard":
    st.markdown("## 📊 Dashboard")

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

        # Statement / metric category filter
        categories_available = sorted(df[df["Ticker"] == selected_ticker]["Category"].unique())
        stmt_selected = st.selectbox("Metric Category", categories_available, key="stmt_cat")

    # safe category fetch
    sel_cat = df[df["Ticker"] == selected_ticker]["Category"].iloc[0] if "Category" in df.columns else "N/A"

    with content_col:
        ticker_df = df[(df["Ticker"] == selected_ticker) & (df["Category"] == stmt_selected)]

        # ---------- Company Header ---------- #
        tinfo = ticker_info(selected_ticker)
        logo_path = _get_logo_path(selected_ticker)
        hcols = st.columns([1,4])
        with hcols[0]:
            if logo_path:
                st.image(logo_path, width=90)
        with hcols[1]:
            st.markdown(f"## {selected_ticker} – {tinfo['name']}")
            st.caption(f"Sector: {tinfo['sector']} • Industry: {tinfo['industry']}")

        # Compute universe of metrics for the selected ticker
        all_metrics = sorted(ticker_df["Metric"].unique())

        # ------------------------- Tabs ------------------------- #
        trend_tab, snapshot_tab = st.tabs(["📈 Metrics Trend Analysis", "📊 Snapshot & Changes"])

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

                base = (
                    alt.Chart(mdf)
                    .encode(
                        x=alt.X("FiscalPeriod", sort=None, title="Fiscal Period"),
                        y=alt.Y("Value", axis=alt.Axis(format="~s"), title="Value"),
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
            mode = st.radio("Display", ["Latest", "QoQ Δ", "YoY Δ"], horizontal=True)

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

# ------------------------- Financial Health Monitoring Page ------------------------- #

if page == "Financial Health Monitoring":
    st.markdown("## 🩺 Financial Health Monitoring")

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
    meta = meta.merge(score_df[["Ticker", "HealthScore", "Insight"]], on="Ticker", how="left")

    categories = sorted(meta["Category"].unique())
    selected_cat = st.selectbox("Select Category", categories, key="fh_category")

    cat_df = meta[meta["Category"] == selected_cat].dropna(subset=["HealthScore"])
    top_df = cat_df.sort_values("HealthScore", ascending=False).head(10)

    if top_df.empty:
        st.info("No sufficient data to compute health scores for this category yet.")
        st.stop()

    st.markdown(f"### Top Stocks in {selected_cat}")
    display_cols = ["Ticker", "Name", "Sector", "HealthScore", "Insight"]
    if "Insight" not in top_df.columns:
        top_df["Insight"] = "Data insufficient"
    # Round HealthScore
    top_df["HealthScore"] = top_df["HealthScore"].round(2)
    st.dataframe(top_df[display_cols].reset_index(drop=True), use_container_width=True)

    st.stop()

# ------------------------- Nexus Community Page ------------------------- #

if page == "Nexus":
    st.markdown("## 🌐 Nexus – Community")

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