from litestar import Litestar, get, Request
from litestar.response import Template, ServerSentEvent
from litestar.template.config import TemplateConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import NotFoundException
from src.scraper.poller import OLXFetcher
from src.models.olx import Product
from src.core.config import settings
from src.core.logging_config import setup_logging, logger
import os
import traceback
import asyncio
from typing import List, Dict, AsyncGenerator

# Initialize logging at top level
setup_logging()

# Simple session cache
_product_cache: List[Product] = []

async def fetch_and_normalize(params: Dict[str, str]) -> List[Product]:
    global _product_cache
    fetcher = OLXFetcher()
    
    # Merge custom params with defaults
    merged_params = settings.DEFAULT_PARAMS.copy()
    merged_params.update({k: v for k, v in params.items() if v})
    
    # Update fetcher params temporarily for this request
    fetcher.params = merged_params
    
    raw_listings = await fetcher.fetch_listings()
    products = [Product.from_olx_json(item) for item in raw_listings]
    
    # Handle manual sorting
    sort = params.get("sort", "newest")
    if sort == "price_low":
        products.sort(key=lambda x: x.price.value)
    elif sort == "price_high":
        products.sort(key=lambda x: x.price.value, reverse=True)
    else:
        # Default: newest first
        products.sort(key=lambda x: x.created_at, reverse=True)
    
    _product_cache = products
    return products

@get("/", http_method=["GET", "HEAD"])
async def index() -> Template:
    # Baseline settings from config
    params = settings.DEFAULT_PARAMS.copy()
    products = await fetch_and_normalize(params)
    return Template(template_name="index.html", context={"products": products, "params": params})

@get("/filter")
async def filter_products(request: Request) -> Template:
    # Use request params directly, which include query, location, price_min, category, size, etc.
    params = request.query_params
    products = await fetch_and_normalize(params)
    return Template(template_name="partials/product_list.html", context={"products": products})

@get("/product/{product_id:str}")
async def product_detail(product_id: str) -> Template:
    try:
        # 1. Search in existing cache
        product = next((p for p in _product_cache if p.id == product_id), None)
        
        # 2. If not found, try a broader search or re-fetch current defaults
        if not product:
            logger.info(f"Product {product_id} not in cache, re-fetching...")
            products = await fetch_and_normalize(settings.DEFAULT_PARAMS)
            product = next((p for p in products if p.id == product_id), None)
        
        # 3. Final safety: Raise 404 if still missing
        if not product:
            logger.warning(f"Product {product_id} definitely not found.")
            raise NotFoundException(f"Product with ID {product_id} not found.")
        
        return Template(
            template_name="detail.html", 
            context={
                "product": product,
                "params": settings.DEFAULT_PARAMS
            }
        )
    except Exception as e:
        logger.error(f"CRITICAL ERROR in product_detail: {e}")
        logger.error(traceback.format_exc())
        raise e

from src.core.polling_manager import polling_manager

@get("/stream")
async def stream_new_products() -> ServerSentEvent:
    """SSE endpoint that streams discovery signals to the client."""
    async def sse_generator() -> AsyncGenerator[ServerSentEvent, None]:
        async for queue in polling_manager.subscribe():
            while True:
                try:
                    # Wait for a refresh signal from PollingManager
                    msg = await queue.get()
                    yield ServerSentEvent(data=msg, event="refresh")
                except Exception:
                    break

    return ServerSentEvent(sse_generator())

@get("/api/poll-status")
async def get_poll_status() -> dict:
    return {
        "seconds_remaining": polling_manager.get_seconds_remaining(),
        "next_poll": polling_manager.next_poll_time.isoformat() if polling_manager.next_poll_time else None
    }

from src.bot.notifier import dp, bot
from aiogram import Bot

async def set_bot_branding(bot: Bot):
    """Programmatically sets the bot's description and info."""
    try:
        await bot.set_my_description(
            "Olx Genie — Your automated intelligence for finding premium deals on OLX.in.\n\n"
            "• Real-time discovery engine\n"
            "• High-density filtered alerts\n"
            "• Direct Web UI integration\n\n"
            "Please enter the heart access key to unlock your personal search genie."
        )
        await bot.set_my_short_description(
            "Your private OLX intelligence assistant. ❤️"
        )
        logger.info("Bot branding successfully updated.")
    except Exception as e:
        logger.error(f"Failed to set bot branding: {e}")

from src.core.database import init_db

async def start_polling_engine(app: Litestar) -> None:
    # Ensure database tables are created
    await init_db()
    polling_manager.start()
    # Set branding and start bot polling in background
    await set_bot_branding(bot)
    asyncio.create_task(dp.start_polling(bot))

async def stop_polling_engine(app: Litestar) -> None:
    await polling_manager.stop()
    await bot.session.close()

template_config = TemplateConfig(
    directory=os.path.join(os.path.dirname(__file__), "templates"),
    engine=JinjaTemplateEngine,
)

app = Litestar(
    route_handlers=[index, filter_products, product_detail, get_poll_status, stream_new_products],
    on_startup=[start_polling_engine],
    on_shutdown=[stop_polling_engine],
    template_config=template_config,
    debug=True,
)
