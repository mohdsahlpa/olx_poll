import asyncio
import json
from curl_cffi.requests import AsyncSession
from src.core.config import settings
from src.core.logging_config import setup_logging, logger

async def inspect_api_response():
    setup_logging()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.olx.in/items/q-iphone",
    }
    
    async with AsyncSession(impersonate="chrome") as session:
        logger.info("Fetching raw response for analysis...")
        response = await session.get(
            str(settings.API_URL), 
            params=settings.DEFAULT_PARAMS, 
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch: {response.status_code}")
            return

        data = response.json()
        listings = data.get("data", [])
        
        if not listings:
            logger.warning("No listings found in response.")
            print(json.dumps(data, indent=2))
            return

        # Inspect the first product in detail
        first_product = listings[0]
        
        print("\n=== RAW PRODUCT STRUCTURE (FIRST ITEM) ===")
        print(json.dumps(first_product, indent=2))
        print("==========================================\n")
        
        # Summary of keys
        print(f"Top-level keys in product: {list(first_product.keys())}")

if __name__ == "__main__":
    asyncio.run(inspect_api_response())
