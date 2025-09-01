"""
Enhanced FinQ Chatbot Tab with MCP Architecture
Provides intelligent financial analysis with access to multiple data sources
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import yfinance as yf
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import traceback
from pathlib import Path
import os

# Import local modules
from auth import load_api_keys
from fred_data import get_fred_series, get_multiple_fred_series

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceManager:
    """MCP-style data source manager for accessing financial data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        cache_time, _ = self.cache[key]
        return (datetime.now() - cache_time).seconds < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        self.cache[key] = (datetime.now(), data)
    
    def get_yahoo_finance_data(self, ticker: str, period: str = "1y") -> Dict[str, Any]:
        """Fetch comprehensive data from Yahoo Finance"""
        cache_key = f"yf_{ticker}_{period}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            ticker_obj = yf.Ticker(ticker)
            
            data = {
                'info': ticker_obj.info,
                'financials': ticker_obj.financials,
                'balance_sheet': ticker_obj.balance_sheet,
                'cashflow': ticker_obj.cashflow,
                'quarterly_financials': ticker_obj.quarterly_financials,
                'quarterly_balance_sheet': ticker_obj.quarterly_balance_sheet,
                'quarterly_cashflow': ticker_obj.quarterly_cashflow,
                'history': ticker_obj.history(period=period),
                'recommendations': ticker_obj.recommendations,
                'earnings': ticker_obj.earnings,
                'quarterly_earnings': ticker_obj.quarterly_earnings
            }
            
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {ticker}: {e}")
            return {}
    
    def get_fred_economic_data(self, series_ids: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch economic data from FRED"""
        cache_key = f"fred_{'_'.join(series_ids)}_{start_date}_{end_date}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            data = get_multiple_fred_series(series_ids, start_date, end_date)
            self._cache_data(cache_key, data)
            return data
        except Exception as e:
            logger.error(f"Error fetching FRED data: {e}")
            return pd.DataFrame()

class FinancialAnalyzer:
    """AI-powered financial analysis engine"""
    
    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.api_key = api_key
        
    def analyze_financial_data(self, user_question: str, context_data: Dict[str, Any]) -> str:
        """Generate comprehensive financial analysis"""
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(user_question, context_data)
        
        try:
            response = self.model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            return response.text
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"I apologize, but I encountered an error while analyzing the data: {str(e)}"
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt for financial analysis"""
        return """You are FinQ, an expert financial analyst AI assistant with deep knowledge of:
- Financial statement analysis (Income Statement, Balance Sheet, Cash Flow)
- Market analysis and stock valuation (including price history and technical indicators)
- Economic indicators and macroeconomic trends (FRED data)

Your capabilities:
1. Analyze financial data from multiple sources (Yahoo Finance, FRED)
2. Provide insights on trends, ratios, and financial health
3. Correlate company performance with macroeconomic indicators
4. Analyze stock price trends and key performance indicators
5. Explain complex financial concepts in simple terms

Guidelines:
- Always base your analysis on the provided data
- Be specific with numbers and metrics when available
- Highlight trends and patterns
- Identify potential risks or concerns
- Provide actionable insights
- Use professional financial terminology appropriately
- If data is insufficient, clearly state what additional information would be helpful
- Format responses with clear sections and bullet points when appropriate"""
    
    def _build_user_prompt(self, user_question: str, context_data: Dict[str, Any]) -> str:
        """Build user prompt with context data"""
        
        prompt_parts = [f"User Question: {user_question}\n"]
        
        if context_data.get('selected_tickers'):
            tickers = context_data['selected_tickers']
            prompt_parts.append(f"Selected Companies: {', '.join(tickers)}\n")
            
            if context_data.get('metric_categories'):
                prompt_parts.append(f"Selected Metrics: {', '.join(context_data['metric_categories'])}\n")
            
            if context_data.get('yahoo_data'):
                yf_data = context_data['yahoo_data']
                for ticker, data in yf_data.items():
                    if data.get('info'):
                        company_name = data['info'].get('longName', ticker)
                        sector = data['info'].get('sector', 'N/A')
                        prompt_parts.append(f"\n--- Data for {ticker} ({company_name}) ---")
                        prompt_parts.append(f"Sector: {sector}")
                        
                        if data.get('longBusinessSummary'):
                            prompt_parts.append(f"Business Summary: {data['longBusinessSummary'][:200]}...")
                        
                        available_metrics = []
                        if "Income Statement" in context_data.get('metric_categories', []) and data.get('financials') is not None:
                            available_metrics.append("Income Statement")
                        if "Balance Sheet" in context_data.get('metric_categories', []) and data.get('balance_sheet') is not None:
                            available_metrics.append("Balance Sheet")
                        if "Cash Flow" in context_data.get('metric_categories', []) and data.get('cashflow') is not None:
                            available_metrics.append("Cash Flow")
                        
                        if available_metrics:
                            prompt_parts.append(f"Available Financials: {', '.join(available_metrics)}")

                        # Add more detailed price info
                        price_info = []
                        if data.get('info'):
                            if 'currentPrice' in data['info']:
                                price_info.append(f"Current Price: ${data['info']['currentPrice']:.2f}")
                            if 'dayHigh' in data['info'] and 'dayLow' in data['info']:
                                price_info.append(f"Day's Range: ${data['info']['dayLow']:.2f} - ${data['info']['dayHigh']:.2f}")
                            if 'fiftyTwoWeekHigh' in data['info'] and 'fiftyTwoWeekLow' in data['info']:
                                price_info.append(f"52-Week Range: ${data['info']['fiftyTwoWeekLow']:.2f} - ${data['info']['fiftyTwoWeekHigh']:.2f}")
                            if 'averageVolume' in data['info']:
                                price_info.append(f"Avg. Volume: {data['info']['averageVolume']:,}")
                        if price_info:
                            prompt_parts.append(f"Price Data: {', '.join(price_info)}")

        if context_data.get('economic_data') is not None and not context_data['economic_data'].empty:
            prompt_parts.append("\n--- Macroeconomic Data ---")
            prompt_parts.append(f"Available Indicators: {', '.join(context_data['economic_data'].columns)}")
            prompt_parts.append(context_data['economic_data'].tail().to_string())
        
        prompt_parts.append("\nPlease provide a comprehensive analysis based on the available data.")
        
        return "\n".join(prompt_parts)

class ChatbotInterface:
    """Streamlit-based chatbot interface"""
    
    def __init__(self):
        self.data_manager = DataSourceManager()
        self.analyzer = None
        self.initialize_ai()
    
    def initialize_ai(self):
        """Initialize AI model with API keys"""
        try:
            load_api_keys()
            api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
            if api_key:
                self.analyzer = FinancialAnalyzer(api_key)
        except Exception as e:
            logger.error(f"Error initializing AI: {e}")

    def render_filters(self, all_tickers):
        st.markdown("#### Chatbot Context")
        
        with st.expander("Company Data", expanded=True):
            selected_tickers = st.multiselect("Select Companies:", options=all_tickers, default=st.session_state.get('selected_tickers', []))
            st.session_state['selected_tickers'] = selected_tickers

            if selected_tickers:
                metric_categories = st.multiselect(
                    "Select Financial Statements:",
                    options=["Income Statement", "Balance Sheet", "Cash Flow"],
                    default=st.session_state.get('metric_categories', ["Income Statement", "Balance Sheet"])
                )
                st.session_state['metric_categories'] = metric_categories

                if st.button("Load Company Data"):
                    with st.spinner(f"Loading data for {len(selected_tickers)} companies..."):
                        all_yahoo_data = {}
                        for ticker in selected_tickers:
                            yahoo_data = self.data_manager.get_yahoo_finance_data(ticker)
                            all_yahoo_data[ticker] = yahoo_data
                        st.session_state['yahoo_data'] = all_yahoo_data
                        st.success("Company data loaded!")

        with st.expander("Macroeconomic Data"):
            fred_series_options = {
                "Real GDP": "GDPC1",
                "Inflation (CPI)": "CPIAUCSL",
                "Unemployment Rate": "UNRATE",
                "10-Year Treasury Yield": "DGS10",
                "Federal Funds Rate": "FEDFUNDS",
            }
            selected_fred_keys = st.multiselect("Select Economic Indicators:", options=list(fred_series_options.keys()), default=st.session_state.get('selected_fred_keys', []))
            st.session_state['selected_fred_keys'] = selected_fred_keys

            if st.button("Load Economic Data"):
                if selected_fred_keys:
                    with st.spinner("Loading economic data..."):
                        series_to_fetch = [fred_series_options[key] for key in selected_fred_keys]
                        end_date = datetime.now().strftime('%Y-%m-%d')
                        start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d') # 5 years of data
                        economic_data = self.data_manager.get_fred_economic_data(series_to_fetch, start_date, end_date)
                        # Rename columns to be more descriptive
                        inv_map = {v: k for k, v in fred_series_options.items()}
                        economic_data.rename(columns=inv_map, inplace=True)
                        st.session_state['economic_data'] = economic_data
                        st.success("Economic data loaded!")
                else:
                    st.warning("Please select at least one economic indicator.")

    def render_content(self):
        st.markdown("## 🤖 FinQ Financial Assistant")
        st.markdown("Ask me anything about financial data, company analysis, or market insights!")
        self._render_chat_interface()
        self._render_quick_actions()

    def _render_chat_interface(self):
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask me about financial data, company analysis, or market insights..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        response = self._generate_response(prompt)
                        st.markdown(response)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    def _generate_response(self, prompt: str) -> str:
        if not self.analyzer:
            return "AI model not initialized. Please check your API configuration."
        
        try:
            context_data = self._gather_context_data()
            response = self.analyzer.analyze_financial_data(prompt, context_data)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _gather_context_data(self) -> Dict[str, Any]:
        context = {}
        if 'selected_tickers' in st.session_state:
            context['selected_tickers'] = st.session_state['selected_tickers']
        if 'metric_categories' in st.session_state:
            context['metric_categories'] = st.session_state['metric_categories']
        if 'yahoo_data' in st.session_state:
            context['yahoo_data'] = st.session_state['yahoo_data']
        if 'economic_data' in st.session_state:
            context['economic_data'] = st.session_state['economic_data']
        return context
    
    def _render_quick_actions(self):
        st.markdown("### 🚀 Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Company Overview"):
                self._quick_company_overview()
        
        with col2:
            if st.button("📈 Market Analysis"):
                self._quick_market_analysis()
        
        with col3:
            if st.button("💡 Investment Ideas"):
                self._quick_investment_ideas()
        
        with col4:
            if st.button("🏭 Sector Analysis"):
                self._quick_sector_analysis()

    def _quick_action_chat(self, prompt: str):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Generating analysis..."):
                response = self._generate_response(prompt)
                st.markdown(response)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})

    def _quick_company_overview(self):
        if not st.session_state.get('selected_tickers'):
            st.warning("Please select one or more companies first.")
            return
        tickers = st.session_state['selected_tickers']
        prompt = f"Provide a comprehensive overview of {tickers[0]} including business model, financial health, and key metrics."
        if len(tickers) > 1:
            prompt = f"Provide a comprehensive comparison of {', '.join(tickers)} including business models, financial health, key metrics, and competitive analysis."
        self._quick_action_chat(prompt)

    def _quick_market_analysis(self):
        prompt = "Analyze current market conditions and provide insights on key economic indicators and market trends."
        if st.session_state.get('selected_tickers'):
            prompt += f" How do these conditions affect {', '.join(st.session_state['selected_tickers'])}?"
        self._quick_action_chat(prompt)

    def _quick_investment_ideas(self):
        prompt = "Based on available data, suggest potential investment opportunities and explain the reasoning behind each recommendation."
        if st.session_state.get('selected_tickers'):
            prompt = f"Based on the analysis of {', '.join(st.session_state['selected_tickers'])} and available market data, suggest potential investment opportunities and explain the reasoning behind each recommendation. Include risk assessment and sector-specific insights."
        self._quick_action_chat(prompt)

    def _quick_sector_analysis(self):
        if not st.session_state.get('selected_tickers'):
            st.warning("Please select one or more companies first.")
            return
        tickers = st.session_state['selected_tickers']
        prompt = f"Analyze the sector performance and industry trends for {', '.join(tickers)} and provide insights on sector-specific opportunities and risks."
        self._quick_action_chat(prompt)

# --- Module-level functions for Streamlit --- #
chatbot_interface = ChatbotInterface()

def render_filters(all_tickers):
    chatbot_interface.render_filters(all_tickers)

def render_content():
    chatbot_interface.render_content()