import asyncio
from src.core.database import init_db
from src.scraper.poller import OLXFetcher, StrategyBPoller
from src.core.logging_config import setup_logging, logger

async def test_polling():
    setup_logging()
    logger.info("Initializing database...")
    await init_db()
    
    fetcher = OLXFetcher()
    poller = StrategyBPoller(fetcher)
    
    logger.info("Starting initial poll (warming up seen IDs)...")
    # First poll will mark everything as seen so we don't flood on start
    await poller.poll()
    
    logger.info("Waiting for next poll cycle (simulated)...")
    await asyncio.sleep(2)
    
    logger.info("Polling again to check for new items...")
    new_items = await poller.poll()
    logger.info(f"Found {len(new_items)} new items.")

if __name__ == "__main__":
    try:
        asyncio.run(test_polling())
    except KeyboardInterrupt:
        pass
