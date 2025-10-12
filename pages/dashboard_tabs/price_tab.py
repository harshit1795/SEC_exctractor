import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf
from datetime import datetime, timedelta
import pandas_ta as ta
import plotly.graph_objects as go
import ast # For safe parsing of string literals
from polygon import RESTClient # New import
from auth import _load_user_prefs # New import

def render_kpi_chart(main_value, comparison_value, title):
    if isinstance(main_value, pd.Series):
        main_value = main_value.iloc[0] if not main_value.empty else 0
    if isinstance(comparison_value, pd.Series):
        comparison_value = comparison_value.iloc[0] if not comparison_value.empty else None

    if comparison_value is not None:
        delta = main_value - comparison_value
        delta_percent = (delta / comparison_value) * 100 if comparison_value != 0 else 0
    else:
        delta = 0
        delta_percent = 0
    
    st.metric(
        label=title,
        value=f"${main_value:,.2f}",
        delta=f"{delta_percent:,.2f}%"
    )

# Removed caching for now to ensure dynamic updates until root cause is found
def get_price_data(ticker: str, period: str = "2y", interval: str = "1d"):
    """Fetches historical price data from yfinance."""
    return yf.download(ticker, period=period, interval=interval)

def get_technical_analysis_summary(data):
    """Calculates technical indicators for summary (SMA for trend)."""
    if data.empty or 'close' not in data.columns:
        return None

    data.ta.sma(length=50, append=True)
    data.ta.sma(length=200, append=True)
    data.ta.rsi(length=14, append=True)
    data.ta.macd(fast=12, slow=26, signal=9, append=True)
    
    data.columns = [str(col).lower() for col in data.columns]

    latest_analysis = data.iloc[-1]
    trend = "Neutral"
    if pd.notna(latest_analysis.get('sma_50')) and pd.notna(latest_analysis.get('sma_200')):
        if latest_analysis['sma_50'] > latest_analysis['sma_200']:
            trend = "Bullish"
        else:
            trend = "Bearish"
            
    analysis_summary = {
        "trend": trend,
        "latest_rsi": latest_analysis.get('rsi_14'),
        "latest_macd": latest_analysis.get('macd_12_26_9'),
    }
    
    return analysis_summary

def get_sentiment_analysis(ticker_symbol):
    """Analyzes news sentiment for a stock using Polygon.ai."""
    try:
        user_prefs = _load_user_prefs().get(st.session_state.get("user"), {})
        polygon_api_key = user_prefs.get("POLYGON_API_KEY")

        st.warning(f"DEBUG: Loaded Polygon.ai API Key (first 5 chars): {str(polygon_api_key)[:5]}...")

        if not polygon_api_key:
            st.error("Polygon.ai API key not found. Please go to Settings to configure it.")
            return None, []

        client = RESTClient(polygon_api_key)
        
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        news_response = client.get_reference_news(
            ticker_lte=ticker_symbol,
            published_utc_gte=thirty_days_ago.isoformat(),
            published_utc_lte=today.isoformat(),
            limit=50 # Fetch up to 50 articles
        )
        
        news_articles = []
        if news_response and news_response.results:
            for article in news_response.results:
                news_articles.append({'title': article.title, 'link': article.article_url})
        
        if not news_articles:
            return None, []

        positive_keywords = ["beat", "exceed", "upgrade", "strong", "growth", "profit", "revenue", "bullish", "buy", "outperform", "surge", "rally"]
        negative_keywords = ["miss", "downgrade", "weak", "loss", "decline", "bearish", "sell", "underperform", "fall", "cut", "concern", "risk"]
        sentiment_scores = []
        for article in news_articles:
            title = article.get('title', '').lower()
            pos_count = sum(1 for word in positive_keywords if word in title)
            neg_count = sum(1 for word in negative_keywords if word in title)
            score = (pos_count - neg_count) / (pos_count + neg_count) if (pos_count + neg_count) > 0 else 0
            sentiment_scores.append(score)

        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        sentiment_category = "Positive" if avg_sentiment > 0.2 else "Negative" if avg_sentiment < -0.2 else "Neutral"
            
        return {
            "overall_sentiment": sentiment_category,
            "sentiment_score": avg_sentiment,
            "articles_analyzed": len(news_articles)
        }, news_articles
    except Exception as e:
        st.error(f"Error fetching news from Polygon.ai: {e}")
        return None, []

