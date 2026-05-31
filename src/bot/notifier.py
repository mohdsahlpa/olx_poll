from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, update
from src.core.config import settings
from src.core.database import async_session
from src.models.storage import Subscriber
from src.models.olx import Product
from src.core.utils import retry_async
from jinja2 import Environment, FileSystemLoader
import logging
import os

logger = logging.getLogger(__name__)

# --- State Management ---
class GenieStates(StatesGroup):
    AWAITING_HEART_KEY = State()
    VERIFIED = State()

# --- Helpers ---
async def set_bot_commands(bot: Bot):
    """Sets the bot's command menu."""
    commands = [
        types.BotCommand(command="start", description="Unlock & start the Genie"),
        types.BotCommand(command="status", description="Check engine & search config"),
        types.BotCommand(command="help", description="How to use Olx Genie"),
        types.BotCommand(command="test_alert", description="Send a test notification to yourself")
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands successfully registered.")

# --- Template Engine ---
template_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=False # We handle our own HTML tags for Telegram
)

def render_template(template_name: str, **context) -> str:
    template = template_env.get_template(template_name)
    return template.render(base_url=settings.BASE_URL, **context)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Initial greeting and password request."""
    async with async_session() as session:
        stmt = select(Subscriber).where(Subscriber.chat_id == message.chat.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            session.add(Subscriber(chat_id=message.chat.id, username=message.from_user.username))
            await session.commit()
            await state.set_state(GenieStates.AWAITING_HEART_KEY)
            await message.answer(
                "<b>Welcome to Olx Genie.</b>\n\n"
                "This is a private automated assistant. Please enter the heart access key to continue.",
                parse_mode=ParseMode.HTML
            )
        elif not user.is_verified:
            await state.set_state(GenieStates.AWAITING_HEART_KEY)
            await message.answer("Access denied. Please enter the heart access key.")
        else:
            await state.set_state(GenieStates.VERIFIED)
            await show_subscription_menu(message)

@dp.message(GenieStates.AWAITING_HEART_KEY, F.text == settings.BOT_PASSWORD)
async def check_password_success(message: types.Message, state: FSMContext):
    """Verify heart access key success."""
    async with async_session() as session:
        await session.execute(
            update(Subscriber)
            .where(Subscriber.chat_id == message.chat.id)
            .values(is_verified=True)
        )
        await session.commit()
    
    await state.set_state(GenieStates.VERIFIED)
    await message.answer("✅ <b>Access Granted.</b>", parse_mode=ParseMode.HTML)
    await show_subscription_menu(message)

@dp.message(GenieStates.AWAITING_HEART_KEY)
async def check_password_fail(message: types.Message):
    """Verify heart access key failure."""
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

@dp.callback_query(GenieStates.VERIFIED, F.data.startswith("sub_"))
async def handle_subscription(callback: types.CallbackQuery):
    is_sub = callback.data == "sub_true"
    from datetime import timezone
    now = datetime.now(timezone.utc)
    async with async_session() as session:
        await session.execute(
            update(Subscriber)
            .where(Subscriber.chat_id == callback.message.chat.id)
            .values(is_subscribed=is_sub, subscribed_at=now if is_sub else None)
        )
        await session.commit()
    
    status = "Active" if is_sub else "Muted"
    await callback.answer(f"Alerts are now {status}.")
    await callback.message.edit_text(f"✅ <b>Genie Status: {status}</b>", parse_mode=ParseMode.HTML)

@dp.message(Command("test_alert"))
async def cmd_test_alert(message: types.Message):
    """Sends a test discovery alert to the user."""
    async with async_session() as session:
        stmt = select(Subscriber).where(Subscriber.chat_id == message.chat.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_verified:
            await message.answer("❌ You must be verified to test alerts.")
            return

    test_text = (
        "<b>🧞‍♂️ GENIE TEST SIGNAL</b>\n\n"
        "Your notification pipeline is <b>active</b>.\n\n"
        "I will notify you individually when a new premium listing is discovered."
    )
    await message.answer(test_text, parse_mode=ParseMode.HTML)

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    """Report system status and current configuration."""
    from src.core.polling_manager import polling_manager
    from src.core.discovery_filter import discovery_filter
    
    # Get local subscription status
    async with async_session() as session:
        stmt = select(Subscriber).where(Subscriber.chat_id == message.chat.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        is_ver = user.is_verified if user else False
        is_sub = user.is_subscribed if user else False

    # Current config details
    q = settings.DEFAULT_PARAMS.get("query", "N/A")
    loc = settings.DEFAULT_PARAMS.get("location", "N/A")
    price = settings.DEFAULT_PARAMS.get("price_min", "0")

    status_text = (
        "<b>🧞‍♂️ Genie Operational Report</b>\n\n"
        f"<b>Engine:</b> {'🟢 Running' if polling_manager.is_running else '🔴 Stopped'}\n"
        f"<b>Cache:</b> {len(discovery_filter._cache)} items indexed\n"
        f"<b>Cycle:</b> Every {settings.POLL_INTERVAL}s (Jittered)\n\n"
        "<b>Current Hunt:</b>\n"
        f"🔍 Query: <code>{q}</code>\n"
        f"📍 Location: <code>{loc}</code>\n"
        f"💰 Min Price: <code>{price}</code>\n\n"
        "<b>Personal Status:</b>\n"
        f"Access: {'✅ Verified' if is_ver else '❌ Unverified'}\n"
        f"Alerts: {'🔔 Active' if is_sub else '🔕 Muted'}"
    )
    
    await message.answer(status_text, parse_mode=ParseMode.HTML)

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Show help information."""
    help_text = (
        "<b>🧞‍♂️ Olx Genie Help</b>\n\n"
        "I am an automated intelligence assistant that polls OLX.in for new listings.\n\n"
        "<b>Commands:</b>\n"
        "/start - Authenticate & configure alerts\n"
        "/status - Check engine & search config\n"
        "/test_alert - Verify your connection\n"
        "/help - Show this message\n\n"
        "<b>Pure Stream Logic:</b>\n"
        "• I notify you <b>individually</b> for every new listing found.\n"
        "• I only alert you about items discovered <b>after</b> you subscribe.\n"
        "• The Web UI is filtered to only show items from the <b>last 30 minutes</b>."
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)

