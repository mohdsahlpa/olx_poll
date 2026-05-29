from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    BOT_TOKEN: str
    API_URL: HttpUrl = "https://api.olx.in/relevance/v4/search"
    
    # Default search parameters for OLX (exactly matching the provided URL)
    DEFAULT_PARAMS: dict = {
        "category": "1453",
        "facet_limit": "1000",
        "location": "2001160",
        "location_facet_limit": "40",
        "make": "iphone",
        "platform": "web-desktop",
        "price_min": "25000",
        "pttEnabled": "true",
        "query": "iphone",
        "relaxedFilters": "true",
        "size": "40",
        "spellcheck": "true",
        "user": "08760266372311145",
        "lang": "en-IN"
    }

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
