import asyncio
import logging
from app.services.data_pipeline import DataPipeline

logger = logging.getLogger(__name__)

async def background_update_scheduler():
    """
    Background worker that periodically polls Yahoo Finance to incrementally update
    the fundamentals_tall.parquet file with the latest available quarters.
    Runs completely outside the normal FastAPI request cycle.
    """
    service = DataPipeline()
    
    # Delay initial execution by 10 minutes (600 seconds) after server boot
    # to guarantee migrations or heavy startup events have completed
    logger.info("⏳ Scheduled incremental fundamentals queue to start in 10 minutes")
    await asyncio.sleep(600)
    
    while True:
        try:
            logger.info("🕒 Starting automated CRON fundamentals update...")
            
            # Since update_all_tickers involves heavy networking/pandas and is blocking,
            # we offload it to the default asyncio ThreadPoolExecutor 
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, service.update_all_tickers)
            
            updated = result.get("updated", 0)
            failed = result.get("failed", 0)
            
            logger.info(f"✅ Automated CRON update complete. Updated: {updated}, Failed: {failed}")
        except Exception as e:
            logger.error(f"❌ Automated CRON update failed: {e}")
            
        # Sleep for 24 hours (86400 seconds) before checking again
        # The next daily run will continue incrementally merging new periods
        await asyncio.sleep(86400)
