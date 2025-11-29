"""
DataSourceManager Service
Migrated from Streamlit chatbot_tab.py

This service provides unified access to multiple financial data sources:
- Yahoo Finance
- FRED Economic Data
- SEC Filings
- Fundamentals Data
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import yfinance as yf
from app.config import settings
from app.services.fred_service import get_multiple_fred_series
from app.services.sec_service import (
    load_cik_ticker_map,
    get_company_filings,
    get_latest_10k_filing_info,
    get_latest_10q_filing_info,
    download_filing_html,
    parse_10k_sections,
    parse_10q_sections
)

logger = logging.getLogger(__name__)


class DataSourceManager:
    """
    MCP-style data source manager for accessing financial data.
    Migrated from Streamlit with async support added.
    """
    
    def __init__(self, cik_df: Optional[pd.DataFrame] = None):
        self.cache: Dict[str, tuple] = {}
        self.cache_ttl = settings.cache_ttl  # 5 minutes default
        self.cik_df = cik_df
        
        # Load CIK mapping if not provided
        if self.cik_df is None or self.cik_df.empty:
            try:
                # Try default path first, then fallback paths
                self.cik_df = load_cik_ticker_map(settings.cik_map_path)
                if self.cik_df.empty:
                    # Try alternative paths
                    logger.info(f"CIK map not found at {settings.cik_map_path}, trying alternative paths...")
                    for alt_path in ["../company_tickers.json", "../secedgarticker.json"]:
                        self.cik_df = load_cik_ticker_map(alt_path)
                        if not self.cik_df.empty:
                            logger.info(f"Successfully loaded CIK map from {alt_path}")
                            break
                    
                    if self.cik_df.empty:
                        logger.warning(f"CIK map is empty or not found. Tried: {settings.cik_map_path}, ../company_tickers.json, ../secedgarticker.json")
            except Exception as e:
                logger.error(f"Error loading CIK map: {e}", exc_info=True)
                self.cik_df = pd.DataFrame()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        cache_time, _ = self.cache[key]
        return (datetime.now() - cache_time).seconds < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        self.cache[key] = (datetime.now(), data)
    
    def clear_cache(self, key_pattern: Optional[str] = None) -> None:
        """
        Clear cache entries
        
        Args:
            key_pattern: Optional pattern to match cache keys (e.g., 'fundamentals_GOOGL')
                        If None, clears all cache
        """
        if key_pattern:
            keys_to_remove = [k for k in self.cache.keys() if key_pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"Cleared {len(keys_to_remove)} cache entries matching '{key_pattern}'")
        else:
            self.cache.clear()
            logger.info("Cleared all cache entries")
    
    async def get_yahoo_finance_data(self, ticker: str, period: str = "1y") -> Dict[str, Any]:
        """
        Fetch comprehensive data from Yahoo Finance
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            Dictionary with financial data
        """
        cache_key = f"yf_{ticker}_{period}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            ticker_obj = yf.Ticker(ticker)
            
            # Fetch multiple data types
            # Note: Some of these are DataFrames, we'll convert to dict for JSON serialization
            history_df = ticker_obj.history(period=period)
            
            # Get earnings dates
            earnings_dates = ticker_obj.earnings_dates
            earnings_data = []
            if earnings_dates is not None and not earnings_dates.empty:
                earnings_dates_reset = earnings_dates.reset_index()
                earnings_data = earnings_dates_reset.to_dict('records')
            
            # Convert history_df to records with Date field
            history_records = []
            if not history_df.empty:
                history_df_reset = history_df.reset_index()
                history_df_reset.rename(columns={'Date': 'Date'}, inplace=True)
                history_records = history_df_reset.to_dict('records')
            
            data = {
                'info': ticker_obj.info,
                'financials': ticker_obj.financials.to_dict() if not ticker_obj.financials.empty else {},
                'balance_sheet': ticker_obj.balance_sheet.to_dict() if not ticker_obj.balance_sheet.empty else {},
                'cashflow': ticker_obj.cashflow.to_dict() if not ticker_obj.cashflow.empty else {},
                'quarterly_financials': ticker_obj.quarterly_financials.to_dict() if not ticker_obj.quarterly_financials.empty else {},
                'quarterly_balance_sheet': ticker_obj.quarterly_balance_sheet.to_dict() if not ticker_obj.quarterly_balance_sheet.empty else {},
                'quarterly_cashflow': ticker_obj.quarterly_cashflow.to_dict() if not ticker_obj.quarterly_cashflow.empty else {},
                'history': history_df.to_dict() if not history_df.empty else {},
                'history_df': history_records,  # Records with Date field included
                'recommendations': ticker_obj.recommendations.to_dict() if ticker_obj.recommendations is not None and not ticker_obj.recommendations.empty else {},
                'earnings_dates': earnings_data,
            }
            
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {ticker}: {e}")
            return {}
    
    async def get_fred_economic_data(
        self, 
        series_ids: List[str], 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch economic data from FRED
        
        Args:
            series_ids: List of FRED series IDs
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with economic data
        """
        cache_key = f"fred_{'_'.join(series_ids)}_{start_date}_{end_date}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            # Convert list to dict format expected by get_multiple_fred_series
            # If no frequency specified, use None (default)
            series_info = {sid: None for sid in series_ids}
            data = get_multiple_fred_series(series_info, start_date, end_date)
            
            if data.empty:
                logger.warning(f"FRED data is empty for series: {series_ids}, date range: {start_date} to {end_date}")
                # Don't cache empty data
                return data
            
            self._cache_data(cache_key, data)
            return data
        except ValueError as e:
            # FRED_API_KEY not configured or authentication error
            logger.error(f"FRED API key error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching FRED data: {e}", exc_info=True)
            raise
    
    async def get_sec_filing_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get SEC filing metadata from SEC EDGAR API
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with filing metadata including latest 10-K and 10-Q info
        """
        cache_key = f"sec_{ticker}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            if self.cik_df.empty:
                logger.warning(f"No CIK information available for {ticker}. CIK map may not be loaded.")
                return {'filings': {}, 'ticker': ticker, 'error': 'CIK map not available'}
            
            company_info = self.cik_df[self.cik_df['ticker'] == ticker.upper()]
            if company_info.empty:
                logger.warning(f"No CIK information found for {ticker}. Available tickers: {self.cik_df['ticker'].head(10).tolist() if not self.cik_df.empty else 'none'}")
                return {'filings': {}, 'ticker': ticker, 'error': f'Ticker {ticker} not found in CIK map'}
            
            cik = company_info.iloc[0]['cik']
            logger.info(f"Found CIK {cik} for ticker {ticker}")
            
            filings_df = get_company_filings(cik)
            
            if filings_df.empty:
                logger.warning(f"No recent filings found for {ticker} (CIK: {cik})")
                return {'filings': {}, 'ticker': ticker, 'error': 'No filings found from SEC API'}
            
            logger.info(f"Found {len(filings_df)} filings for {ticker}")
            
            # Get latest 10-K and 10-Q filing info
            filings_metadata = {}
            
            latest_10k = get_latest_10k_filing_info(ticker, cik, filings_df)
            if latest_10k:
                logger.info(f"Found latest 10-K for {ticker}: {latest_10k.get('filingDate')}")
                filings_metadata['10-k'] = latest_10k
            else:
                logger.info(f"No 10-K filings found for {ticker}")
            
            latest_10q = get_latest_10q_filing_info(ticker, cik, filings_df)
            if latest_10q:
                logger.info(f"Found latest 10-Q for {ticker}: {latest_10q.get('filingDate')}")
                filings_metadata['10-q'] = latest_10q
            else:
                logger.info(f"No 10-Q filings found for {ticker}")
            
            data = {'filings': filings_metadata, 'ticker': ticker}
            self._cache_data(cache_key, data)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching SEC filing data for {ticker}: {e}", exc_info=True)
            return {'filings': {}, 'ticker': ticker, 'error': str(e)}
    
    async def get_10k_section_data(self, ticker: str, sections: List[str]) -> Dict[str, str]:
        """
        Fetches and parses key sections from the latest 10-K filing.
        
        Args:
            ticker: Stock ticker symbol
            sections: List of sections to fetch (e.g., ['business', 'risk', 'mda'])
        
        Returns:
            Dictionary mapping section names to text content
        """
        cache_key = f"10k_{ticker}_{'_'.join(sections)}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]

        try:
            if self.cik_df.empty:
                logger.warning(f"No CIK information available for {ticker}")
                return {}
            
            company_info = self.cik_df[self.cik_df['ticker'] == ticker.upper()]
            if company_info.empty:
                logger.warning(f"No CIK information found for {ticker}")
                return {}
            
            cik = company_info.iloc[0]['cik']
            filings_df = get_company_filings(cik)
            if filings_df.empty:
                logger.warning(f"No recent filings found for {ticker}")
                return {}

            latest_10k_info = get_latest_10k_filing_info(ticker, cik, filings_df)
            if not latest_10k_info:
                logger.warning(f"No 10-K filings found for {ticker}")
                return {}

            html_content = download_filing_html(latest_10k_info['doc_url'])
            if not html_content:
                logger.error(f"Could not download 10-K HTML for {ticker}")
                return {}

            business_text, risk_text, mda_text = parse_10k_sections(html_content)
            
            section_data = {}
            if "business" in sections:
                section_data["Business Overview (Item 1)"] = business_text
            if "risk" in sections:
                section_data["Risk Factors (Item 1A)"] = risk_text
            if "mda" in sections:
                section_data["Management's Discussion & Analysis (Item 7)"] = mda_text
            
            self._cache_data(cache_key, section_data)
            return section_data

        except Exception as e:
            logger.error(f"Error fetching or parsing 10-K data for {ticker}: {e}")
            return {}

    async def get_10q_section_data(self, ticker: str, sections: List[str]) -> Dict[str, str]:
        """
        Fetches and parses key sections from the latest 10-Q filing.
        
        Args:
            ticker: Stock ticker symbol
            sections: List of sections to fetch (e.g., ['risk', 'mda'])
        
        Returns:
            Dictionary mapping section names to text content
        """
        cache_key = f"10q_{ticker}_{'_'.join(sections)}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]

        try:
            if self.cik_df.empty:
                logger.warning(f"No CIK information available for {ticker}")
                return {}
            
            company_info = self.cik_df[self.cik_df['ticker'] == ticker.upper()]
            if company_info.empty:
                logger.warning(f"No CIK information found for {ticker}")
                return {}
            
            cik = company_info.iloc[0]['cik']
            filings_df = get_company_filings(cik)
            if filings_df.empty:
                logger.warning(f"No recent filings found for {ticker}")
                return {}

            latest_10q_info = get_latest_10q_filing_info(ticker, cik, filings_df)
            if not latest_10q_info:
                logger.warning(f"No 10-Q filings found for {ticker}")
                return {}

            html_content = download_filing_html(latest_10q_info['doc_url'])
            if not html_content:
                logger.error(f"Could not download 10-Q HTML for {ticker}")
                return {}

            risk_text, mda_text = parse_10q_sections(html_content)
            
            section_data = {}
            if "risk" in sections:
                section_data["Risk Factors (Part II, Item 1A)"] = risk_text
            if "mda" in sections:
                section_data["Management's Discussion & Analysis (Part I, Item 2)"] = mda_text
            
            self._cache_data(cache_key, section_data)
            return section_data

        except Exception as e:
            logger.error(f"Error fetching or parsing 10-Q data for {ticker}: {e}")
            return {}

    async def get_fundamentals_data(self, ticker: str) -> pd.DataFrame:
        """
        Get fundamentals data from parquet file
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            DataFrame with fundamentals data
        """
        cache_key = f"fundamentals_{ticker}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][1]
        
        try:
            # Try multiple possible paths
            # Railway runs from finq-backend/, so check current directory first
            possible_paths = [
                Path("fundamentals_tall.parquet"),  # Current directory (finq-backend/)
                Path(settings.fundamentals_path),
                Path(__file__).parent.parent.parent.parent / settings.fundamentals_path,
                Path(__file__).parent.parent.parent.parent / "fundamentals_tall.parquet",
                Path("../fundamentals_tall.parquet"),
            ]
            
            fundamentals_path = None
            for path in possible_paths:
                if path.exists():
                    fundamentals_path = path
                    break
            
            if not fundamentals_path:
                logger.warning(f"Fundamentals file not found. Tried: {possible_paths}")
                return pd.DataFrame()
            
            logger.info(f"Loading fundamentals from {fundamentals_path}")
            df = pd.read_parquet(fundamentals_path)
            
            # Try different column name variations
            ticker_col = None
            for col in ['ticker', 'Ticker', 'TICKER']:
                if col in df.columns:
                    ticker_col = col
                    break
            
            if ticker_col:
                ticker_data = df[df[ticker_col].str.upper() == ticker.upper()].copy()
                logger.info(f"Found {len(ticker_data)} rows for ticker {ticker}")
                
                # Sort by FiscalPeriod to ensure latest data is first
                # Try different column name variations for period
                period_col = None
                for col in ['FiscalPeriod', 'fiscalPeriod', 'Period', 'period', 'Date', 'date']:
                    if col in ticker_data.columns:
                        period_col = col
                        break
                
                if period_col:
                    # Sort by period (descending - latest first)
                    # Handle period formats like "2025 Q3", "2024 Q4", etc.
                    def parse_period(period_str):
                        """Parse period string to sortable tuple (year, quarter)"""
                        try:
                            if pd.isna(period_str):
                                return (0, 0)
                            period_str = str(period_str).strip()
                            # Handle formats like "2025 Q3", "2025Q3", "2025-03", etc.
                            if 'Q' in period_str.upper():
                                parts = period_str.upper().split('Q')
                                year = int(parts[0].strip())
                                quarter = int(parts[1].strip()) if len(parts) > 1 else 0
                                return (year, quarter)
                            elif '-' in period_str:
                                # Handle "2025-03" format
                                parts = period_str.split('-')
                                year = int(parts[0])
                                quarter = int(parts[1]) // 3 if len(parts) > 1 else 0
                                return (year, quarter)
                            else:
                                # Try to parse as year
                                year = int(period_str[:4]) if len(period_str) >= 4 else 0
                                return (year, 0)
                        except:
                            return (0, 0)
                    
                    # Add a temporary sort column
                    ticker_data['_sort_period'] = ticker_data[period_col].apply(parse_period)
                    ticker_data = ticker_data.sort_values('_sort_period', ascending=False)
                    ticker_data = ticker_data.drop('_sort_period', axis=1)
                    logger.info(f"Sorted fundamentals data by {period_col} (latest first)")
            else:
                logger.warning("No ticker column found in fundamentals data")
                ticker_data = pd.DataFrame()
            
            self._cache_data(cache_key, ticker_data)
            return ticker_data
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals data for {ticker}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def get_available_tickers(self) -> List[str]:
        """
        Get list of available tickers from fundamentals data or data directory
        
        Returns:
            List of ticker symbols
        """
        try:
            # Try fundamentals file first (check multiple possible paths)
            possible_paths = [
                Path(settings.fundamentals_path),
                Path(__file__).parent.parent.parent.parent / settings.fundamentals_path,
                Path(__file__).parent.parent.parent.parent / "fundamentals_tall.parquet",
                Path("../fundamentals_tall.parquet"),
            ]
            
            for fundamentals_path in possible_paths:
                if fundamentals_path.exists():
                    try:
                        df = pd.read_parquet(fundamentals_path)
                        # Try different column name variations
                        for col in ['ticker', 'Ticker', 'TICKER']:
                            if col in df.columns:
                                tickers = sorted(df[col].str.upper().unique().tolist())
                                if tickers:
                                    logger.info(f"Found {len(tickers)} tickers from {fundamentals_path}")
                                    return tickers
                    except Exception as e:
                        logger.warning(f"Error reading {fundamentals_path}: {e}")
                        continue
            
            # Fallback to data directory
            data_dir_paths = [
                Path(settings.data_dir),
                Path(__file__).parent.parent.parent.parent / settings.data_dir,
            ]
            
            for data_dir in data_dir_paths:
                if data_dir.exists():
                    tickers = [d.name for d in data_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
                    if tickers:
                        return sorted(tickers)
            
            # Final fallback: return common S&P 500 tickers
            logger.warning("No tickers found in data files, using fallback list")
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'V', 'JNJ',
                'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'NFLX',
                'PYPL', 'CMCSA', 'XOM', 'VZ', 'CSCO', 'AVGO', 'COST', 'PFE', 'MRK', 'TMO',
                'ABT', 'ACN', 'NKE', 'LIN', 'DHR', 'PM', 'TXN', 'NEE', 'HON', 'QCOM'
            ]
        except Exception as e:
            logger.error(f"Error getting available tickers: {e}")
            # Return fallback list on error
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'V', 'JNJ',
                'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'NFLX'
            ]

