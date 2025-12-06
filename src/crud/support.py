import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from models.support import Room, SupportChat, SenderType

logger = logging.getLogger("crud.support")


async def get_or_create_room(user_id: int, db: AsyncSession):
    logger.debug(f"Поиск комнаты для user_id={user_id}")
    q = select(Room).where(Room.user_id == user_id).order_by(desc(Room.created_at))
    room = (await db.execute(q)).scalars().first()

    if room:
        logger.debug(f"Найдена существующая комната id={room.id} для user_id={user_id}")
        return room

    room = Room(user_id=user_id)
    await db.add(room)
    await db.commit()
    await db.refresh(room)
    logger.info(f"Создана новая комната id={room.id} для user_id={user_id}")
    return room


async def get_last_messages(room_id: int, db: AsyncSession, limit: int = 20):
    logger.debug(f"Получение последних {limit} сообщений для room_id={room_id}")
    q = (
        select(SupportChat)
        .where(SupportChat.room_id == room_id)
        .order_by(desc(SupportChat.created_at))
        .limit(limit)
    )
    result = await db.execute(q)
    msgs = result.scalars().all()
    logger.debug(f"Получено {len(msgs)} сообщений для room_id={room_id}")
    return list(reversed(msgs))


async def save_message(room_id: int, sender: SenderType, message: str, db: AsyncSession):
    logger.debug(f"Сохранение сообщения для room_id={room_id}, отправитель={sender}")
    msg = SupportChat(
        room_id=room_id,
        sender=sender,
        message=message
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    logger.info(f"Сообщение сохранено id={msg.id} для room_id={room_id}")
    return msg
