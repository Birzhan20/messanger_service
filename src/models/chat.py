from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, String, Index
from sqlalchemy.orm import relationship

from src.core.database import Base


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(BigInteger, primary_key=True)
    announcement_id = Column(BigInteger, ForeignKey('announcements.id'), nullable=False)
    buyer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_message_text = Column(String(255), nullable=True)
    last_message_type = Column(String(20), default='text')
    last_message_at = Column(DateTime, nullable=True)

    ad = relationship("Announcement", back_populates="chats")
    buyer = relationship("User", back_populates="buyer_chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_unique_chat', 'announcement_id', 'buyer_id', unique=True),
    )