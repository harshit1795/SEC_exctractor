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
            
            # Fetch multiple data types
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
    
    def get_sec_filing_data(self, ticker: str) -> Dict[str, Any]:
        """Get SEC filing data from local storage"""
        cache_key = f"sec_{ticker}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            data_dir = Path("data") / ticker
            if not data_dir.exists():
                return {}
            
            filings = {}
            for file_path in data_dir.glob("*.htm"):
                year = file_path.stem.split('-')[-1] if '-' in file_path.stem else file_path.stem
                filings[year] = {
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                }
            
            data = {'filings': filings, 'ticker': ticker}
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching SEC data for {ticker}: {e}")
            return {}
    
    def get_fundamentals_data(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """Get fundamentals data from parquet file"""
        cache_key = "fundamentals"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            if Path("fundamentals_tall.parquet").exists():
                df = pd.read_parquet("fundamentals_tall.parquet")
                if ticker:
                    df = df[df['Ticker'] == ticker]
                self._cache_data(cache_key, df)
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading fundamentals data: {e}")
            return pd.DataFrame()
    
    def get_available_tickers(self) -> List[str]:
        """Get list of available tickers from data directory"""
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
        """Build user prompt with context data"""
        
        prompt_parts = [f"User Question: {user_question}\n"]
        
        # Add available data sources
        if context_data.get('available_tickers'):
            prompt_parts.append(f"Available Companies: {', '.join(context_data['available_tickers'])}\n")
        
        # Add specific company data if available
        if context_data.get('selected_tickers'):
            tickers = context_data['selected_tickers']
            prompt_parts.append(f"Selected Companies: {', '.join(tickers)}\n")
            
            # Add selected metric categories
            if context_data.get('metric_categories'):
                prompt_parts.append(f"Selected Metrics: {', '.join(context_data['metric_categories'])}\n")
            
            # Add Yahoo Finance data for all companies
            if context_data.get('yahoo_data'):
                yf_data = context_data['yahoo_data']
                for ticker, data in yf_data.items():
                    if data.get('info'):
                        company_name = data['info'].get('longName', ticker)
                        sector = data['info'].get('sector', 'N/A')
                        prompt_parts.append(f"Company {ticker} ({company_name}): {sector}\n")
                        
                        if data.get('longBusinessSummary'):
                            prompt_parts.append(f"  Business: {data['longBusinessSummary'][:200]}...\n")
                        
                        # Show available metrics based on selection
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
        
        # Add economic data if available
        if context_data.get('economic_data') is not None:
            prompt_parts.append("Economic Data Available: FRED economic indicators\n")
        
        # Add fundamentals data if available
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
        """Initialize AI model with API keys"""
        try:
            load_api_keys()
            # Get API key from environment or session state
            api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
            if api_key:
                self.analyzer = FinancialAnalyzer(api_key)
            else:
                st.warning("Google API key not found. Please configure it in your environment or secrets.")
        except Exception as e:
            logger.error(f"Error initializing AI: {e}")
            st.error(f"Failed to initialize AI model: {e}")
    
    def render(self):
        """Render the chatbot interface"""
        st.markdown("## 🤖 FinQ Financial Assistant")
        st.markdown("Ask me anything about financial data, company analysis, or market insights!")
        
        # Data source selection
        self._render_data_source_selector()
        
        # Chat interface
        self._render_chat_interface()
        
        # Quick actions
        self._render_quick_actions()
    
    def _render_data_source_selector(self):
        """Render data source selection interface"""
        with st.expander("🔍 Data Sources & Context", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Company selection
                available_tickers = self.data_manager.get_available_tickers()
                selected_tickers = st.multiselect(
                    "Select Companies for Context:",
                    options=available_tickers,
                    default=[],
                    help="Select one or more companies to analyze. You can compare multiple companies or analyze sector performance."
                )
                
                if selected_tickers:
                    st.session_state['selected_tickers'] = selected_tickers
                    
                    # Metric category selection
                    st.markdown("**📊 Financial Metrics**")
                    metric_categories = st.multiselect(
                        "Select Metric Categories:",
                        options=[
                            "Income Statement",
                            "Balance Sheet", 
                            "Cash Flow",
                            "Stock Price & Volume",
                            "Earnings & Estimates",
                            "Valuation Metrics",
                            "Technical Indicators"
                        ],
                        default=["Income Statement", "Balance Sheet"],
                        help="Choose which financial metrics to include in your analysis. More categories provide richer analysis but may take longer to load."
                    )
                    
                    if metric_categories:
                        st.session_state['metric_categories'] = metric_categories
                        
                        # Load company data for all selected tickers
                        if st.button("Load Company Data"):
                            with st.spinner(f"Loading {', '.join(metric_categories)} data for {len(selected_tickers)} companies..."):
                                all_yahoo_data = {}
                                for ticker in selected_tickers:
                                    yahoo_data = self.data_manager.get_yahoo_finance_data(ticker)
                                    all_yahoo_data[ticker] = yahoo_data
                                
                                st.session_state['yahoo_data'] = all_yahoo_data
                                st.success(f"Loaded {', '.join(metric_categories)} data for {len(selected_tickers)} companies: {', '.join(selected_tickers)}")
                                
                                # Show data summary with selected metrics
                                with st.expander("📊 Data Summary", expanded=False):
                                    for ticker, data in all_yahoo_data.items():
                                        if data.get('info'):
                                            company_name = data['info'].get('longName', ticker)
                                            sector = data['info'].get('sector', 'N/A')
                                            market_cap = data['info'].get('marketCap', 'N/A')
                                            if market_cap and market_cap != 'N/A':
                                                market_cap = f"${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else str(market_cap)
                                            
                                            st.write(f"**{ticker}** ({company_name}) - {sector} - Market Cap: {market_cap}")
                                            
                                            # Show available metrics for this company
                                            available_metrics = []
                                            if "Income Statement" in metric_categories and data.get('financials') is not None:
                                                available_metrics.append("Income Statement")
                                            if "Balance Sheet" in metric_categories and data.get('balance_sheet') is not None:
                                                available_metrics.append("Balance Sheet")
                                            if "Cash Flow" in metric_categories and data.get('cashflow') is not None:
                                                available_metrics.append("Cash Flow")
                                            if "Stock Price & Volume" in metric_categories and data.get('history') is not None:
                                                available_metrics.append("Stock Price & Volume")
                                            if "Earnings & Estimates" in metric_categories and data.get('earnings') is not None:
                                                available_metrics.append("Earnings & Estimates")
                                            
                                            if available_metrics:
                                                st.write(f"  📈 Available: {', '.join(available_metrics)}")
            
            with col2:
                # Economic indicators
                st.markdown("**Economic Indicators**")
                fred_series = st.multiselect(
                    "Select FRED series:",
                    options=["GDP", "UNRATE", "CPIAUCSL", "DGS10", "FEDFUNDS"],
                    default=["GDP", "UNRATE"]
                )
                
                if fred_series and st.button("Load Economic Data"):
                    with st.spinner("Loading economic data..."):
                        end_date = datetime.now().strftime('%Y-%m-%d')
                        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                        economic_data = self.data_manager.get_fred_economic_data(
                            fred_series, start_date, end_date
                        )
                        st.session_state['economic_data'] = economic_data
                        st.success("Economic data loaded!")
    
    def _render_chat_interface(self):
        """Render the main chat interface"""
        # Initialize chat history
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        # Display chat history
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask me about financial data, company analysis, or market insights..."):
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

                # Generate and display response
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        response = self._generate_response(prompt)
                        st.markdown(response)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    def _generate_response(self, prompt: str) -> str:
        """Generate AI response based on user prompt and available data"""
        if not self.analyzer:
            return "AI model not initialized. Please check your API configuration."
        
        try:
            # Gather context data
            context_data = self._gather_context_data()
            
            # Generate analysis
            response = self.analyzer.analyze_financial_data(prompt, context_data)
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _gather_context_data(self) -> Dict[str, Any]:
        """Gather all available context data"""
        context = {}
        
        # Multiple ticker context
        if 'selected_tickers' in st.session_state:
            context['selected_tickers'] = st.session_state['selected_tickers']
            
            # Metric categories
            if 'metric_categories' in st.session_state:
                context['metric_categories'] = st.session_state['metric_categories']
            
            # Yahoo Finance data for all selected tickers
            if 'yahoo_data' in st.session_state:
                context['yahoo_data'] = st.session_state['yahoo_data']
        
        # Economic data
        if 'economic_data' in st.session_state:
            context['economic_data'] = st.session_state['economic_data']
        
        # Fundamentals data for all selected tickers
        if 'selected_tickers' in st.session_state:
            all_fundamentals = []
            for ticker in st.session_state['selected_tickers']:
                fundamentals = self.data_manager.get_fundamentals_data(ticker)
                if not fundamentals.empty:
                    all_fundamentals.append(fundamentals)
            
            if all_fundamentals:
                context['fundamentals_data'] = pd.concat(all_fundamentals, ignore_index=True)
        
        # Available tickers
        context['available_tickers'] = self.data_manager.get_available_tickers()
        
        return context
    
    def _render_quick_actions(self):
        """Render quick action buttons"""
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
        """Generate quick company overview"""
        if 'selected_tickers' not in st.session_state or not st.session_state['selected_tickers']:
            st.warning("Please select one or more companies first.")
            return
        
        tickers = st.session_state['selected_tickers']
        if len(tickers) == 1:
            prompt = f"Provide a comprehensive overview of {tickers[0]} including business model, financial health, and key metrics."
        else:
            prompt = f"Provide a comprehensive comparison of {', '.join(tickers)} including business models, financial health, key metrics, and competitive analysis."
        
        self._add_quick_action_to_chat(prompt)
    
    def _quick_market_analysis(self):
        """Generate quick market analysis"""
        if 'selected_tickers' in st.session_state and st.session_state['selected_tickers']:
            tickers = st.session_state['selected_tickers']
            prompt = f"Analyze current market conditions and provide insights on how they affect {', '.join(tickers)} and their sectors. Include analysis of key economic indicators and market trends."
        else:
            prompt = "Analyze current market conditions and provide insights on key economic indicators and market trends."
        
        self._add_quick_action_to_chat(prompt)
    
    def _quick_investment_ideas(self):
        """Generate quick investment ideas"""
        if 'selected_tickers' in st.session_state and st.session_state['selected_tickers']:
            tickers = st.session_state['selected_tickers']
            prompt = f"Based on the analysis of {', '.join(tickers)} and available market data, suggest potential investment opportunities and explain the reasoning behind each recommendation. Include risk assessment and sector-specific insights."
        else:
            prompt = "Based on available data, suggest potential investment opportunities and explain the reasoning behind each recommendation."
        
        self._add_quick_action_to_chat(prompt)
    
    def _quick_sector_analysis(self):
        """Generate quick sector analysis"""
        if 'selected_tickers' not in st.session_state or not st.session_state['selected_tickers']:
            st.warning("Please select one or more companies first.")
            return
        
        tickers = st.session_state['selected_tickers']
        if len(tickers) == 1:
            prompt = f"Analyze the sector performance and industry trends for {tickers[0]} and provide insights on sector-specific opportunities and risks."
        else:
            prompt = f"Provide a comprehensive sector analysis comparing {', '.join(tickers)}, including industry trends, competitive landscape, and sector-specific investment opportunities."
        
        self._add_quick_action_to_chat(prompt)

    def _add_quick_action_to_chat(self, prompt: str):
        """Add quick action to chat and generate response"""
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Generating analysis..."):
                    context_data = self._gather_context_data()
                    response = self.analyzer.analyze_financial_data(prompt, context_data)
                    st.markdown(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})

def render():
    """Main render function for the chatbot tab"""
    try:
        chatbot = ChatbotInterface()
        chatbot.render()
    except Exception as e:
        logger.error(f"Error rendering chatbot: {e}")
        st.error(f"Failed to load chatbot: {e}")
        st.exception(e)