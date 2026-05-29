import httpx
import logging
import asyncio
from typing import List, Set, Optional
from sqlalchemy import select
from src.core.config import settings
from src.core.database import async_session
from src.models.storage import SeenItem, PollerState
from src.core.logging_config import logger

class OLXFetcher:
    def __init__(self):
        self.base_url = str(settings.API_URL)
        self.params = settings.DEFAULT_PARAMS
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

    async def fetch_listings(self) -> List[dict]:
        """Fetches raw listings from OLX API with retries."""
        async with httpx.AsyncClient(timeout=15.0, headers=self.headers) as client:
            for attempt in range(3):
                try:
                    response = await client.get(self.base_url, params=self.params)
                    if response.status_code == 403:
                        logger.warning(f"Access forbidden (403) on attempt {attempt + 1}. Retrying with backoff...")
                        await asyncio.sleep(5 * (attempt + 1))
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    return data.get("data", [])
                except httpx.HTTPError as e:
                    logger.error(f"HTTP error occurred: {e}")
                    if attempt == 2: raise
                    await asyncio.sleep(2)
            return []

class StrategyBPoller:
    """Implementation of Strategy B: High-Water Mark (ID Tracking)."""
    
    def __init__(self, fetcher: OLXFetcher):
        self.fetcher = fetcher

    async def poll(self) -> List[dict]:
        """Runs a single poll cycle and returns NEW items only."""
        raw_items = await self.fetcher.fetch_listings()
        if not raw_items:
            return []

        new_items = []
        async with async_session() as session:
            # 1. Get all seen IDs in one go for comparison
            # In a real high-scale app, we'd use a more sophisticated timestamp check
            # but for Strategy B, we track existence.
            stmt = select(SeenItem.external_id)
            result = await session.execute(stmt)
            seen_ids = set(result.scalars().all())

            for item in raw_items:
                item_id = str(item.get("id"))
                if item_id not in seen_ids:
                    new_items.append(item)
                    # Mark as seen
                    session.add(SeenItem(id=item_id, external_id=item_id))
            
            if new_items:
                await session.commit()
                logger.info(f"Detected {len(new_items)} new items.")
            
        return new_items
