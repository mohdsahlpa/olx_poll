import asyncio
import random
import os
from datetime import datetime, timedelta
from typing import Optional, Set
from src.core.logging_config import logger

from src.scraper.poller import OLXFetcher, StrategyBPoller
from src.core.config import settings
from src.models.olx import Product

class PollingManager:
    def __init__(self):
        self.next_poll_time: Optional[datetime] = None
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.last_poll_status = "Initialized"
        
        # Initialize engine components
        self.fetcher = OLXFetcher()
        self.poller = StrategyBPoller(self.fetcher)
        
        # SSE Broadcast Queues (Store queues for connected clients)
        self.subscribers: Set[asyncio.Queue] = set()

    async def subscribe(self):
        """Creates a new queue for an SSE client."""
        queue = asyncio.Queue()
        self.subscribers.add(queue)
        logger.info(f"SSE: Client connected. Total subscribers: {len(self.subscribers)}")
        try:
            yield queue
        finally:
            self.subscribers.remove(queue)
            logger.info(f"SSE: Client disconnected. Total subscribers: {len(self.subscribers)}")

    async def _signal_refresh(self):
        """Pushes a refresh signal to all connected SSE clients."""
        for queue in list(self.subscribers):
            await queue.put("refresh")

    def get_seconds_remaining(self) -> int:
        if not self.next_poll_time:
            return 0
        remaining = (self.next_poll_time - datetime.now()).total_seconds()
        return max(0, int(remaining))

    async def _polling_loop(self):
        logger.info("Genie Heartbeat: Starting background polling engine.")
        
        # 1. Warm up the database (mark current items as seen to avoid initial flood)
        logger.info("Genie Heartbeat: Warming up database...")
        try:
            await self.poller.poll()
        except Exception as e:
            logger.error(f"Genie Heartbeat: Initial warmup failed: {e}")
        
        while self.is_running:
            # 2. Calculate next interval (15, 30, 60)
            interval = random.choice([15, 30, 60])
            self.next_poll_time = datetime.now() + timedelta(seconds=interval)
            
            logger.info(f"Genie Heartbeat: Next poll in {interval}s at {self.next_poll_time.strftime('%H:%M:%S')}")
            
            # 3. Wait for the interval
            await asyncio.sleep(interval)
            
            # 4. Perform the poll
            try:
                new_products = await self.poller.poll()
                if new_products:
                    logger.info(f"Genie Heartbeat: Found {len(new_products)} new products. Broadcasting...")
                    
                    # Notify SSE clients (Single refresh trigger)
                    await self._signal_refresh()
                    
                    # Notify Telegram Subscribers
                    from src.bot.notifier import broadcast_listing
                    for product in new_products:
                        await broadcast_listing(product)
                        await asyncio.sleep(1) # Safety
                
                self.last_poll_status = f"Last poll found {len(new_products)} items at {datetime.now().strftime('%H:%M:%S')}"
            except Exception as e:
                logger.error(f"Genie Heartbeat: Poll cycle failed: {e}")

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._polling_loop())

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

polling_manager = PollingManager()
