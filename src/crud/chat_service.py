from datetime import datetime
from sqlalchemy import select, update, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, aliased
from fastapi import HTTPException, status

from models.chat import Chat
from models.announcement import Announcement
from models.messages import Message
from models.user import User


async def get_or_create_chat(announcement_id: int, buyer_id: int, seller_id: int, db: AsyncSession):
    """Создаёт или возвращает существующий чат (как в мессенджере: 1 чат = 1 покупатель + 1 продавец + 1 объявление)"""

    result = await db.execute(
        select(Chat).where(
            Chat.announcement_id == announcement_id,
            Chat.seller_id == seller_id,
            Chat.buyer_id == buyer_id
        )
    )
    chat = result.scalar_one_or_none()

    if chat:
        return chat

    # Проверяем, существует ли объявление
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()
    print(announcement.user_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Объявление не найдено")

    # Проверяем, что seller_id действительно владелец объявления (безопасность!)
    if announcement.user_id != seller_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь владельцем этого объявления")

    chat = Chat(
        announcement_id=announcement_id,
        seller_id=seller_id,
        buyer_id=buyer_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(chat)
    await db.flush()
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


async def get_user_chats(db: "AsyncSession", user_id: int, tab: str = "all", search_query: str = None):
    """Все чаты пользователя (покупатель или продавец)"""
    seller_alias = aliased(User)
    buyer_alias = aliased(User)

    # Базовый запрос
    query = (
        select(
            Chat,
            func.count(Message.id).filter(
                Message.is_read == False,
                Message.sender_id != user_id
            ).label("unread_count"),
            seller_alias,
            buyer_alias
        )
        .join(Announcement, Chat.announcement_id == Announcement.id)
        .join(seller_alias, Announcement.user_id == seller_alias.id)
        .join(buyer_alias, Chat.buyer_id == buyer_alias.id)
        .outerjoin(Message, Chat.id == Message.chat_id)
        .group_by(Chat.id, Announcement.id, seller_alias.id, buyer_alias.id)
        .order_by(Chat.last_message_at.desc().nulls_last())
    )

    if tab == "buying":
        query = query.where(Chat.buyer_id == user_id)
    elif tab == "selling":
        query = query.where(Announcement.user_id == user_id)
    else:
        query = query.where(
            or_(
                Chat.buyer_id == user_id,
                Announcement.user_id == user_id
            )
        )

    result = await db.execute(query)
    rows = result.all()

    chats_data = []
    for chat, unread_count, seller, buyer in rows:
        # Определяем партнера
        if chat.buyer_id == user_id:
            partner = seller
        else:
            partner = buyer

        if search_query and search_query.lower() not in partner.name.lower():
            continue

        chats_data.append({
            "id": chat.id,
            "partner_id": partner.id,
            "partner_name": partner.name,
            "partner_avatar": None,
            "partner_phone": partner.representative_phone,
            "partner_role_id": partner.user_role_id,
            "last_message": chat.last_message_text,
            "last_message_type": chat.last_message_type,
            "last_message_at": chat.last_message_at,
            "unread_count": unread_count,
            "is_online": False
        })

    return chats_data


async def get_chat_with_messages(chat_id: int, user_id: int, db: AsyncSession):
    """Открыть чат + историю + отметить прочитанными"""
    seller_alias = aliased(User)
    buyer_alias = aliased(User)

    result = await db.execute(
        select(Chat, seller_alias, buyer_alias)
        .join(Announcement, Chat.announcement_id == Announcement.id)
        .join(seller_alias, Announcement.user_id == seller_alias.id)
        .join(buyer_alias, Chat.buyer_id == buyer_alias.id)
        .options(
            selectinload(Chat.messages).selectinload(Message.sender)
        )
        .where(
            Chat.id == chat_id,
            or_(
                Chat.buyer_id == user_id,
                Announcement.user_id == user_id
            )
        )
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Чат не найден или доступ запрещён")

    chat, seller, buyer = row

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

    # Определяем партнера
    if chat.buyer_id == user_id:
        partner = seller
    else:
        partner = buyer

    return {
        "id": chat.id,
        "announcement_id": chat.announcement_id,
        "partner_id": partner.id,
        "partner_name": partner.name,
        "partner_avatar": None,
        "partner_phone": partner.representative_phone,
        "partner_role_id": partner.user_role_id,
        "partner_online": False,
        "messages": chat.messages
    }