from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from models.support import Room, SupportChat, SenderType


async def get_or_create_room(user_id: int, db: AsyncSession):
    q = select(Room).where(Room.user_id == user_id).order_by(desc(Room.created_at))
    room = (await db.execute(q)).scalars().first()

    if room:
        return room

    room = Room(user_id=user_id)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def get_last_messages(room_id: int, db: AsyncSession, limit: int = 20):
    q = (
        select(SupportChat)
        .where(SupportChat.room_id == room_id)
        .order_by(desc(SupportChat.created_at))
        .limit(limit)
    )
    result = await db.execute(q)
    msgs = result.scalars().all()
    return list(reversed(msgs))


async def save_message(room_id: int, sender: SenderType, message: str, db: AsyncSession):
    msg = SupportChat(
        room_id=room_id,
        sender=sender,
        message=message
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg
