"""
Financial data API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.data_source_manager import DataSourceManager
from app.schemas.financial import (
    TickerDataResponse,
    MultipleTickersResponse,
    FredDataResponse,
    SecFilingResponse,
    SecFilingResponse,
    SecSectionResponse,
    FundamentalsResponse,
    TickerSearchResponse,
    TickerSearchResult
)
import pandas as pd
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financial", tags=["financial"])

# Global DataSourceManager instance (singleton pattern)
_data_source_manager: Optional[DataSourceManager] = None


def get_data_source_manager() -> DataSourceManager:
    """Get or create DataSourceManager instance"""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
    return _data_source_manager


def _dataframe_to_dict(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert DataFrame to list of dictionaries for JSON serialization"""
    if df.empty:
        return []
    
    # Reset index to include it in the dict
    df_reset = df.reset_index()
    # Convert to dict, handling datetime and other types
    return df_reset.to_dict(orient='records')


@router.get("/ticker/{ticker}", response_model=TickerDataResponse)
async def get_ticker_data(
    ticker: str,
    period: str = "1y",
    db: Session = Depends(get_db)
):
    """
    Get financial data for a single ticker from Yahoo Finance
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        period: Time period for historical data (default: '1y')
            Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    
    Returns:
        Financial data including info, financials, balance sheet, cashflow, etc.
    """
    try:
        manager = get_data_source_manager()
        data = await manager.get_yahoo_finance_data(ticker.upper(), period)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker {ticker}. Please verify the ticker symbol."
            )
        
        return TickerDataResponse(
            ticker=ticker.upper(),
            period=period,
            data=data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticker data for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data for {ticker}: {str(e)}"
        )


@router.get("/tickers", response_model=MultipleTickersResponse)
async def get_multiple_tickers(
    tickers: str,  # Comma-separated list
    period: str = "1y",
    db: Session = Depends(get_db)
):
    """
    Get financial data for multiple tickers
    
    Args:
        tickers: Comma-separated ticker symbols (e.g., 'AAPL,MSFT,GOOGL')
        period: Time period for historical data
    
    Returns:
        Dictionary mapping tickers to their financial data
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    
    if not ticker_list:
        raise HTTPException(status_code=400, detail="No valid tickers provided")
    
    if len(ticker_list) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 tickers allowed per request"
        )
    
    try:
        manager = get_data_source_manager()
        results = {}
        
        for ticker in ticker_list:
            try:
                data = await manager.get_yahoo_finance_data(ticker, period)
                results[ticker] = data if data else {}
            except Exception as e:
                logger.error(f"Error fetching data for {ticker}: {e}")
                results[ticker] = {"error": str(e)}
        
        return MultipleTickersResponse(
            tickers=ticker_list,
            period=period,
            data=results
        )
    except Exception as e:
        logger.error(f"Error fetching multiple tickers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data: {str(e)}"
        )


@router.get("/fred", response_model=FredDataResponse)
async def get_fred_data(
    series_ids: str,  # Comma-separated
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """
    Get FRED economic data
    
    Args:
        series_ids: Comma-separated FRED series IDs (e.g., 'GDP,UNRATE,CPIAUCSL')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        FRED economic data as JSON (DataFrame converted to list of dicts)
    """
    series_list = [s.strip() for s in series_ids.split(",") if s.strip()]
    
    if not series_list:
        raise HTTPException(status_code=400, detail="No valid series IDs provided")
    
    if len(series_list) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 series IDs allowed per request"
        )
    
    try:
        manager = get_data_source_manager()
        df = await manager.get_fred_economic_data(series_list, start_date, end_date)
        
        if df.empty:
            # Check if it's an API key issue
            from app.config import settings
            if not settings.fred_api_key:
                raise HTTPException(
                    status_code=500,
                    detail="FRED_API_KEY not configured. Please set FRED_API_KEY in your backend .env file."
                )
            
            raise HTTPException(
                status_code=404,
                detail=f"No data found for series {series_ids} in date range {start_date} to {end_date}. Please check that the series IDs are valid and the date range is correct."
            )
        
        # Convert DataFrame to list of dicts for JSON serialization
        data_list = _dataframe_to_dict(df)
        
        return FredDataResponse(
            series_ids=series_list,
            start_date=start_date,
            end_date=end_date,
            data=data_list
        )
    except HTTPException:
        raise
    except ValueError as e:
        # FRED_API_KEY not configured
        logger.error(f"FRED API key error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"FRED API configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error fetching FRED data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching FRED data: {str(e)}"
        )


@router.get("/sec/{ticker}", response_model=SecFilingResponse)
async def get_sec_filings(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    Get SEC filing metadata for a ticker
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with filing metadata
    """
    try:
        manager = get_data_source_manager()
        data = await manager.get_sec_filing_data(ticker.upper())
        
        # Return empty filings dict instead of 404 if no filings found
        # This allows the frontend to show a helpful message
        filings = data.get('filings', {}) if data else {}
        
        return SecFilingResponse(
            ticker=ticker.upper(),
            filings=filings
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching SEC filings for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching SEC filings: {str(e)}"
        )


