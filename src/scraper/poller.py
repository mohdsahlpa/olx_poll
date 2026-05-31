import httpx
import logging
import asyncio
from typing import List, Set, Optional
from sqlalchemy import select
from src.core.config import settings
from src.core.database import async_session
from src.models.storage import SeenItem, PollerState
from src.core.logging_config import logger
from src.models.olx import Product

from src.core.utils import get_random_user_agent

class OLXFetcher:
    def __init__(self):
        self.base_url = str(settings.API_URL)
        self.params = settings.DEFAULT_PARAMS
        # Simplified headers to match curl/7.81.0 which works locally
        self.base_headers = {
            "User-Agent": "curl/7.81.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.olx.in/",
            "Origin": "https://www.olx.in",
            "Connection": "keep-alive",
        }

    async def fetch_listings(self) -> List[dict]:
        """Fetches raw listings using lightweight headers and rotating User-Agents."""
        headers = self.base_headers.copy()
        headers["User-Agent"] = get_random_user_agent()
        
        async with httpx.AsyncClient(
            http2=False, 
            timeout=30.0, 
            headers=headers,
            follow_redirects=True
        ) as client:
            for attempt in range(3):
                try:
                    logger.info(f"Attempting fetch (Genie Light) - Attempt {attempt + 1}")
                    response = await client.get(self.base_url, params=self.params)
                    
                    if response.status_code == 403:
                        logger.warning(f"403 Forbidden. Throttled. Attempt {attempt + 1}")
                        await asyncio.sleep(10 * (attempt + 1))
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    return data.get("data", [])
                except (httpx.ReadTimeout, httpx.ConnectTimeout):
                    logger.warning(f"Timeout. Server is slow. Attempt {attempt + 1}")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Error on attempt {attempt + 1}: {type(e).__name__} - {e}")
                    if attempt == 2: return []
                    await asyncio.sleep(5)
            return []

class StrategyBPoller:
    """Implementation of Strategy B: High-Water Mark (ID Tracking)."""
    
    def __init__(self, fetcher: OLXFetcher):
        self.fetcher = fetcher

    async def poll(self) -> List[Product]:
        """Runs a single poll cycle and returns NEW normalized Product objects."""
        raw_items = await self.fetcher.fetch_listings()
        if not raw_items:
            return []

        new_products = []
        async with async_session() as session:
            # 1. Get all seen IDs
            stmt = select(SeenItem.external_id)
            result = await session.execute(stmt)
            seen_ids = set(result.scalars().all())

            for item_data in raw_items:
                product = Product.from_olx_json(item_data)
                if product.external_id not in seen_ids:
                    new_products.append(product)
                    
                    # Store in database with metadata
                    session.add(SeenItem(
                        id=product.id,
                        external_id=product.external_id,
                        title=product.title,
                        price_display=product.price.display,
                        image_url=product.image_url,
                        created_at=product.created_at
                    ))
            
            if new_products:
                await session.commit()
                logger.info(f"Detected {len(new_products)} new products.")
            
        return new_products
