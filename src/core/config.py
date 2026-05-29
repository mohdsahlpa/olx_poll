from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    BOT_TOKEN: str
    API_URL: str = "https://www.olx.in/api/relevance/v2/search"
    POLL_INTERVAL: int = 30  # Default 30 seconds
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///olx_bot.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
