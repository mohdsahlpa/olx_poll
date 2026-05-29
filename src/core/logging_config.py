import logging
import sys
from src.core.config import settings

def setup_logging():
    """
    Configures centralized logging for the application.
    """
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("olx_bot.log", encoding="utf-8")
        ]
    )
    
    # Set levels for third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)

logger = logging.getLogger("olxbot")
