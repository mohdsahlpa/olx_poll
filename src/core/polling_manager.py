import asyncio
import random
import os
from datetime import datetime, timedelta
from typing import Optional, Set
from src.core.logging_config import logger

from src.scraper.poller import OLXFetcher, StrategyBPoller
from src.core.config import settings
from src.models.olx import Product
from src.core.stealth_config import get_poisson_interval

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

    async def _signal_discovery(self, product: Product):
        """Pushes a rich JSON discovery payload to all connected SSE clients."""
        import json
        payload = {
            "id": product.id,
            "title": product.title,
            "price": product.price.display,
            "image": product.image_url,
            "location": product.location,
            "time": product.ist_created_at.strftime('%I:%M %p')
        }
        data = json.dumps(payload)
        for queue in list(self.subscribers):
            await queue.put(data)

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
            # 2. Calculate next interval using Poisson Distribution around settings.POLL_INTERVAL
            interval = get_poisson_interval(float(settings.POLL_INTERVAL))
            self.next_poll_time = datetime.now() + timedelta(seconds=interval)
            
            logger.info(f"Genie Heartbeat: Next poll in {interval:.1f}s at {self.next_poll_time.strftime('%H:%M:%S')}")
            
            # 3. Wait for the interval
            await asyncio.sleep(interval)
            
            # 4. Perform the poll
            try:
                logger.info("Genie Trace: Starting poll cycle...")
                new_products = await self.poller.poll()
                
                if new_products:
                    logger.info(f"Genie Trace: {len(new_products)} unseen products discovered.")
                    
                    # Notify Telegram Subscribers (Pure Stream - Individual)
                    from src.bot.notifier import broadcast_listing
                    for product in new_products:
                        # 1. ALWAYS Broadcast to Bot (Pure Discovery)
                        # The bot internally filters by subscriber timestamp.
                        logger.info(f"Genie Trace: Handoff to bot for product {product.id}")
                        await broadcast_listing(product)
                        
                        # 2. ONLY Broadcast to SSE if within 30m window (for UI relevance)
                        if product.is_new:
                            logger.info(f"Genie Trace: Prepending {product.id} to UI (30m window).")
                            await self._signal_discovery(product)
                        else:
                            logger.info(f"Genie Trace: Skipping UI prepend for {product.id} (Older than 30m).")
                        
                        await asyncio.sleep(1.0) # Safety stagger
                else:
                    logger.info("Genie Trace: No new products found in this cycle.")
                
                self.last_poll_status = f"Last poll discovered {len(new_products)} recent items at {datetime.now().strftime('%H:%M:%S')}"
            except Exception as e:
                logger.error(f"Genie Heartbeat: Poll cycle failed: {e}", exc_info=True)

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
