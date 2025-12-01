from datetime import datetime

from sqlalchemy import BigInteger, Column, ForeignKey, String, Text, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship

from core.database import Base


class Message(Base):
    __tablename__ = 'messages'

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    chat_id = Column(BigInteger, ForeignKey('chats.id'), nullable=False)
    sender_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    message_text = Column(Text, nullable=True)
    message_type = Column(String(20), default='text')        # text, image, video, document
    file_url = Column(String(500), nullable=True)            # S3 url
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