def render_filters():
    st.markdown("#### Price Filters")
    start_date_input = st.date_input("Start date", pd.to_datetime("today") - pd.DateOffset(months=1), key="price_start")
    end_date_input = st.date_input("End date", pd.to_datetime("today"), key="price_end")
    aggregation = st.selectbox("Aggregation", ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'], key="price_agg")
    chart_type = st.radio("Chart Type", ['Candlestick', 'Line'], key="price_chart_type")
    if chart_type == 'Line':
        line_metric = st.selectbox("Metric for Line Chart", ['Open', 'High', 'Low', 'Close'], index=3, key="price_line_metric").lower()
    else:
        line_metric = 'close' # Default for candlestick
    
    return {"start_date": start_date_input, "end_date": end_date_input, "aggregation": aggregation, "chart_type": chart_type, "line_metric": line_metric}

def render_content(selected_ticker, filters):
    st.markdown("### Price Chart")

    # --- FILTERS ---
    c1, c2 = st.columns(2)
    with c1:
        start_date_input = st.date_input("Start date", pd.to_datetime("today") - pd.DateOffset(months=1), key="price_start")
    with c2:
        end_date_input = st.date_input("End date", pd.to_datetime("today"), key="price_end")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        aggregation = st.selectbox("Aggregation", ['Daily', 'Weekly', 'Monthly'], key="price_agg")
    with c2:
        chart_type = st.radio("Chart Type", ['Candlestick', 'Line'], key="price_chart_type")
    with c3:
        line_metric = st.selectbox("Metric for Line Chart", ['Open', 'High', 'Low', 'Close'], index=3, key="price_line_metric").lower() if chart_type == 'Line' else 'close'
    with c4:
        show_bb = st.checkbox("Show Bollinger Bands", key="price_show_bb")

    # --- DATA PIPELINE ---
    # 1. Fetch daily data for the longest possible range needed (for TA)
    price_df_full = get_price_data(selected_ticker, period="2y", interval="1d")
    if price_df_full.empty:
        st.warning("Could not retrieve price data.")
        return

    # 2. Immediately standardize columns and index
    processed_columns = []
    for col in price_df_full.columns:
        col_str = str(col)
        if col_str.startswith("('") and col_str.endswith("')"):
            try:
                import ast
                parsed_tuple = ast.literal_eval(col_str)
                if isinstance(parsed_tuple, tuple) and len(parsed_tuple) > 0:
                    processed_columns.append(str(parsed_tuple[0]))
                else:
                    processed_columns.append(col_str) # Fallback
            except (ValueError, SyntaxError):
                processed_columns.append(col_str) # Fallback
        else:
            processed_columns.append(col_str)
    
    price_df_full.columns = [c.lower() for c in processed_columns]
    price_df_full.reset_index(inplace=True)
    price_df_full.rename(columns={'Date': 'date'}, inplace=True) # yfinance now uses lowercase 'date' index name

    # 3. Get Technical Analysis Summary (for KPIs) and Sentiment Analysis
    analysis_summary = get_technical_analysis_summary(price_df_full.copy())
    sentiment_summary, news_articles_from_polygon = get_sentiment_analysis(selected_ticker)

    # 4. Filter by Date Range to create the base dataframe for display
    price_df = price_df_full[
        (price_df_full['date'].dt.date >= start_date_input) &
        (price_df_full['date'].dt.date <= end_date_input)
    ].copy()

    # 5. Resample if needed (for Weekly/Monthly)
    if aggregation in ['Weekly', 'Monthly']:
        price_df.set_index('date', inplace=True)
        agg_logic = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}
        period_map = {'Weekly': 'W', 'Monthly': 'M'}
        price_df = price_df.resample(period_map[aggregation]).agg(agg_logic).dropna().reset_index()

    if price_df.empty:
        st.warning("No data available for the selected time range and aggregation.")
        return

    # 6. Calculate Indicators on the final, processed dataframe
    price_df.ta.bbands(length=20, std=2, append=True)
    price_df.ta.rsi(length=14, append=True)
    price_df.ta.macd(fast=12, slow=26, signal=9, append=True)
    price_df.columns = [str(col).lower() for col in price_df.columns] # Ensure new indicator columns are also lowercase

    # --- DYNAMIC KPI SECTION ---
    st.subheader("Key Performance Indicators")
    kpi_col1, kpi_col2 = st.columns([1, 2])
    with kpi_col1:
        latest_close = price_df['close'].iloc[-1]
        previous_close = price_df['close'].iloc[-2] if len(price_df) > 1 else latest_close
        render_kpi_chart(latest_close, previous_close, f"Latest {aggregation} Change")
    with kpi_col2:
        st.write("**Latest Period's Data**")
        latest_data = price_df.iloc[-1:][['open', 'high', 'low', 'close', 'volume']].copy()
        latest_data['volume'] = latest_data['volume'].apply(lambda x: f"{x / 1_000_000:.2f}M")
        for col in ['open', 'high', 'low', 'close']:
            latest_data[col] = latest_data[col].apply(lambda x: f"${x:,.2f}")
        st.table(latest_data.T.rename(columns={latest_data.index[0]: "Value"}))

    # --- MAIN PRICE CHART (PLOTLY) ---
    st.subheader(f"{aggregation} {chart_type} Chart")
    fig = go.Figure()
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(x=price_df['date'], open=price_df['open'], high=price_df['high'], low=price_df['low'], close=price_df['close'], name='Price'))
    else: # Line chart
        fig.add_trace(go.Scatter(x=price_df['date'], y=price_df[line_metric], mode='lines', name=line_metric.capitalize()))

    if show_bb and 'bbu_20_2.0_2.0' in price_df.columns:
        fig.add_trace(go.Scatter(x=price_df['date'], y=price_df['bbu_20_2.0_2.0'], mode='lines', line=dict(width=0), hoverinfo='none', showlegend=False))
        fig.add_trace(go.Scatter(x=price_df['date'], y=price_df['bbl_20_2.0_2.0'], mode='lines', line=dict(width=0), fillcolor='rgba(128,128,128,0.2)', fill='tonexty', hoverinfo='none', showlegend=False))
        fig.add_trace(go.Scatter(x=price_df['date'], y=price_df['bbm_20_2.0_2.0'], mode='lines', line=dict(color='gray', dash='dash'), name='Middle BB'))

    fig.update_layout(title_text=f"{aggregation} {chart_type} Chart for {selected_ticker}", xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=False, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    # --- ADVANCED ANALYSIS SECTION ---
    st.markdown("---")
    st.subheader("Advanced Analysis")
    with st.expander("Technical Analysis", expanded=False):
        if analysis_summary:
            kpi_cols = st.columns(3)
            kpi_cols[0].metric("Trend", analysis_summary.get('trend', 'N/A'), help="The trend is determined by the relationship between the 50-day and 200-day Simple Moving Averages (SMA). A 'Bullish' trend (Golden Cross) occurs when the 50-day SMA is above the 200-day SMA. A 'Bearish' trend (Death Cross) occurs when the 50-day SMA is below the 200-day SMA.")
            kpi_cols[1].metric("Latest RSI", f"{analysis_summary.get('latest_rsi', 0):.2f}")
            kpi_cols[2].metric("Latest MACD", f"{analysis_summary.get('latest_macd', 0):.2f}")

            st.write("##### Key Levels for Selected Period")
            latest_values = price_df.iloc[-1] if not price_df.empty else None
            if latest_values is not None:
                dynamic_support = price_df['close'].min()
                dynamic_resistance = price_df['close'].max()
                summary_data = {
                    "Metric": ["Resistance", "Support", "Bollinger Upper Band", "Bollinger Middle Band", "Bollinger Lower Band"],
                    "Value": [
                        f"${dynamic_resistance:,.2f}",
                        f"${dynamic_support:,.2f}",
                        f"${latest_values.get('bbu_20_2.0_2.0', 0):,.2f}",
                        f"${latest_values.get('bbm_20_2.0_2.0', 0):,.2f}",
                        f"${latest_values.get('bbl_20_2.0_2.0', 0):,.2f}"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                st.table(summary_df.set_index("Metric"))
            else:
                st.warning("No data available for the selected period to calculate key levels.")

            font_config = {"titleFontSize": 18, "labelFontSize": 14}

            rsi_chart = alt.Chart(price_df).mark_line(color='green').encode(x=alt.X('date:T', title=''), y=alt.Y('rsi_14:Q', title='RSI', scale=alt.Scale(domain=[0, 100]))).properties(height=100, title='RSI')
            rsi_rules = alt.Chart(pd.DataFrame({'y': [30, 70]})).mark_rule(color='gray').encode(y='y')
            
            macd_base = alt.Chart(price_df).encode(x=alt.X('date:T', title='Date')).properties(height=100, title='MACD')
            macd_lines = macd_base.mark_line().transform_fold(fold=['macd_12_26_9', 'macds_12_26_9'], as_=['indicator', 'value']).encode(y=alt.Y('value:Q', title='Value'), color='indicator:N')
            macd_hist = macd_base.mark_bar(opacity=0.4).encode(y=alt.Y('macdh_12_26_9:Q', title='Histogram'), color=alt.condition('datum.macdh_12_26_9 > 0', alt.value('green'), alt.value('red')))
            macd_chart = alt.layer(macd_lines, macd_hist).resolve_scale(y='independent')

            combined_chart = alt.vconcat(rsi_chart + rsi_rules, macd_chart, spacing=10).configure_title(fontSize=font_config["titleFontSize"]).configure_axis(labelFontSize=font_config["labelFontSize"], titleFontSize=font_config["labelFontSize"]).configure_legend(titleFontSize=font_config["labelFontSize"], labelFontSize=font_config["labelFontSize"])
            st.altair_chart(combined_chart, use_container_width=True)
            st.caption("The MACD Histogram (green/red bars) shows the difference between the MACD line and the Signal line. Green bars indicate the MACD line is above the Signal line (bullish momentum), while red bars indicate it is below (bearish momentum).")

    # News sentiment is not dynamic and can be left as is
    with st.expander("News Sentiment Analysis", expanded=False):
        if sentiment_summary:
            st.metric("Overall Sentiment", sentiment_summary.get('overall_sentiment', 'N/A'))
            st.write("##### Recent News")
            if news_articles_from_polygon:
                for article in news_articles_from_polygon[:10]:
                    title = article.get('title', 'No Title Available')
                    link = article.get('link', '#')
                    st.markdown(f"- [{title}]({link})")
            else:
                st.write("No news found for this ticker.")
        else:
            st.write("Could not retrieve news sentiment. Please check your Polygon.ai API key in Settings.")
