from datetime import datetime
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status

from src.models.chat import Chat
from src.models.announcement import Announcement
from src.models.messages import Message
from src.models.user import User


async def get_or_create_chat(announcement_id: int, buyer_id: int, db: AsyncSession):
    """Получить чат или создать новый (кнопка 'Написать')"""
    # Ищем существующий чат
    result = await db.execute(
        select(Chat).where(
            Chat.announcement_id == announcement_id,
            Chat.buyer_id == buyer_id
        )
    )
    chat = result.scalar_one_or_none()

    if not chat:
        result = await db.execute(select(Announcement).where(Announcement.id == announcement_id))
        announcement = result.scalar_one_or_none()
        if not announcement:
            raise HTTPException(status_code=404, detail="Объявление не найдено")

        chat = Chat(
            announcement_id=announcement_id,
            buyer_id=buyer_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)

    return chat


async def send_message(chat_id: int, sender_id: int, db: AsyncSession, text: str = None, file_url: str = None,
                       message_type: str  = "text"):
    """Отправить сообщение + обновить превью"""
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")

    result = await db.execute(select(Announcement.user_id).where(Announcement.id == chat.announcement_id))
    seller_id = result.scalar_one()

    if sender_id not in (chat.buyer_id, seller_id):
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    message = Message(
        chat_id=chat_id,
        sender_id=sender_id,
        message_text=text,
        file_url=file_url,
        message_type=message_type,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.add(message)

    # Обновляем превью чата
    if message_type == "text" and text:
        preview = text[:100] + ("..." if len(text) > 100 else "")
    elif message_type == "image":
        preview = "Фото"
    elif message_type == "video":
        preview = "Видео"
    elif message_type == "document":
        preview = "Документ"
    else:
        preview = "Сообщение"

    chat.last_message_text = preview
    chat.last_message_type = message_type
    chat.last_message_at = datetime.utcnow()

    await db.commit()
    await db.refresh(message)
    return message


async def get_user_chats(db: "AsyncSession", user_id: int):
    """Все чаты пользователя (покупатель или продавец)"""
    result = await db.execute(
        select(Chat)
        .join(Announcement)
        .options(
            selectinload(Chat.ad),
            selectinload(Chat.buyer),
        )
        .where(
            or_(
                Chat.buyer_id == user_id,
                Announcement.user_id == user_id
            )
        )
        .order_by(Chat.last_message_at.desc().nulls_last())
    )
    return result.scalars().all()


async def get_chat_with_messages(chat_id: int, user_id: int, db: AsyncSession):
    """Открыть чат + историю + отметить прочитанными"""
    result = await db.execute(
        select(Chat)
        .options(
            selectinload(Chat.ad).selectinload(Announcement.user_id),
            selectinload(Chat.buyer),
            selectinload(Chat.messages).selectinload(Message.sender)
        )
        .where(
            Chat.id == chat_id,
            or_(
                Chat.buyer_id == user_id,
                Chat.ad.has(Announcement.user_id == user_id)
            )
        )
    )
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден или доступ запрещён")

    # Отмечаем входящие сообщения прочитанными
    await db.execute(
        update(Message)
        .where(
            Message.chat_id == chat_id,
            Message.sender_id != user_id,
            Message.is_read == False
        )
        .values(is_read=True)
    )
    await db.commit()

    return chat