from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, update
from src.core.config import settings
from src.core.database import async_session
from src.models.storage import Subscriber
from src.models.olx import Product
import logging

logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Initial greeting and password request."""
    async with async_session() as session:
        # Check if user exists
        stmt = select(Subscriber).where(Subscriber.chat_id == message.chat.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            session.add(Subscriber(chat_id=message.chat.id, username=message.from_user.username))
            await session.commit()
            await message.answer(
                "<b>Welcome to Olx Genie.</b>\n\n"
                "This is a private automated assistant. Please enter the heart access key to continue.",
                parse_mode=ParseMode.HTML
            )
        elif not user.is_verified:
            await message.answer("Access denied. Please enter the heart access key.")
        else:
            await show_subscription_menu(message)

@dp.message(F.text == "❤️")
async def check_password(message: types.Message):
    """Verify heart access key."""
    if message.text == settings.BOT_PASSWORD:
        async with async_session() as session:
            await session.execute(
                update(Subscriber)
                .where(Subscriber.chat_id == message.chat.id)
                .values(is_verified=True)
            )
            await session.commit()
        await message.answer("✅ <b>Access Granted.</b>", parse_mode=ParseMode.HTML)
        await show_subscription_menu(message)
    else:
        await message.answer("❌ Incorrect key. Access denied.")

async def show_subscription_menu(message: types.Message):
    """Ask verified user to subscribe or not."""
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔔 Subscribe to Alerts", callback_data="sub_true"),
        types.InlineKeyboardButton(text="🔕 Mute Alerts", callback_data="sub_false")
    )
    await message.answer(
        "<b>Genie Control Center</b>\n\nWould you like to receive real-time notifications for new listings?",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data.startswith("sub_"))
async def handle_subscription(callback: types.CallbackQuery):
    is_sub = callback.data == "sub_true"
    async with async_session() as session:
        await session.execute(
            update(Subscriber)
            .where(Subscriber.chat_id == callback.message.chat.id)
            .values(is_subscribed=is_sub)
        )
        await session.commit()
    
    status = "Active" if is_sub else "Muted"
    await callback.answer(f"Alerts are now {status}.")
    await callback.message.edit_text(f"✅ <b>Genie Status: {status}</b>", parse_mode=ParseMode.HTML)

# --- Notification Logic ---

async def broadcast_listing(product: Product):
    """Send a new product to all active subscribers with an Instant Contact button."""
    async with async_session() as session:
        stmt = select(Subscriber.chat_id).where(Subscriber.is_subscribed == True)
        result = await session.execute(stmt)
        subscriber_ids = result.scalars().all()

    # Base URL for the Genie Web UI
    base_url = settings.BASE_URL
    
    # "Instant Contact" Link (Deep link to OLX Chat)
    contact_url = f"https://www.olx.in/chat/conversation/item/{product.id}"
    
    text = (
        f"<b>🆕 GENIE DISCOVERY</b>\n\n"
        f"<b>{product.title}</b>\n"
        f"💰 <code>{product.price.display}</code>\n\n"
        f"📍 {product.location}, {product.city}\n"
        f"🕒 {product.created_at.strftime('%H:%M • %d %b')}\n\n"
        f"🔗 <a href='{base_url}/product/{product.id}'>VIEW IN GENIE DASHBOARD</a>"
    )

    # Keyboard with Instant Contact Bridge
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="💬 INSTANT CONTACT", url=contact_url),
        types.InlineKeyboardButton(text="🖥️ GENIE DASHBOARD", url=f"{base_url}/product/{product.id}")
    )

    for chat_id in subscriber_ids:
        try:
            if product.image_url:
                await bot.send_photo(
                    chat_id=chat_id, 
                    photo=product.image_url, 
                    caption=text, 
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
            else:
                await bot.send_message(
                    chat_id=chat_id, 
                    text=text, 
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.error(f"Broadcast failed for {chat_id}: {e}")
