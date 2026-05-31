import random
import asyncio
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def retry_async(retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Decorator to retry an async function with exponential backoff."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{retries} failed for {func.__name__}: {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= 2
            logger.error(f"All {retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator
