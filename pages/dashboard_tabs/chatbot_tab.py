
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

from auth import load_api_keys, _load_user_prefs, _save_user_prefs
from fred_data import get_fred_series, get_multiple_fred_series

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceManager:
    """MCP-style data source manager for accessing financial data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    def _is_cache_valid(self, key: str) -> bool:
        if key not in self.cache:
            return False
        cache_time, _ = self.cache[key]
        return (datetime.now() - cache_time).seconds < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any) -> None:
        self.cache[key] = (datetime.now(), data)
    
    def get_yahoo_finance_data(self, ticker: str, period: str = "1y") -> Dict[str, Any]:
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
    
    def get_available_tickers(self) -> List[str]:
        try:
            data_dir = Path("data")
            if data_dir.exists():
                return [d.name for d in data_dir.iterdir() if d.is_dir()]
            return []
        except Exception as e:
            logger.error(f"Error getting available tickers: {e}")
            return []

class FinancialAnalyzer:
    """AI-powered financial analysis engine"""
    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.api_key = api_key
        
    def analyze_financial_data(self, user_question: str, context_data: Dict[str, Any]) -> str:
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(user_question, context_data)
        try:
            response = self.model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            return response.text
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return f"I apologize, but I encountered an error while analyzing the data: {str(e)}"
    
    def _build_system_prompt(self) -> str:
        return """You are FinQ, an expert financial analyst AI assistant with deep knowledge of:
- Financial statement analysis (Income Statement, Balance Sheet, Cash Flow)
- Market analysis and stock valuation
- Economic indicators and macroeconomic trends
- SEC filings and regulatory compliance
- Risk assessment and financial modeling

Your capabilities:
1. Analyze financial data from multiple sources (Yahoo Finance, FRED, SEC filings)
2. Provide insights on trends, ratios, and financial health
3. Compare companies and sectors
4. Identify risks and opportunities
5. Explain complex financial concepts in simple terms
6. Make data-driven recommendations

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
        prompt_parts = [f"User Question: {user_question}\n"]
        if context_data.get('available_tickers'):
            prompt_parts.append(f"Available Companies: {', '.join(context_data['available_tickers'])}\n")
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
                        prompt_parts.append(f"  Company {ticker} ({company_name}): {sector}\n")
                        if data.get('longBusinessSummary'):
                            prompt_parts.append(f"  Business: {data['longBusinessSummary'][:200]}...\n")
                        available_metrics = []
                        if "Income Statement" in context_data.get('metric_categories', []) and data.get('financials') is not None:
                            available_metrics.append("Income Statement")
                        if "Balance Sheet" in context_data.get('metric_categories', []) and data.get('balance_sheet') is not None:
                            available_metrics.append("Balance Sheet")
                        if "Cash Flow" in context_data.get('metric_categories', []) and data.get('cashflow') is not None:
                            available_metrics.append("Cash Flow")
                        if "Stock Price & Volume" in context_data.get('metric_categories', []) and data.get('history') is not None:
                            available_metrics.append("Stock Price & Volume")
                        if "Earnings & Estimates" in context_data.get('metric_categories', []) and data.get('earnings') is not None:
                            available_metrics.append("Earnings & Estimates")
                        if available_metrics:
                            prompt_parts.append(f"  Available Metrics: {', '.join(available_metrics)}\n")
                        if "Stock Price & Volume" in context_data.get('metric_categories', []) and data.get('history') is not None:
                            hist_data = data['history']
                            if not hist_data.empty:
                                latest_price = hist_data['Close'].iloc[-1]
                                prompt_parts.append(f"  Latest Price: ${latest_price:.2f}\n")
        if context_data.get('economic_data') is not None:
            prompt_parts.append("Economic Data Available: FRED economic indicators\n")
        if context_data.get('fundamentals_data') is not None:
            prompt_parts.append("Fundamentals Data Available: Historical financial metrics\n")
        prompt_parts.append("\nPlease provide a comprehensive analysis based on the available data.")
        return "\n".join(prompt_parts)

