import asyncio
from aiogram import Bot
from src.core.database import init_db
from src.scraper.poller import OLXFetcher, StrategyBPoller
from src.core.logging_config import setup_logging, logger
from src.core.config import settings
from src.models.olx import Product

async def test_polling():
    setup_logging()
    
    # Initialize Bot
    bot = Bot(token=settings.BOT_TOKEN)
    
    # Try to find a user ID to send a test message to
    # For testing, you might need to message the bot first to get your chat_id
    # We will log the new items and try to send one if we have a destination
    
    logger.info("Initializing database...")
    await init_db()
    
    fetcher = OLXFetcher()
    poller = StrategyBPoller(fetcher)
    
    logger.info("Starting initial poll (warming up seen IDs)...")
    initial_items = await poller.poll()
    logger.info(f"Initial poll marked {len(initial_items)} items as seen.")
    
    print("\n--- TEST READY ---")
    print("The database is now 'warm'. I will poll every 15 seconds.")
    print("If a NEW item appears on OLX, it will be logged here.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            logger.info("Polling OLX...")
            new_items = await poller.poll()
            
            if new_items:
                for raw_item in new_items:
                    product = Product.from_olx_json(raw_item)
                    msg = (
                        f"🆕 <b>{product.title}</b>\n"
                        f"💰 {product.price.display}\n"
                        f"📍 {product.location}\n"
                        f"🔗 <a href='{product.url}'>View Listing</a>"
                    )
                    logger.info(f"NEW ITEM: {product.title} - {product.price.display}")
                    # Note: We can't send until we know a chat_id. 
                    # You can find yours by messaging the bot and checking logs later.
            else:
                logger.info("No new items found.")
                
            await asyncio.sleep(15)
    except Exception as e:
        logger.error(f"Polling loop error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_polling())
    except KeyboardInterrupt:
        logger.info("Test stopped by user.")
