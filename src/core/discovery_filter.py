from typing import Set
from sqlalchemy import select
from src.core.database import async_session
from src.models.storage import SeenItem
from src.core.logging_config import logger

class DiscoveryFilter:
    """
    High-performance in-memory cache for seen IDs.
    Acts as a source-of-truth for the poller to avoid redundant DB lookups.
    """
    def __init__(self):
        self._cache: Set[str] = set()
        self._is_initialized = False

    async def initialize(self):
        """Loads all existing external_ids from the database into memory."""
        if self._is_initialized:
            return
            
        async with async_session() as session:
            stmt = select(SeenItem.external_id)
            result = await session.execute(stmt)
            ids = result.scalars().all()
            self._cache.update(ids)
            
        self._is_initialized = True
        logger.info(f"DiscoveryFilter: Initialized with {len(self._cache)} seen items.")

    def is_seen(self, external_id: str) -> bool:
        """Check if an ID has been seen (O(1) lookup)."""
        return external_id in self._cache

    def add(self, external_id: str):
        """Add a new ID to the cache."""
        self._cache.add(external_id)

discovery_filter = DiscoveryFilter()