@router.get("/sec/{ticker}/10k", response_model=SecSectionResponse)
async def get_10k_sections(
    ticker: str,
    sections: str = "business,risk,mda",  # Comma-separated
    db: Session = Depends(get_db)
):
    """
    Get 10-K filing sections for a ticker
    
    Args:
        ticker: Stock ticker symbol
        sections: Comma-separated sections to fetch (business, risk, mda)
    
    Returns:
        Dictionary with section names and content
    """
    section_list = [s.strip().lower() for s in sections.split(",") if s.strip()]
    
    if not section_list:
        raise HTTPException(status_code=400, detail="No valid sections provided")
    
    try:
        manager = get_data_source_manager()
        data = await manager.get_10k_section_data(ticker.upper(), section_list)
        
        if not data:
            # Return empty sections instead of 404
            return SecSectionResponse(
                ticker=ticker.upper(),
                sections={},
                filing_type="10-K"
            )
        
        return SecSectionResponse(
            ticker=ticker.upper(),
            sections=data,
            filing_type="10-K"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching 10-K sections for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching 10-K sections: {str(e)}"
        )


@router.get("/sec/{ticker}/10q", response_model=SecSectionResponse)
async def get_10q_sections(
    ticker: str,
    sections: str = "risk,mda",  # Comma-separated
    db: Session = Depends(get_db)
):
    """
    Get 10-Q filing sections for a ticker
    
    Args:
        ticker: Stock ticker symbol
        sections: Comma-separated sections to fetch (risk, mda)
    
    Returns:
        Dictionary with section names and content
    """
    section_list = [s.strip().lower() for s in sections.split(",") if s.strip()]
    
    if not section_list:
        raise HTTPException(status_code=400, detail="No valid sections provided")
    
    try:
        manager = get_data_source_manager()
        data = await manager.get_10q_section_data(ticker.upper(), section_list)
        
        if not data:
            # Return empty sections instead of 404
            return SecSectionResponse(
                ticker=ticker.upper(),
                sections={},
                filing_type="10-Q"
            )
        
        return SecSectionResponse(
            ticker=ticker.upper(),
            sections=data,
            filing_type="10-Q"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching 10-Q sections for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching 10-Q sections: {str(e)}"
        )


@router.get("/fundamentals/{ticker}", response_model=FundamentalsResponse)
async def get_fundamentals(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    Get fundamentals data for a ticker
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Fundamentals data as JSON (DataFrame converted to list of dicts)
    """
    try:
        manager = get_data_source_manager()
        df = await manager.get_fundamentals_data(ticker.upper())
        
        if df.empty:
            # Check if it's a file not found issue
            from pathlib import Path
            from app.config import settings
            possible_paths = [
                Path(settings.fundamentals_path),
                Path(__file__).parent.parent.parent.parent / settings.fundamentals_path,
                Path(__file__).parent.parent.parent.parent / "fundamentals_tall.parquet",
                Path("../fundamentals_tall.parquet"),
            ]
            file_found = any(p.exists() for p in possible_paths)
            
            if not file_found:
                logger.error(f"Fundamentals file not found. Tried paths: {possible_paths}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Fundamentals data file not found on server. Please check FUNDAMENTALS_PATH environment variable."
                )
            
            raise HTTPException(
                status_code=404,
                detail=f"No fundamentals data found for ticker {ticker}. The file exists but contains no data for this ticker."
            )
        
        data_list = _dataframe_to_dict(df)
        
        return FundamentalsResponse(
            ticker=ticker.upper(),
            data=data_list
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching fundamentals: {str(e)}"
        )


@router.get("/tickers/available")
async def get_available_tickers(db: Session = Depends(get_db)):
    """
    Get list of available tickers
    
    Returns:
        List of available ticker symbols
    """
    try:
        manager = get_data_source_manager()
        tickers = manager.get_available_tickers()
        
        return {
            "tickers": tickers,
            "count": len(tickers)
        }
    except Exception as e:
        logger.error(f"Error getting available tickers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting available tickers: {str(e)}"
        )



@router.get("/search", response_model=TickerSearchResponse)
async def search_tickers(
    q: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Search for tickers by symbol or company name
    
    Args:
        q: Search query
        limit: Maximum number of results
        
    Returns:
        List of matching tickers and company names
    """
    if not q or len(q.strip()) < 1:
        raise HTTPException(status_code=400, detail="Query string 'q' is required")
        
    try:
        manager = get_data_source_manager()
        results = manager.search_tickers(q, limit)
        
        return TickerSearchResponse(
            query=q,
            results=results,
            count=len(results)
        )
    except Exception as e:
        logger.error(f"Error searching tickers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching tickers: {str(e)}"
        )
