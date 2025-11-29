#!/usr/bin/env python3
"""
Monthly Data Pipeline Update Script

This script can be run:
1. Manually: python scripts/monthly_data_update.py
2. Via Railway Cron: Scheduled monthly
3. Via GitHub Actions: Scheduled workflow
4. Via External Cron: HTTP call to API endpoint

Usage:
    python scripts/monthly_data_update.py [--tickers TICKER1 TICKER2 ...]
    
Options:
    --tickers: Optional list of specific tickers to update (default: all)
    --force: Force refresh all data (default: incremental update)
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.data_pipeline import DataPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_monthly_update(tickers=None, force_refresh=False):
    """
    Run monthly data pipeline update
    
    Args:
        tickers: Optional list of tickers to update (None = all)
        force_refresh: If True, replace all data (default: incremental)
    
    Returns:
        Dict with update results
    """
    try:
        pipeline = DataPipeline()
        
        # Get tickers to update
        if tickers is None:
            status = await pipeline.get_latest_periods()
            if status.get('ticker_periods'):
                tickers = list(status['ticker_periods'].keys())
                logger.info(f"Found {len(tickers)} tickers in existing data")
            else:
                # Fallback to common tickers if no data exists
                tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'V']
                logger.info(f"No existing data found, using default tickers: {tickers}")
        
        logger.info(f"Starting monthly update for {len(tickers)} tickers")
        logger.info(f"Tickers: {', '.join(tickers[:10])}{'...' if len(tickers) > 10 else ''}")
        
        # Run batch update
        result = await pipeline.update_all_tickers(
            tickers=tickers,
            batch_size=10,
            delay=0.5  # 0.5 second delay between requests
        )
        
        # Log results
        logger.info("=" * 60)
        logger.info("MONTHLY UPDATE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total tickers processed: {result['total_tickers']}")
        logger.info(f"Successfully updated: {result['updated']}")
        logger.info(f"Failed: {result['failed']}")
        logger.info(f"File path: {result.get('file_path', 'N/A')}")
        
        # Log individual failures if any
        if result['failed'] > 0:
            logger.warning("Failed tickers:")
            for r in result['results']:
                if not r.get('success'):
                    logger.warning(f"  - {r.get('ticker')}: {r.get('message', 'Unknown error')}")
        
        # Check data freshness
        status = await pipeline.get_latest_periods()
        if status.get('latest_period'):
            logger.info(f"Latest period in data: {status['latest_period']}")
            logger.info(f"Total records: {status.get('total_records', 0):,}")
            logger.info(f"Total tickers: {status.get('total_tickers', 0)}")
        
        logger.info("=" * 60)
        
        return result
        
    except Exception as e:
        logger.error(f"Monthly update failed: {e}", exc_info=True)
        raise


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Monthly data pipeline update')
    parser.add_argument(
        '--tickers',
        nargs='+',
        help='Specific tickers to update (default: all)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh all data (default: incremental)'
    )
    
    args = parser.parse_args()
    
    try:
        result = await run_monthly_update(
            tickers=args.tickers,
            force_refresh=args.force
        )
        
        # Exit with error code if failures occurred
        if result['failed'] > 0:
            logger.warning(f"Update completed with {result['failed']} failures")
            sys.exit(1)
        
        logger.info("Monthly update completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error in monthly update: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

