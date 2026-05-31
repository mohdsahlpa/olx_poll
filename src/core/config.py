from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    BOT_TOKEN: str
    API_URL: HttpUrl = "https://api.olx.in/relevance/v4/search"
    
    # Default search parameters for OLX
    DEFAULT_PARAMS: dict = {
        "category": "1453",
        "facet_limit": "100",
        "location": "2001160",
        "location_facet_limit": "20",
        "make": "iphone",
        "platform": "web-desktop",
        "price_min": "25000",
        "pttEnabled": "true",
        "query": "iphone",
        "relaxedFilters": "true",
        "size": "40",
        "spellcheck": "true",
        "lang": "en-IN"
    }

    POLL_INTERVAL: int = 30
    LOG_LEVEL: str = "INFO"
    # Robust paths for production
    @property
    def DATABASE_URL(self) -> str:
        if os.name != 'nt':  # Linux/Production
            db_path = os.path.join(os.path.expanduser("~"), "olx_bot.db")
            return f"sqlite+aiosqlite:///{db_path}"
        return "sqlite+aiosqlite:///olx_bot.db"

    @property
    def BASE_URL(self) -> str:
        # Check if running on Render
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url:
            return render_url.rstrip("/")
        # Fallback to manual env var or local loopback
        return os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    
    # Secure access: Password key
    BOT_PASSWORD: str = "idontknow" 

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("POLL_INTERVAL")
    @classmethod
    def validate_poll_interval(cls, v: int) -> int:
        if v < 15:
            raise ValueError("Poll interval must be at least 15 seconds")
        return v

settings = Settings()
