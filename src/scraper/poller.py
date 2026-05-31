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

from src.core.stealth_config import get_stealth_profile

class OLXFetcher:
    def __init__(self):
        self.base_url = str(settings.API_URL)
        self.params = settings.DEFAULT_PARAMS
        # Minimalist high-trust headers with explicit Host and no compression
        self.headers = {
            "Host": "api.olx.in",
            "User-Agent": "curl/7.81.0",
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "Connection": "close", # Force close to avoid stale gateway sessions
        }

    async def fetch_listings(self) -> List[dict]:
        """Fetches raw listings using a high-trust minimalist strategy with extended timeout."""
        # Use fresh client per request to avoid gateway connection reuse issues
        async with httpx.AsyncClient(
            http2=False, 
            timeout=60.0, # Increased for 504 resilience
            headers=self.headers,
            follow_redirects=True
        ) as client:
            for attempt in range(3):
                try:
                    logger.info(f"Attempting fetch (Resilient Trust) - Attempt {attempt + 1}")
                    response = await client.get(self.base_url, params=self.params)
                    
                    if response.status_code == 403:
                        logger.warning(f"403 Forbidden. Strategy: Long Sleep {60 * (attempt + 1)}s")
                        await asyncio.sleep(60 * (attempt + 1))
                        continue
                    
                    if response.status_code == 504:
                        logger.warning(f"504 Gateway Timeout. Server is overloaded. Attempt {attempt + 1}")
                        await asyncio.sleep(10)
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    return data.get("data", [])
                except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ReadError):
                    logger.warning(f"Network error (Reset/Timeout). Attempt {attempt + 1}")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"Error on attempt {attempt + 1}: {type(e).__name__} - {e}")
                    if attempt == 2: return []
                    await asyncio.sleep(5)
            return []

from src.core.discovery_filter import discovery_filter

from datetime import datetime, timedelta, timezone

class StrategyBPoller:
    """Implementation of Strategy B: High-Water Mark with a 30-minute Discovery Window."""
    
    def __init__(self, fetcher: OLXFetcher):
        self.fetcher = fetcher

    async def poll(self) -> List[Product]:
        """Runs a single poll cycle and returns NEW normalized Product objects within the 30m window."""
        # Ensure filter is loaded
        await discovery_filter.initialize()
        
        raw_items = await self.fetcher.fetch_listings()
        if not raw_items:
            return []

        new_products = []
        now = datetime.utcnow()
        discovery_window = now - timedelta(minutes=30)

        async with async_session() as session:
            for item_data in raw_items:
                product = Product.from_olx_json(item_data)
                
                # Check if it's already in the 'seen' database/cache
                is_unseen = not discovery_filter.is_seen(product.external_id)
                
                # Apply 30-minute rule: only consider it 'New' for discovery if posted recently
                is_recent = product.created_at >= discovery_window
                
                if is_unseen:
                    # Add to database regardless of age so we don't process it again
                    discovery_filter.add(product.external_id)
                    session.add(SeenItem(
                        id=product.id,
                        external_id=product.external_id,
                        title=product.title,
                        price_display=product.price.display,
                        image_url=product.image_url,
                        created_at=product.created_at
                    ))
                    
                    # Only return for broadcast/UI if it meets the recency requirement
                    if is_recent:
                        new_products.append(product)
            
            if new_products:
                await session.commit()
                logger.info(f"Detected {len(new_products)} new products within the 30m window.")
            elif any(discovery_filter.is_seen(Product.from_olx_json(i).external_id) for i in raw_items):
                # Ensure we commit the 'seen' items even if they weren't in the window
                await session.commit()
            
        return new_products
