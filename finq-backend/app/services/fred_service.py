"""
FRED API service
Wrapper around fredapi for use in FastAPI
Migrated from fred_data.py
"""
import pandas as pd
from fredapi import Fred
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize FRED client
_fred_client = None


def get_fred_client() -> Fred:
    """Get or create FRED client"""
    global _fred_client
    if _fred_client is None:
        if not settings.fred_api_key:
            raise ValueError("FRED_API_KEY not configured")
        _fred_client = Fred(api_key=settings.fred_api_key)
    return _fred_client


def get_fred_series(
    series_id: str, 
    start_date: str, 
    end_date: str, 
    frequency: str = None
) -> pd.Series:
    """
    Fetch a single FRED series
    
    Args:
        series_id: FRED series ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        frequency: Optional frequency (d, w, m, q, a)
    
    Returns:
        Pandas Series with data
    """
    try:
        fred = get_fred_client()
        # Only pass frequency if it's not None
        if frequency:
            data = fred.get_series(
                series_id, 
                observation_start=start_date, 
                observation_end=end_date, 
                frequency=frequency
            )
        else:
            data = fred.get_series(
                series_id, 
                observation_start=start_date, 
                observation_end=end_date
            )
        if data is None or data.empty:
            logger.warning(f"No data found for FRED series: {series_id} in date range {start_date} to {end_date}")
            return pd.Series()
        logger.info(f"Successfully fetched {len(data)} data points for FRED series: {series_id}")
        return data
    except ValueError as e:
        # FRED_API_KEY not configured - re-raise
        logger.error(f"FRED API key error for series {series_id}: {e}")
        raise
    except Exception as e:
        error_msg = str(e).lower()
        # Check if it's an API key or authentication error
        if 'api key' in error_msg or 'authentication' in error_msg or 'invalid' in error_msg or '403' in error_msg or '401' in error_msg:
            logger.error(f"FRED API authentication error for series {series_id}: {e}")
            raise ValueError(f"FRED API authentication failed: {e}")
        # For other errors, log and return empty (might be network issue, invalid series, etc.)
        logger.error(f"Error fetching FRED series {series_id}: {e}")
        return pd.Series()


def get_multiple_fred_series(
    series_info: dict, 
    start_date: str, 
    end_date: str
) -> pd.DataFrame:
    """
    Fetch multiple FRED series
    
    Args:
        series_info: Dict mapping series_id to frequency (or None)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        DataFrame with all series
    """
    all_data = {}
    errors = []
    for series_id, freq in series_info.items():
        try:
            data = get_fred_series(series_id, start_date, end_date, frequency=freq)
            if not data.empty:
                all_data[series_id] = data
            else:
                logger.warning(f"Empty data returned for FRED series: {series_id}")
        except ValueError as e:
            # API key or authentication error - re-raise immediately
            logger.error(f"FRED API key error for {series_id}: {e}")
            raise
        except Exception as e:
            logger.warning(f"Could not fetch {series_id}: {e}")
            errors.append(f"{series_id}: {str(e)}")
    
    if not all_data:
        if errors:
            logger.error(f"All FRED series failed to fetch. Errors: {errors}")
        else:
            logger.warning(f"No data returned for any FRED series: {list(series_info.keys())}")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_data)
    df.index.name = 'Date'
    # Localize timezone to UTC (matching original behavior)
    if not df.empty:
        df.index = df.index.tz_localize('UTC') if df.index.tz is None else df.index
    logger.info(f"Successfully fetched FRED data: {len(df)} rows, {len(df.columns)} series")
    return df


