"""
Data Pipeline Service for fetching and updating financial fundamentals data
"""
import pandas as pd
import yfinance as yf
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
from app.config import settings

logger = logging.getLogger(__name__)


class DataPipeline:
    """Service for fetching and updating fundamentals data"""
    
    def __init__(self):
        self.fundamentals_path = self._find_fundamentals_file()
    
    def _find_fundamentals_file(self) -> Optional[Path]:
        """Find the fundamentals parquet file"""
        # Railway runs from finq-backend/, so check current directory first
        # Priority: Railway volume > env var > current directory > project root
        possible_paths = [
            Path("/data/fundamentals_tall.parquet"),  # Railway volume (persistent)
            Path(settings.fundamentals_path),  # From environment variable
            Path("fundamentals_tall.parquet"),  # Current directory (finq-backend/)
            Path(__file__).parent.parent.parent.parent / settings.fundamentals_path,
            Path(__file__).parent.parent.parent.parent / "fundamentals_tall.parquet",
            Path("../fundamentals_tall.parquet"),
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found fundamentals file at {path}")
                return path
        
        logger.warning(f"Fundamentals file not found. Tried: {possible_paths}")
        return None
    
    def _get_existing_data(self) -> pd.DataFrame:
        """Load existing fundamentals data"""
        if not self.fundamentals_path or not self.fundamentals_path.exists():
            return pd.DataFrame()
        
        try:
            df = pd.read_parquet(self.fundamentals_path)
            logger.info(f"Loaded {len(df)} existing rows from {self.fundamentals_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
            return pd.DataFrame()
    
    def _melt_quarterly_data(self, df: pd.DataFrame, ticker: str, category: str) -> pd.DataFrame:
        """
        Convert quarterly financial statements to long format
        Based on build_fundamentals_tall.py logic
        
        Args:
            df: DataFrame with quarterly data (columns are dates, rows are metrics)
            ticker: Ticker symbol
            category: Category name (IncomeStatement, BalanceSheet, CashFlow)
        
        Returns:
            DataFrame in long format with columns: Ticker, FiscalPeriod, Metric, Value, Category, PeriodEnd
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Convert columns to datetime if needed
        cols = []
        for c in df.columns:
            try:
                cols.append(pd.to_datetime(c))
            except (ValueError, TypeError):
                cols.append(pd.NaT)
        df.columns = cols
        df = df.dropna(axis=1, how='all')
        
        records = []
        for metric, row in df.iterrows():
            for period_end, value in row.items():
                if pd.isna(period_end):
                    continue
                
                # Convert to quarter label (e.g., "2025Q1")
                quarter = f"{period_end.year}Q{(period_end.month - 1) // 3 + 1}"
                
                records.append({
                    'Ticker': ticker,
                    'PeriodEnd': period_end.date() if isinstance(period_end, pd.Timestamp) else None,
                    'FiscalPeriod': quarter,
                    'Metric': metric,
                    'Category': category,
                    'Value': float(value) if pd.notna(value) else 0.0,
                })
        
        return pd.DataFrame(records)
    
    async def fetch_ticker_quarterly(self, ticker: str) -> pd.DataFrame:
        """
        Fetch latest quarterly financial data for a ticker from Yahoo Finance
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            DataFrame with quarterly data in long format
        """
        try:
            stock = yf.Ticker(ticker)
            
            all_records = []
            
            # Fetch Income Statement
            try:
                income_stmt = stock.quarterly_financials
                if income_stmt is not None and not income_stmt.empty:
                    income_melted = self._melt_quarterly_data(income_stmt, ticker, 'IncomeStatement')
                    all_records.append(income_melted)
                    logger.info(f"Fetched {len(income_melted)} income statement records for {ticker}")
            except Exception as e:
                logger.warning(f"Error fetching income statement for {ticker}: {e}")
            
            # Fetch Balance Sheet
            try:
                balance_sheet = stock.quarterly_balance_sheet
                if balance_sheet is not None and not balance_sheet.empty:
                    balance_melted = self._melt_quarterly_data(balance_sheet, ticker, 'BalanceSheet')
                    all_records.append(balance_melted)
                    logger.info(f"Fetched {len(balance_melted)} balance sheet records for {ticker}")
            except Exception as e:
                logger.warning(f"Error fetching balance sheet for {ticker}: {e}")
            
            # Fetch Cash Flow
            try:
                cashflow = stock.quarterly_cashflow
                if cashflow is not None and not cashflow.empty:
                    cashflow_melted = self._melt_quarterly_data(cashflow, ticker, 'CashFlow')
                    all_records.append(cashflow_melted)
                    logger.info(f"Fetched {len(cashflow_melted)} cash flow records for {ticker}")
            except Exception as e:
                logger.warning(f"Error fetching cash flow for {ticker}: {e}")
            
            if all_records:
                result = pd.concat(all_records, ignore_index=True)
                logger.info(f"Total records fetched for {ticker}: {len(result)}")
                return result
            else:
                logger.warning(f"No data fetched for {ticker}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching quarterly data for {ticker}: {e}")
            return pd.DataFrame()
    
    async def update_ticker_data(self, ticker: str, force_refresh: bool = False) -> Dict:
        """
        Update fundamentals data for a specific ticker
        
        Args:
            ticker: Stock ticker symbol
            force_refresh: If True, replace all data for this ticker. If False, merge new data.
        
        Returns:
            Dict with update status and statistics
        """
        try:
            # Load existing data
            existing_df = self._get_existing_data()
            
            # Fetch new data
            new_data = await self.fetch_ticker_quarterly(ticker.upper())
            
            if new_data.empty:
                return {
                    'success': False,
                    'message': f'No data fetched for {ticker}',
                    'ticker': ticker,
                    'new_records': 0,
                    'total_records': len(existing_df) if not existing_df.empty else 0
                }
            
            # Merge with existing data
            if existing_df.empty:
                updated_df = new_data
            elif force_refresh:
                # Remove old data for this ticker and add new
                existing_df = existing_df[existing_df['Ticker'].str.upper() != ticker.upper()]
                updated_df = pd.concat([existing_df, new_data], ignore_index=True)
            else:
                # Merge: remove duplicates and keep latest
                # Combine existing and new data
                combined = pd.concat([existing_df, new_data], ignore_index=True)
                
                # Remove duplicates, keeping the latest (new) data
                # Group by Ticker, FiscalPeriod, Metric, Category and keep last
                updated_df = combined.drop_duplicates(
                    subset=['Ticker', 'FiscalPeriod', 'Metric', 'Category'],
                    keep='last'
                )
            
            # Save updated data
            if not self.fundamentals_path:
                # Try to find or create file in appropriate location
                # Priority: Railway volume > current directory > project root
                possible_paths = [
                    Path("/data/fundamentals_tall.parquet"),  # Railway volume
                    Path("fundamentals_tall.parquet"),  # Current directory
                    Path(__file__).parent.parent.parent.parent / "fundamentals_tall.parquet",
                ]
                
                for path in possible_paths:
                    # Use first path that exists (for parent directory) or current directory
                    if path.parent.exists() or path == Path("fundamentals_tall.parquet"):
                        self.fundamentals_path = path
                        break
                
                # Fallback to current directory if nothing found
                if not self.fundamentals_path:
                    self.fundamentals_path = Path("fundamentals_tall.parquet")
            
            # Ensure parent directory exists
            self.fundamentals_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the updated data
            updated_df.to_parquet(self.fundamentals_path, index=False)
            logger.info(f"Saved {len(updated_df):,} records to {self.fundamentals_path}")
            
            new_count = len(new_data)
            total_count = len(updated_df)
            existing_count = len(existing_df) if not existing_df.empty else 0
            
            logger.info(f"Updated {ticker}: {new_count} new records, {total_count} total records")
            
            return {
                'success': True,
                'message': f'Successfully updated data for {ticker}',
                'ticker': ticker,
                'new_records': new_count,
                'existing_records': existing_count,
                'total_records': total_count,
                'file_path': str(self.fundamentals_path)
            }
            
        except Exception as e:
            logger.error(f"Error updating data for {ticker}: {e}")
            return {
                'success': False,
                'message': f'Error updating {ticker}: {str(e)}',
                'ticker': ticker,
                'error': str(e)
            }
    
    async def update_all_tickers(self, tickers: Optional[List[str]] = None, 
                                 batch_size: int = 10, 
                                 delay: float = 0.5) -> Dict:
        """
        Update fundamentals data for multiple tickers
        
        Args:
            tickers: List of tickers to update. If None, uses available tickers.
            batch_size: Number of tickers to process before saving
            delay: Delay between requests (seconds)
        
        Returns:
            Dict with update statistics
        """
        if tickers is None:
            # Get available tickers from existing data
            existing_df = self._get_existing_data()
            if not existing_df.empty and 'Ticker' in existing_df.columns:
                tickers = sorted(existing_df['Ticker'].unique().tolist())
            else:
                # Fallback to common tickers
                tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
        
        results = []
        total_updated = 0
        total_failed = 0
        
        logger.info(f"Starting batch update for {len(tickers)} tickers")
        
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"[{i}/{len(tickers)}] Updating {ticker}...")
            
            result = await self.update_ticker_data(ticker, force_refresh=False)
            results.append(result)
            
            if result['success']:
                total_updated += 1
            else:
                total_failed += 1
            
            # Delay to avoid rate limiting
            if i < len(tickers):
                time.sleep(delay)
        
        return {
            'success': True,
            'total_tickers': len(tickers),
            'updated': total_updated,
            'failed': total_failed,
            'results': results,
            'file_path': str(self.fundamentals_path) if self.fundamentals_path else None
        }
    
    async def get_latest_periods(self, ticker: Optional[str] = None) -> Dict:
        """
        Get information about the latest periods in the data
        
        Args:
            ticker: Optional ticker to filter by
        
        Returns:
            Dict with latest period info
        """
        existing_df = self._get_existing_data()
        
        if existing_df.empty:
            return {
                'latest_period': None,
                'ticker_periods': {},
                'total_records': 0
            }
        
        if ticker:
            existing_df = existing_df[existing_df['Ticker'].str.upper() == ticker.upper()]
        
        if existing_df.empty:
            return {
                'latest_period': None,
                'ticker_periods': {},
                'total_records': 0
            }
        
        # Get latest period per ticker
        ticker_periods = {}
        for t in existing_df['Ticker'].unique():
            ticker_data = existing_df[existing_df['Ticker'] == t]
            periods = sorted(ticker_data['FiscalPeriod'].unique())
            ticker_periods[t] = {
                'latest': periods[-1] if periods else None,
                'all_periods': periods,
                'count': len(periods)
            }
        
        # Overall latest period
        all_periods = sorted(existing_df['FiscalPeriod'].unique())
        latest_period = all_periods[-1] if all_periods else None
        
        return {
            'latest_period': latest_period,
            'ticker_periods': ticker_periods,
            'total_records': len(existing_df),
            'total_tickers': len(existing_df['Ticker'].unique())
        }

