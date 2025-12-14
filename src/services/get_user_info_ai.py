from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from models import User, Announcement, Chat
from typing import Optional


async def get_user_ai_context(user_id: int, db) -> Optional[dict]:
    # 1. Данные пользователя
    user_query = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_query.scalar_one_or_none()
    if not user:
        return None

    # 2. Количество объявлений
    ann_count_query = await db.execute(
        select(func.count(Announcement.id))
        .where(Announcement.user_id == user_id)
    )
    announcement_count = ann_count_query.scalar() or 0

    # 3. Статусы чатов
    chats_query = await db.execute(
        select(Chat)
        .options(joinedload(Chat.messages))
        .where((Chat.seller_id == user_id) | (Chat.buyer_id == user_id))
        .order_by(Chat.last_message_at.desc())
    )
    chats = chats_query.unique().scalars().all()

    active_statuses = []
    for chat in chats:
        last_msg_type = chat.last_message_type or "text"
        last_msg_at = chat.last_message_at or datetime.utcnow()

        # Проверяем наличие непрочитанных сообщений от другого пользователя
        unread = any(m.sender_id != user_id and not m.is_read for m in chat.messages)

        active_statuses.append({
            "chat_id": chat.id,
            "has_unread": unread,
            "last_message_type": last_msg_type,
            "last_message_at": last_msg_at
        })

    # 4. Собираем всё в единый объект (без истории сообщений)
    return {
        "id": user.id,
        "email": user.email,
        "profile_type": user.user_role_id,
        "announcement_count": announcement_count,
        "active_statuses": active_statuses
    }



# from sqlalchemy import select, func
# from sqlalchemy.orm import joinedload

# from models import User, Announcement, Chat, Message


# async def get_user_ai_context(user_id: int, db):
#     # 1. Данные пользователя
#     user_query = await db.execute(
#         select(User).where(User.id == user_id)
#     )
#     user = user_query.scalar_one_or_none()

#     if not user:
#         return None

#     # 2. Количество объявлений
#     ann_count_query = await db.execute(
#         select(func.count(Announcement.id))
#         .where(Announcement.user_id == user_id)
#     )
#     announcement_count = ann_count_query.scalar() or 0

#     # 3. История обращений + статусы
#     chats_query = await db.execute(
#         select(Chat)
#         .options(
#             joinedload(Chat.messages)  # сразу подгружаем сообщения
#         )
#         .where((Chat.seller_id == user_id) | (Chat.buyer_id == user_id))
#         .order_by(Chat.last_message_at.desc())
#     )
#     chats = chats_query.unique().scalars().all()

#     history = []
#     active_statuses = []

#     for chat in chats:
#         # выбираем последние сообщения
#         messages = sorted(chat.messages, key=lambda m: m.created_at)

#         history.append({
#             "chat_id": chat.id,
#             "announcement_id": chat.announcement_id,
#             "role": "seller" if chat.seller_id == user_id else "buyer",
#             "last_message_text": chat.last_message_text,
#             "last_message_type": chat.last_message_type,
#             "last_message_at": chat.last_message_at,
#             "messages": [
#                 {
#                     "id": msg.id,
#                     "sender_id": msg.sender_id,
#                     "text": msg.message_text,
#                     "type": msg.message_type,
#                     "file_url": msg.file_url,
#                     "is_read": msg.is_read,
#                     "created_at": msg.created_at
#                 }
#                 for msg in messages
#             ]
#         })

#         # активный статус чата (если есть хотя бы одно непрочитанное)
#         unread = any(m.sender_id != user_id and m.is_read is False for m in messages)

#         active_statuses.append({
#             "chat_id": chat.id,
#             "has_unread": unread,
#             "last_message_type": chat.last_message_type,
#             "last_message_at": chat.last_message_at
#         })

#     # 4. Собираем всё в единый объект
#     return {
#         "id": user.id,
#         "email": user.email,
#         "profile_type": user.user_role_id,
#         "announcement_count": announcement_count,
#         "history": history,
#         "active_statuses": active_statuses
#     }
