import asyncio
import json
from src.scraper.poller import OLXFetcher
from src.models.olx import Product
from src.core.logging_config import setup_logging, logger

async def verify_fetch_and_normalize():
    setup_logging()
    fetcher = OLXFetcher()
    
    logger.info("Attempting to fetch listings...")
    raw_listings = await fetcher.fetch_listings()
    
    if not raw_listings:
        logger.error("No listings returned from API.")
        return

    logger.info(f"Successfully fetched {len(raw_listings)} raw listings.")
    
    normalized_products = []
    for i, item in enumerate(raw_listings):
        try:
            product = Product.from_olx_json(item)
            normalized_products.append(product)
            if i < 5:  # Print first 5 for verification
                print(f"\n[Product {i+1}]")
                print(f"Title:    {product.title}")
                print(f"Price:    {product.price.display}")
                print(f"Location: {product.location}")
                print(f"URL:      {product.url}")
                print(f"Image:    {product.image_url}")
        except Exception as e:
            logger.error(f"Failed to normalize item {i}: {e}")

    logger.info(f"Total normalized products: {len(normalized_products)}/{len(raw_listings)}")

if __name__ == "__main__":
    asyncio.run(verify_fetch_and_normalize())
