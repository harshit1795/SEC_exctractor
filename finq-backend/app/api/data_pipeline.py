"""
Data Pipeline API endpoints for updating financial data
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.data_pipeline import DataPipeline
from app.api.financial import get_data_source_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data-pipeline", tags=["data-pipeline"])

# Global pipeline instance
_pipeline: Optional[DataPipeline] = None


def get_pipeline() -> DataPipeline:
    """Get or create DataPipeline instance"""
    global _pipeline
    if _pipeline is None:
        _pipeline = DataPipeline()
    return _pipeline


@router.post("/update/{ticker}")
async def update_ticker(
    ticker: str,
    force_refresh: bool = False,
    db: Session = Depends(get_db)
):
    """
    Update fundamentals data for a specific ticker
    
    Args:
        ticker: Stock ticker symbol
        force_refresh: If True, replace all existing data for this ticker
    
    Returns:
        Update status and statistics
    """
    try:
        pipeline = get_pipeline()
        result = await pipeline.update_ticker_data(ticker.upper(), force_refresh)
        
        if result.get('success'):
            # Clear cache for this ticker's fundamentals data
            manager = get_data_source_manager()
            manager.clear_cache(f"fundamentals_{ticker.upper()}")
            logger.info(f"Cleared cache for {ticker.upper()} after data update")
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result.get('message', 'Update failed')
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticker {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating ticker: {str(e)}"
        )


@router.post("/update-batch")
async def update_batch(
    tickers: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Update fundamentals data for multiple tickers
    
    Args:
        tickers: List of tickers to update. If not provided, updates all available tickers.
    
    Returns:
        Batch update status
    """
    try:
        pipeline = get_pipeline()
        
        # If no tickers provided, get from existing data
        if not tickers:
            existing_info = await pipeline.get_latest_periods()
            if existing_info.get('ticker_periods'):
                tickers = list(existing_info['ticker_periods'].keys())
            else:
                # Fallback to common tickers
                tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
        
        result = await pipeline.update_all_tickers(tickers, batch_size=10, delay=0.5)
        
        return {
            'message': f'Batch update completed: {result["updated"]} updated, {result["failed"]} failed',
            **result
        }
    except Exception as e:
        logger.error(f"Error in batch update: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch update: {str(e)}"
        )


@router.get("/status")
async def get_data_status(
    ticker: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get status of current data (latest periods, record counts, etc.)
    
    Args:
        ticker: Optional ticker to filter by
    
    Returns:
        Data status information
    """
    try:
        pipeline = get_pipeline()
        status = await pipeline.get_latest_periods(ticker)
        return status
    except Exception as e:
        logger.error(f"Error getting data status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting data status: {str(e)}"
        )


@router.post("/update-latest")
async def update_latest_data(
    tickers: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Update data for tickers that need updates (check latest period and fetch if needed)
    
    This is a smart update that only fetches data for tickers that might have new quarters
    
    Args:
        tickers: Optional list of specific tickers to update
    
    Returns:
        Update results
    """
    try:
        pipeline = get_pipeline()
        
        # Get current status
        status = await pipeline.get_latest_periods()
        
        # Determine which tickers need updates
        if tickers is None:
            # Update all tickers that have data
            if status.get('ticker_periods'):
                tickers = list(status['ticker_periods'].keys())
            else:
                tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
        
        # Update each ticker
        result = await pipeline.update_all_tickers(tickers, batch_size=10, delay=0.5)
        
        return {
            'message': 'Latest data update completed',
            **result
        }
    except Exception as e:
        logger.error(f"Error updating latest data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating latest data: {str(e)}"
        )

