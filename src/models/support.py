import enum
from sqlalchemy import Column, Boolean, Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from core.database import Base


class SenderType(enum.Enum):
    user = "user"
    assistant = "assistant"


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    is_agent_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("SupportChat", back_populates="room")


class SupportChat(Base):
    __tablename__ = "support_chat"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("room.id", ondelete="CASCADE"))
    sender = Column(Enum(SenderType), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="messages")
