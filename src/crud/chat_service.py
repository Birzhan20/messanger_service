from datetime import datetime
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status

from models.chat import Chat
from models.announcement import Announcement
from models.messages import Message
from models.user import User


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
            seller_id=announcement.user_id,
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


async def get_user_chats(db: "AsyncSession", user_id: int, role: str = None):
    """
    Все чаты пользователя (покупатель или продавец).
    
    Args:
        db: AsyncSession
        user_id: ID пользователя
        role: Фильтр - "buyer" (Покупаю) или "seller" (Продаю), None = все чаты
    """
    query = (
        select(Chat)
        .join(Announcement)
        .options(
            selectinload(Chat.ad),
            selectinload(Chat.buyer),
        )
    )
    
    if role == "buyer":
        # Показываем чаты, где пользователь — покупатель
        query = query.where(Chat.buyer_id == user_id)
    elif role == "seller":
        # Показываем чаты, где пользователь — продавец (владелец объявления)
        query = query.where(Announcement.user_id == user_id)
    else:
        # Все чаты пользователя
        query = query.where(
            or_(
                Chat.buyer_id == user_id,
                Announcement.user_id == user_id
            )
        )
    
    query = query.order_by(Chat.last_message_at.desc().nulls_last())
    result = await db.execute(query)
    return result.scalars().all()


async def get_chat_with_messages(chat_id: int, user_id: int, db: AsyncSession):
    """
    Открыть чат + историю + отметить прочитанными.
    
    Возвращает чат с информацией о партнёре (имя, телефон, роль).
    """
    result = await db.execute(
        select(Chat)
        .options(
            selectinload(Chat.ad).selectinload(Announcement.seller),
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
    
    # Определяем партнёра (если я покупатель - партнёр продавец, и наоборот)
    if chat.buyer_id == user_id:
        # Я покупатель, партнёр - продавец
        partner = chat.ad.seller if chat.ad else None
    else:
        # Я продавец, партнёр - покупатель
        partner = chat.buyer
    
    # Формируем ответ с информацией о партнёре
    partner_info = None
    if partner:
        # Определяем роль по user_role_id (1-2 = Бизнес, 3+ = Частное лицо)
        role = "Бизнес" if partner.user_role_id and partner.user_role_id <= 2 else "Частное лицо"
        partner_info = {
            "id": partner.id,
            "name": partner.company_name or partner.name,
            "phone": partner.representative_phone,
            "company_name": partner.company_name,
            "role": role
        }
    
    return {
        "id": chat.id,
        "announcement_id": chat.announcement_id,
        "partner": partner_info,
        "messages": [
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "message_text": msg.message_text,
                "message_type": msg.message_type,
                "file_url": msg.file_url,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in sorted(chat.messages, key=lambda m: m.created_at or datetime.min)
        ]
    }