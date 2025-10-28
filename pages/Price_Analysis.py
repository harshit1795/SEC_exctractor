
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import re

def get_stock_data(ticker_symbol, period="1y"):
    """Fetches historical stock data."""
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period=period)
    return data

def get_technical_analysis(data):
    """Calculates technical indicators."""
    if data.empty:
        return None, None

    # Create a new DataFrame for the analysis
    analysis = pd.DataFrame(index=data.index)
    
    # Moving Averages
    analysis['SMA_50'] = ta.sma(data['Close'], length=50)
    analysis['SMA_200'] = ta.sma(data['Close'], length=200)
    
    # RSI
    analysis['RSI'] = ta.rsi(data['Close'], length=14)
    
    # MACD
    macd = ta.macd(data['Close'], fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        analysis['MACD'] = macd['MACD_12_26_9']
        analysis['MACD_signal'] = macd['MACDs_12_26_9']
        analysis['MACD_hist'] = macd['MACDh_12_26_9']

    # Bollinger Bands
    bollinger = ta.bbands(data['Close'], length=20, std=2)
    if bollinger is not None and not bollinger.empty:
        analysis['BB_upper'] = bollinger['BBU_20_2.0']
        analysis['BB_middle'] = bollinger['BBM_20_2.0']
        analysis['BB_lower'] = bollinger['BBL_20_2.0']

    # Determine Trend
    latest_analysis = analysis.iloc[-1]
    trend = "Neutral"
    if pd.notna(latest_analysis['SMA_50']) and pd.notna(latest_analysis['SMA_200']):
        if latest_analysis['SMA_50'] > latest_analysis['SMA_200']:
            trend = "Bullish"
        else:
            trend = "Bearish"
            
    # Support and Resistance (simple implementation)
    support = data['Close'][-200:].min()
    resistance = data['Close'][-200:].max()
    
    analysis_summary = {
        "trend": trend,
        "support": support,
        "resistance": resistance,
        "latest": latest_analysis.to_dict()
    }
    
    return analysis, analysis_summary

def get_sentiment_analysis(ticker_symbol):
    """Analyzes news sentiment for a stock."""
    ticker = yf.Ticker(ticker_symbol)
    news = ticker.news

    if not news:
        return None, []

    positive_keywords = [
        "beat", "exceed", "upgrade", "strong", "growth", "profit", 
        "revenue", "bullish", "buy", "outperform", "surge", "rally",
        "breakthrough", "innovation", "expansion", "record"
    ]
    negative_keywords = [
        "miss", "downgrade", "weak", "loss", "decline", "bearish", 
        "sell", "underperform", "fall", "cut", "concern", "risk",
        "lawsuit", "investigation", "recall", "bankruptcy"
    ]

    sentiment_scores = []
    for article in news:
        title = article.get('title', '').lower()
        # Simple keyword search
        pos_count = sum(1 for word in positive_keywords if word in title)
        neg_count = sum(1 for word in negative_keywords if word in title)
        
        score = 0
        if pos_count + neg_count > 0:
            score = (pos_count - neg_count) / (pos_count + neg_count)
        sentiment_scores.append(score)

    if not sentiment_scores:
        avg_sentiment = 0
    else:
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

    if avg_sentiment > 0.2:
        sentiment_category = "Positive"
    elif avg_sentiment < -0.2:
        sentiment_category = "Negative"
    else:
        sentiment_category = "Neutral"
        
    sentiment_summary = {
        "overall_sentiment": sentiment_category,
        "sentiment_score": avg_sentiment,
        "articles_analyzed": len(news)
    }
    
    return sentiment_summary, news


st.set_page_config(layout="wide")
st.title("Stock Price and Sentiment Analysis")

ticker_symbol = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL").upper()

if st.button(f"Analyze {ticker_symbol}"):
    data = get_stock_data(ticker_symbol)
    
    if data.empty:
        st.error(f"Could not retrieve data for {ticker_symbol}. Please check the ticker.")
    else:
        st.header(f"Analysis for {ticker_symbol}")
        
        analysis_df, analysis_summary = get_technical_analysis(data)
        sentiment_summary, news = get_sentiment_analysis(ticker_symbol)

        # --- Display ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Technical Analysis")
            if analysis_summary:
                st.metric("Trend", analysis_summary['trend'])
                st.metric("Support", f"${analysis_summary['support']:.2f}")
                st.metric("Resistance", f"${analysis_summary['resistance']:.2f}")

                st.write("#### Price Chart with Bollinger Bands")
                chart_data = pd.concat([data['Close'], analysis_df[['BB_upper', 'BB_middle', 'BB_lower']]], axis=1)
                st.line_chart(chart_data)

                st.write("#### RSI Indicator")
                st.line_chart(analysis_df['RSI'])
                
                st.write("#### Key Indicator Values")
                st.table(pd.DataFrame(analysis_summary['latest'], index=['Value']).T)

        with col2:
            st.subheader("News Sentiment Analysis")
            if sentiment_summary:
                st.metric("Overall Sentiment", sentiment_summary['overall_sentiment'])
                st.metric("Sentiment Score", f"{sentiment_summary['sentiment_score']:.3f}")
                st.metric("Articles Analyzed", sentiment_summary['articles_analyzed'])
                
                st.write("#### Recent News")
                for article in news[:10]: # Display top 10 articles
                    st.markdown(f"[{article['title']}]({article['link']})")
            else:
                st.write("No news found for this ticker.")
