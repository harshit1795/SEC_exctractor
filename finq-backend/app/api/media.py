"""
Media generation API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.media_service import MediaService
from app.services.data_source_manager import DataSourceManager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/media", tags=["media"])

# Global media service instance
_media_service: Optional[MediaService] = None


def get_media_service() -> MediaService:
    """Get or create MediaService instance"""
    global _media_service
    if _media_service is None:
        _media_service = MediaService()
    return _media_service


@router.get("/chart/price/{ticker}")
async def generate_price_chart(
    ticker: str,
    period: str = Query(default="1y", description="Time period"),
    user_id: str = Query(default="anonymous", description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Generate price chart image for a ticker
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        user_id: User ID
        db: Database session
    
    Returns:
        Base64 encoded chart image
    """
    try:
        media_service = get_media_service()
        data_manager = DataSourceManager()
        
        # Get price data
        yahoo_data = await data_manager.get_yahoo_finance_data(ticker.upper(), period)
        
        if not yahoo_data:
            raise HTTPException(
                status_code=404,
                detail=f"No price data found for {ticker}"
            )
        
        # Get history data - try history_df first (records format), then history (dict format)
        import pandas as pd
        
        if 'history_df' in yahoo_data and yahoo_data['history_df']:
            # Use records format (easier to convert)
            price_df = pd.DataFrame(yahoo_data['history_df'])
            if 'Date' in price_df.columns:
                price_df['Date'] = pd.to_datetime(price_df['Date'])
                price_df.set_index('Date', inplace=True)
        elif 'history' in yahoo_data and yahoo_data['history']:
            # Convert dict format to DataFrame
            history_dict = yahoo_data['history']
            if isinstance(history_dict, dict) and len(history_dict) > 0:
                # History dict has dates as keys, OHLCV as nested dicts
                price_df = pd.DataFrame(history_dict).T
                price_df.index = pd.to_datetime(price_df.index)
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"No historical data available for {ticker}"
                )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data available for {ticker}"
            )
        
        # Generate chart
        chart_image = media_service.generate_price_chart(
            price_df,
            ticker.upper(),
            period
        )
        
        if not chart_image:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate chart image"
            )
        
        return {
            "ticker": ticker.upper(),
            "period": period,
            "image": chart_image,
            "format": "png"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating price chart: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating chart: {str(e)}"
        )


@router.get("/summary/{ticker}")
async def generate_summary_image(
    ticker: str,
    user_id: str = Query(default="anonymous", description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Generate summary card image for a ticker
    
    Args:
        ticker: Stock ticker symbol
        user_id: User ID
        db: Database session
    
    Returns:
        Base64 encoded summary image
    """
    try:
        media_service = get_media_service()
        data_manager = DataSourceManager()
        
        # Get ticker data
        yahoo_data = await data_manager.get_yahoo_finance_data(ticker.upper(), "1y")
        
        if not yahoo_data or 'info' not in yahoo_data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {ticker}"
            )
        
        info = yahoo_data['info']
        
        # Extract key metrics
        metrics = {
            "Current Price": f"${info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}",
            "Market Cap": f"${format_number(info.get('marketCap', 0))}",
            "P/E Ratio": info.get('trailingPE', 'N/A'),
            "52 Week High": f"${info.get('fiftyTwoWeekHigh', 'N/A')}",
            "52 Week Low": f"${info.get('fiftyTwoWeekLow', 'N/A')}"
        }
        
        # Generate summary image
        summary_image = media_service.generate_summary_image(
            ticker.upper(),
            info.get('longName', ticker),
            metrics
        )
        
        if not summary_image:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate summary image"
            )
        
        return {
            "ticker": ticker.upper(),
            "image": summary_image,
            "format": "png"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )


def format_number(num):
    """Helper to format large numbers"""
    if not num or num == 'N/A':
        return 'N/A'
    if num >= 1e12:
        return f"{(num / 1e12):.2f}T"
    if num >= 1e9:
        return f"{(num / 1e9):.2f}B"
    if num >= 1e6:
        return f"{(num / 1e6):.2f}M"
    return f"{num:,.0f}"

