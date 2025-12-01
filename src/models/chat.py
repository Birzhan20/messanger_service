from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, String, Index, Integer
from sqlalchemy.orm import relationship

from core.database import Base


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    announcement_id = Column(BigInteger, ForeignKey('announcements.id'), nullable=False)
    seller_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    buyer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_message_text = Column(String(255), nullable=True)
    last_message_type = Column(String(20), default='text')
    last_message_at = Column(DateTime, nullable=True)

    announcement = relationship("Announcement", back_populates="chats")
    seller = relationship("User", back_populates="seller_chats", foreign_keys=[seller_id])
    buyer = relationship("User", back_populates="buyer_chats", foreign_keys=[buyer_id])
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

    __table_args__ = (
        Index(
            'ix_unique_chat_per_ad_buyer',
            'announcement_id', 'seller_id', 'buyer_id',
            unique=True
        ),
    )