import pytest
from pydantic import ValidationError
from src.core.config import Settings

def test_settings_validation():
    # Test valid settings
    settings = Settings(
        BOT_TOKEN="123:abc",
        POLL_INTERVAL=30
    )
    assert settings.POLL_INTERVAL == 30

def test_invalid_poll_interval():
    # Poll interval < 15 should fail
    with pytest.raises(ValueError, match="Poll interval must be at least 15 seconds"):
        Settings(BOT_TOKEN="123:abc", POLL_INTERVAL=10)

def test_invalid_url():
    with pytest.raises(ValidationError):
        Settings(BOT_TOKEN="123:abc", API_URL="not-a-url")
