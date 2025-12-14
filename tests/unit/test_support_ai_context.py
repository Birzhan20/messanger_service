# tests/unit/test_user_context.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.get_user_info_ai import get_user_ai_context
from sqlalchemy import text

@pytest.mark.asyncio
async def test_get_user_context(db_session: AsyncSession):
    # Подготавливаем данные
    await db_session.execute(text("""
        INSERT INTO users (id, email, profile_type) 
        VALUES (1, 'test@example.com', 'basic')
    """))

    await db_session.execute(text("""
        INSERT INTO tickets (id, user_id, status, message)
        VALUES (10, 1, 'open', 'help me')
    """))

    await db_session.execute(text("""
        INSERT INTO announcements (id, user_id)
        VALUES (5, 1)
    """))

    await db_session.commit()

    # Делаем вызов
    result = await get_user_ai_context(db_session, user_id=1)

    # Проверяем поля
    assert result["id"] == 1
    assert result["email"] == "test@example.com"
    assert result["profile_type"] == "basic"
    assert result["tickets_count"] == 1
    assert result["announcements_count"] == 1
    assert result["last_ticket_status"] == "open"