from datetime import datetime, timezone

# --- Notification Logic ---

@retry_async(retries=3, delay=2.0)
async def broadcast_listing(product: Product):
    """Send a new product to all active subscribers who joined before discovery."""
    logger.info(f"Genie Trace: Preparing broadcast for {product.id}")
    async with async_session() as session:
        # PURE STREAM: Only notify users whose subscription started BEFORE this product was fetched
        try:
            stmt = select(Subscriber.chat_id).where(
                Subscriber.is_subscribed == True,
                Subscriber.subscribed_at <= datetime.now(timezone.utc)
            )
            result = await session.execute(stmt)
            subscriber_ids = result.scalars().all()
            logger.info(f"Genie Trace: Found {len(subscriber_ids)} target subscribers.")
        except Exception as e:
            logger.error(f"Genie Trace: Database query failed: {e}", exc_info=True)
            return

    if not subscriber_ids:
        logger.info("Genie Trace: No active subscribers found for this product.")
        return

    text = render_template("discovery.html", product=product)
    contact_url = f"https://www.olx.in/chat/conversation/item/{product.id}"
    dashboard_url = f"{settings.BASE_URL}/product/{product.id}"

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🖥️ GENIE DASHBOARD", url=dashboard_url)
    )

    for chat_id in subscriber_ids:
        try:
            logger.info(f"Genie Trace: Handing to Telegram API for {chat_id}")
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
            logger.info(f"Genie Trace: Telegram API success for {chat_id}")
        except Exception as e:
            logger.error(f"Genie Trace: Telegram API failed for {chat_id}: {e}", exc_info=True)