class ChatbotInterface:
    """Streamlit-based chatbot interface"""
    
    def __init__(self):
        self.data_manager = DataSourceManager()
        self.analyzer = None
        self.initialize_ai()
    
    def initialize_ai(self):
        try:
            load_api_keys()
            api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
            if api_key:
                self.analyzer = FinancialAnalyzer(api_key)
        except Exception as e:
            logger.error(f"Error initializing AI: {e}")

    def render_filters(self):
        """Render data source selection interface"""
        st.markdown("#### Chat Context Options")
        user_prefs = st.session_state.get("user_prefs", {})
        chatbot_prefs = user_prefs.get("chatbot_tab", {})

        col1, col2 = st.columns(2)
        with col1:
            available_tickers = self.data_manager.get_available_tickers()
            default_tickers = chatbot_prefs.get("selected_tickers", [])
            selected_tickers = st.multiselect("Select Companies for Context:", options=available_tickers, default=default_tickers)
            
            if selected_tickers:
                default_metrics = chatbot_prefs.get("metric_categories", ["Income Statement", "Balance Sheet"])
                metric_categories = st.multiselect("Select Metric Categories:", options=["Income Statement", "Balance Sheet", "Cash Flow", "Stock Price & Volume", "Earnings & Estimates"], default=default_metrics)
                
                if st.button("Load Company Data"):
                    with st.spinner(f"Loading data for {len(selected_tickers)} companies..."):
                        all_yahoo_data = {}
                        for ticker in selected_tickers:
                            all_yahoo_data[ticker] = self.data_manager.get_yahoo_finance_data(ticker)
                        st.session_state['yahoo_data'] = all_yahoo_data
                        st.success(f"Loaded data for: {', '.join(selected_tickers)}")
        with col2:
            st.markdown("**Economic Indicators**")
            fred_options = ["GDP", "UNRATE", "CPIAUCSL", "DGS10", "FEDFUNDS"]
            default_fred = chatbot_prefs.get("fred_series", ["GDP", "UNRATE"])
            fred_series = st.multiselect("Select FRED series:", options=fred_options, default=default_fred)
            
            if fred_series and st.button("Load Economic Data"):
                with st.spinner("Loading economic data..."):
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                    st.session_state['economic_data'] = self.data_manager.get_fred_economic_data(fred_series, start_date, end_date)
                    st.success("Economic data loaded!")

        if st.button("Save Chat Context", key="save_chat_prefs"):
            all_prefs = _load_user_prefs()
            user = st.session_state.get("user")
            if user:
                user_prefs = all_prefs.setdefault(user, {})
                user_prefs["chatbot_tab"] = {
                    "selected_tickers": selected_tickers,
                    "metric_categories": metric_categories if selected_tickers else [],
                    "fred_series": fred_series
                }
                _save_user_prefs(all_prefs)
                st.session_state.user_prefs = user_prefs
                st.success("Chat context preferences saved!")

    def render_content(self):
        """Render the main chatbot interface"""
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
        if prompt := st.chat_input("Ask me about financial data..."):
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
            return self.analyzer.analyze_financial_data(prompt, context_data)
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
        if 'selected_tickers' in st.session_state:
            all_fundamentals = []
            for ticker in st.session_state['selected_tickers']:
                fundamentals = self.data_manager.get_fundamentals_data(ticker)
                if not fundamentals.empty:
                    all_fundamentals.append(fundamentals)
            if all_fundamentals:
                context['fundamentals_data'] = pd.concat(all_fundamentals, ignore_index=True)
        context['available_tickers'] = self.data_manager.get_available_tickers()
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
    
    def _quick_company_overview(self):
        if 'selected_tickers' not in st.session_state or not st.session_state['selected_tickers']:
            st.warning("Please select one or more companies first.")
            return
        tickers = st.session_state['selected_tickers']
        prompt = f"Provide a comprehensive overview of {tickers[0]}." if len(tickers) == 1 else f"Provide a comprehensive comparison of {', '.join(tickers)}."
        self._add_quick_action_to_chat(prompt)
    
    def _quick_market_analysis(self):
        tickers_prompt = f" for {', '.join(st.session_state['selected_tickers'])}" if 'selected_tickers' in st.session_state and st.session_state['selected_tickers'] else ""
        prompt = f"Analyze current market conditions and provide insights on how they affect the market{tickers_prompt}."
        self._add_quick_action_to_chat(prompt)
    
    def _quick_investment_ideas(self):
        tickers_prompt = f" for {', '.join(st.session_state['selected_tickers'])}" if 'selected_tickers' in st.session_state and st.session_state['selected_tickers'] else ""
        prompt = f"Based on the analysis of the market{tickers_prompt}, suggest potential investment opportunities."
        self._add_quick_action_to_chat(prompt)
    
    def _quick_sector_analysis(self):
        if 'selected_tickers' not in st.session_state or not st.session_state['selected_tickers']:
            st.warning("Please select one or more companies first.")
            return
        tickers = st.session_state['selected_tickers']
        prompt = f"Analyze the sector performance and industry trends for {tickers[0]}." if len(tickers) == 1 else f"Provide a comprehensive sector analysis comparing {', '.join(tickers)}."
        self._add_quick_action_to_chat(prompt)

    def _add_quick_action_to_chat(self, prompt: str):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Generating analysis..."):
                    context_data = self._gather_context_data()
                    response = self.analyzer.analyze_financial_data(prompt, context_data)
                    st.markdown(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
