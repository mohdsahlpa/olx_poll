import pytest
from sqlalchemy import select
from src.models.storage import SeenItem, Subscriber

@pytest.mark.asyncio
async def test_database_init(test_session):
    # Tables should exist and be empty
    stmt = select(SeenItem)
    result = await test_session.execute(stmt)
    assert result.scalars().all() == []

@pytest.mark.asyncio
async def test_subscriber_operations(test_session):
    # Create subscriber
    sub = Subscriber(chat_id=123, username="test_user")
    test_session.add(sub)
    await test_session.commit()
    
    # Retrieve subscriber
    stmt = select(Subscriber).where(Subscriber.chat_id == 123)
    result = await test_session.execute(stmt)
    retrieved = result.scalar_one()
    assert retrieved.username == "test_user"
    assert retrieved.is_verified is False
