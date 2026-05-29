from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

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
    # Use absolute path for database to avoid permission issues on servers
    @property
    def DATABASE_URL(self) -> str:
        # If running on Alwaysdata/Linux, use the home directory
        if os.name != 'nt': # Not Windows
            db_path = os.path.join(os.path.expanduser("~"), "olx_bot.db")
            return f"sqlite+aiosqlite:///{db_path}"
        return "sqlite+aiosqlite:///olx_bot.db"
    BASE_URL: str = "http://127.0.0.1:8000"
    
    # Secure access: Heart emoji access key
    BOT_PASSWORD: str = "❤️" 

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("POLL_INTERVAL")
    @classmethod
    def validate_poll_interval(cls, v: int) -> int:
        if v < 15:
            raise ValueError("Poll interval must be at least 15 seconds")
        return v

settings = Settings()
