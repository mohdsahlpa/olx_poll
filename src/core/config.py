from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    BOT_TOKEN: str
    # Using HttpUrl ensures validation of the URL format
    API_URL: HttpUrl = "https://www.olx.in/api/relevance/v2/search"
    POLL_INTERVAL: int = 30
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite+aiosqlite:///olx_bot.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("POLL_INTERVAL")
    @classmethod
    def validate_poll_interval(cls, v: int) -> int:
        if v < 15:
            raise ValueError("Poll interval must be at least 15 seconds")
        return v

settings = Settings()
