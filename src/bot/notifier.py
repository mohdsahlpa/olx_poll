from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from src.core.config import settings
from src.models.olx import Product
import logging

logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

async def format_product_message(product: Product) -> str:
    """Formats a product into a high-density Telegram HTML message."""
    msg = (
        f"<b>🆕 NEW LISTING DETECTED</b>\n\n"
        f"<b>{product.title}</b>\n"
        f"💰 <code>{product.price.display}</code>\n\n"
        f"📍 <b>Location:</b> {product.location}, {product.city}\n"
        f"🏛 <b>State:</b> {product.state}\n"
        f"👤 <b>Seller:</b> {product.seller_name or 'Anonymous'}\n"
        f"🕒 <b>Posted:</b> {product.created_at.strftime('%H:%M • %d %b')}\n\n"
        f"🔗 <a href='{product.url}'>VIEW ORIGINAL LISTING</a>"
    )
    return msg

async def notify_new_product(chat_id: str, product: Product):
    """Sends a notification with an image if available."""
    text = await format_product_message(product)
    try:
        if product.image_url:
            await bot.send_photo(
                chat_id=chat_id,
                photo=product.image_url,
                caption=text,
                parse_mode=ParseMode.HTML
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")
