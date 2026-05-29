from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class SeenItem(Base):
    __tablename__ = "seen_items"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    external_id: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[Optional[str]] = mapped_column(String)
    price_display: Mapped[Optional[str]] = mapped_column(String)
    image_url: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Subscriber(Base):
    """Users verified and subscribed to alerts."""
    __tablename__ = "subscribers"
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PollerState(Base):
    __tablename__ = "poller_state"
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
