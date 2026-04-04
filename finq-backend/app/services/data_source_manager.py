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
import asyncio
import diskcache as dc
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import yfinance as yf
from app.config import settings
from app.services.fred_service import get_multiple_fred_series
from app.services.sec_service import (
    load_cik_ticker_map,
    lookup_cik_online,
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
    Uses diskcache for persistence across restarts.
    """
    
    def __init__(self, cik_df: Any = None):
        self.cache_dir = settings.cache_dir
        self.cache = dc.Cache(self.cache_dir)
        self.cache_ttl = settings.cache_ttl  # 5 minutes default
        self.cik_df = cik_df if cik_df is not None else pd.DataFrame()
        
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
        """
        Check if cached data is still valid.
        Note: diskcache handles TTL automatically if passed during set(),
        but we keep this for compatibility with existing logic or custom checks.
        """
        return key in self.cache
    
    def _cache_data(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Cache data with configured or specific TTL"""
        expire_time = ttl if ttl is not None else self.cache_ttl
        self.cache.set(key, data, expire=expire_time)
    
    def clear_cache(self, key_pattern: Optional[str] = None) -> None:
        """
        Clear cache entries
        
        Args:
            key_pattern: Optional pattern to match cache keys (e.g., 'fundamentals_GOOGL')
                        If None, clears all cache
        """
        if key_pattern:
            # diskcache doesn't have a direct 'matching' delete, so we iterate
            keys_to_remove = [k for k in self.cache.iterkeys() if isinstance(k, str) and key_pattern in k]
            for key in keys_to_remove:
                self.cache.delete(key)
            logger.info(f"Cleared {len(keys_to_remove)} cache entries matching '{key_pattern}'")
        else:
            self.cache.clear()
            logger.info("Cleared all cache entries")
    
    def _resolve_cik(self, ticker: str) -> Optional[str]:
        """
        Resolve a ticker to its CIK number.
        First tries the local CIK map, then falls back to online SEC EDGAR lookup.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            CIK number as a zero-padded 10-digit string, or None if not found
        """
        # Try local CIK map first
        if not self.cik_df.empty:
            company_info = self.cik_df[self.cik_df['ticker'] == ticker.upper()]
            if not company_info.empty:
                cik = company_info.iloc[0]['cik']
                logger.info(f"Resolved CIK {cik} for {ticker} from local map")
                return cik
        
        # Fallback to online lookup
        logger.info(f"Local CIK map empty or ticker {ticker} not found, trying online lookup...")
        cik = lookup_cik_online(ticker)
        if cik:
            logger.info(f"Resolved CIK {cik} for {ticker} from SEC EDGAR API")
            return cik
        
        logger.warning(f"Could not resolve CIK for ticker {ticker} from any source")
        return None
    
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
            return self.cache[cache_key]
        
        try:
            ticker_obj = yf.Ticker(ticker)
            
            # Fetch multiple data types
            # Note: Some of these are DataFrames, we'll convert to dict for JSON serialization
            try:
                history_df = ticker_obj.history(period=period)
            except Exception as e:
                logger.warning(f"Error fetching history for {ticker}: {e}")
                history_df = pd.DataFrame()
            
            # Get earnings dates
            earnings_data = []
            try:
                earnings_dates = ticker_obj.earnings_dates
                if earnings_dates is not None and not earnings_dates.empty:
                    earnings_dates_reset = earnings_dates.reset_index()
                    raw_records = earnings_dates_reset.to_dict('records')
                    # Convert Timestamp objects to ISO strings for JSON serialization
                    for record in raw_records:
                        clean_record = {}
                        for k, v in record.items():
                            if hasattr(v, 'isoformat'):
                                clean_record[k] = v.isoformat()
                            elif pd.isna(v) if isinstance(v, (float, type(None))) else False:
                                clean_record[k] = None
                            else:
                                clean_record[k] = v
                        earnings_data.append(clean_record)
            except Exception as e:
                logger.warning(f"Error fetching earnings dates for {ticker}: {e}")
            
            # Get info safely
            try:
                info = ticker_obj.info
            except Exception as e:
                logger.warning(f"Error fetching info for {ticker}: {e}")
                info = {}
            
            data = {
                'info': info,
                'financials': ticker_obj.financials.to_dict() if hasattr(ticker_obj, 'financials') and not ticker_obj.financials.empty else {},
                'balance_sheet': ticker_obj.balance_sheet.to_dict() if hasattr(ticker_obj, 'balance_sheet') and not ticker_obj.balance_sheet.empty else {},
                'cashflow': ticker_obj.cashflow.to_dict() if hasattr(ticker_obj, 'cashflow') and not ticker_obj.cashflow.empty else {},
                'quarterly_financials': ticker_obj.quarterly_financials.to_dict() if hasattr(ticker_obj, 'quarterly_financials') and not ticker_obj.quarterly_financials.empty else {},
                'quarterly_balance_sheet': ticker_obj.quarterly_balance_sheet.to_dict() if hasattr(ticker_obj, 'quarterly_balance_sheet') and not ticker_obj.quarterly_balance_sheet.empty else {},
                'quarterly_cashflow': ticker_obj.quarterly_cashflow.to_dict() if hasattr(ticker_obj, 'quarterly_cashflow') and not ticker_obj.quarterly_cashflow.empty else {},
                'history': history_df.to_dict() if not history_df.empty else {},
                'history_df': history_df.reset_index().to_dict('records') if not history_df.empty else [],
                'recommendations': ticker_obj.recommendations.to_dict() if hasattr(ticker_obj, 'recommendations') and ticker_obj.recommendations is not None and not ticker_obj.recommendations.empty else {},
                'earnings_dates': earnings_data,
            }
            
            self._cache_data(cache_key, data, ttl=settings.cache_ttl_prices)
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
            return self.cache[cache_key]
        
        try:
            # Convert list to dict format expected by get_multiple_fred_series
            # If no frequency specified, use None (default)
            series_info = {sid: None for sid in series_ids}
            data = get_multiple_fred_series(series_info, start_date, end_date)
            
            if data.empty:
                logger.warning(f"FRED data is empty for series: {series_ids}, date range: {start_date} to {end_date}")
                # Don't cache empty data
                return data
            
            self._cache_data(cache_key, data, ttl=settings.cache_ttl_macro)
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
            return self.cache[cache_key]
        
        try:
            cik = self._resolve_cik(ticker)
            if not cik:
                return {'filings': {}, 'ticker': ticker, 'error': f'Could not resolve CIK for {ticker}'}
            
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
            self._cache_data(cache_key, data, ttl=settings.cache_ttl_sec)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching SEC filing data for {ticker}: {e}", exc_info=True)
            return {'filings': {}, 'ticker': ticker, 'error': str(e)}
    
    async def summarize_sec_sections(
        self, 
        ticker: str, 
        sections: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Summarizes multiple SEC filing sections using FinancialAnalyzer.
        
        Args:
            ticker: Stock ticker symbol
            sections: Dictionary mapping section names to full text
        
        Returns:
            Dictionary mapping section names to AI summaries
        """
        from app.services.financial_analyzer import FinancialAnalyzer
        
        try:
            analyzer = FinancialAnalyzer(cache=self.cache)
            summaries = {}
            
            # Summarize sections in parallel to save time
            tasks = []
            section_keys = []
            
            for section_name, text in sections.items():
                if text and len(text.strip()) > 100:
                    tasks.append(analyzer.summarize_sec_section(section_name, text))
                    section_keys.append(section_name)
            
            if not tasks:
                return {}
                
            results = await asyncio.gather(*tasks)
            
            for i, summary in enumerate(results):
                summaries[section_keys[i]] = summary
                
            return summaries
        except Exception as e:
            logger.error(f"Error in summarize_sec_sections for {ticker}: {e}")
            return {}

    async def get_comparison_summary(
        self,
        tickers: List[str],
        report_type: str,
        section_key: str
    ) -> str:
        """
        Orchestrates comparative summary for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            report_type: '10-k' or '10-q'
            section_key: Key of the section to compare (e.g. 'business', 'risk', 'mda')
            
        Returns:
            Comparative AI summary string
        """
        from app.services.financial_analyzer import FinancialAnalyzer
        
        try:
            ticker_texts = {}
            tasks = []
            valid_tickers = []
            
            for ticker in tickers:
                if report_type.lower() == '10-k':
                    tasks.append(self.get_10k_section_data(ticker, [section_key]))
                else:
                    tasks.append(self.get_10q_section_data(ticker, [section_key]))
                valid_tickers.append(ticker)
            
            results = await asyncio.gather(*tasks)
            
            for i, result in enumerate(results):
                if result:
                    text = list(result.values())[0] if result.values() else ""
                    ticker_texts[valid_tickers[i]] = text
            
            if not ticker_texts:
                return "Could not retrieve section data for any of the selected companies."
            
            analyzer = FinancialAnalyzer(cache=self.cache)
            section_label = section_key.replace('_', ' ').title()
            
            return await analyzer.summarize_sec_comparison(section_label, ticker_texts)
        except Exception as e:
            logger.error(f"Error in get_comparison_summary: {e}")
            return f"Comparison failed: {str(e)}"

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
            return self.cache[cache_key]

        try:
            cik = self._resolve_cik(ticker)
            if not cik:
                return {}
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
            
            self._cache_data(cache_key, section_data, ttl=settings.cache_ttl_sec)
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
            return self.cache[cache_key]

        try:
            cik = self._resolve_cik(ticker)
            if not cik:
                return {}
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
            
            self._cache_data(cache_key, section_data, ttl=settings.cache_ttl_sec)
            return section_data

        except Exception as e:
            logger.error(f"Error fetching or parsing 10-Q data for {ticker}: {e}")
            return {}

    async def get_fundamentals_data(self, ticker: str) -> pd.DataFrame:
        """
        Get fundamentals data for a ticker from the PostgreSQL `fundamentals` table.

        The data is stored in long/tall format:
          ticker | period_end | fiscal_period | metric | category | value

        Falls back to an empty DataFrame when the table has no data for the ticker.
        """
        cache_key = f"fundamentals_{ticker}"

        if self._is_cache_valid(cache_key):
            cached = self.cache[cache_key]
            logger.debug(f"Cache hit for fundamentals_{ticker}")
            return cached

        try:
            from app.database import SessionLocal
            import sqlalchemy as sa

            ticker_upper = ticker.strip().upper()
            logger.info(f"Fetching fundamentals from DB for {ticker_upper}")

            with SessionLocal() as session:
                rows = session.execute(
                    sa.text(
                        """
                        SELECT ticker, period_end, fiscal_period, metric, category, value
                        FROM   fundamentals
                        WHERE  ticker = :ticker
                        ORDER  BY fiscal_period DESC
                        """
                    ),
                    {"ticker": ticker_upper},
                ).fetchall()

            if not rows:
                logger.warning(f"No fundamentals rows found in DB for {ticker_upper}")
                return pd.DataFrame()

            ticker_data = pd.DataFrame(
                rows,
                columns=["Ticker", "PeriodEnd", "FiscalPeriod", "Metric", "Category", "Value"],
            )
            logger.info(f"Loaded {len(ticker_data)} fundamentals rows for {ticker_upper} from DB")

            self._cache_data(cache_key, ticker_data, ttl=settings.cache_ttl_financials)
            return ticker_data

        except Exception as e:
            logger.error(f"Error fetching fundamentals data for {ticker}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def get_available_tickers(self) -> List[str]:
        """
        Return the list of distinct tickers present in the `fundamentals` DB table.
        Falls back to a hardcoded S&P-500 subset when the table is empty/unavailable.
        """
        _FALLBACK = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'V', 'JNJ',
            'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'NFLX',
            'PYPL', 'CMCSA', 'XOM', 'VZ', 'CSCO', 'AVGO', 'COST', 'PFE', 'MRK', 'TMO',
            'ABT', 'ACN', 'NKE', 'LIN', 'DHR', 'PM', 'TXN', 'NEE', 'HON', 'QCOM',
        ]
        try:
            from app.database import SessionLocal
            import sqlalchemy as sa

            with SessionLocal() as session:
                rows = session.execute(
                    sa.text("SELECT DISTINCT ticker FROM fundamentals ORDER BY ticker")
                ).fetchall()

            tickers = [r[0] for r in rows]
            if tickers:
                logger.info(f"Found {len(tickers)} tickers in DB fundamentals table")
                return tickers

            logger.warning("fundamentals table is empty, using fallback ticker list")
            return _FALLBACK

        except Exception as e:
            logger.error(f"Error getting available tickers from DB: {e}")
            return _FALLBACK


    def search_tickers(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for tickers by symbol or company name using the CIK map.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with 'ticker' and 'name'
        """
        if not query or self.cik_df.empty:
            return []
            
        query = query.upper().strip()
        
        # Search in ticker column (exact match first, then starts with)
        # Using string constraints for better performance
        mask_ticker = self.cik_df['ticker'].astype(str).str.contains(query, case=False, na=False)
        mask_name = self.cik_df['name'].astype(str).str.contains(query, case=False, na=False)
        
        # Combine masks
        matches = self.cik_df[mask_ticker | mask_name]
        
        if matches.empty:
            return []
            
        # Prioritize ticker matches that start with query
        matches['score'] = 0
        
        # Exact ticker match gets highest score
        matches.loc[matches['ticker'] == query, 'score'] = 3
        # Ticker starts with query gets medium score
        matches.loc[matches['ticker'].str.startswith(query), 'score'] = 2
        # Name starts with query gets low score
        matches.loc[matches['name'].str.upper().str.startswith(query), 'score'] = 1
        
        # Sort by score descending, then by ticker length (shorter tickers usually more popular)
        matches = matches.sort_values(by=['score', 'ticker'], ascending=[False, True])
        
        # Limit results
        matches = matches.head(limit)
        
        return matches[['ticker', 'name']].to_dict('records')
