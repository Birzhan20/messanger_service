from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PartnerInfo(BaseModel):
    """Информация о партнёре в чате."""
    id: int
    name: str
    phone: Optional[str] = Field(None, description="Номер телефона партнёра")
    company_name: Optional[str] = None
    role: str = Field(description="Роль: 'Бизнес' или 'Частное лицо'")
    
    class Config:
        from_attributes = True


class MessageItem(BaseModel):
    """Сообщение в чате."""
    id: int
    sender_id: int
    message_text: Optional[str] = None
    message_type: str = "text"
    file_url: Optional[str] = None
    is_read: bool = False
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChatListItem(BaseModel):
    """Элемент списка чатов."""
    id: int
    partner: PartnerInfo
    announcement_title: Optional[str] = None
    last_message_text: Optional[str] = None
    last_message_type: str = "text"
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
    
    class Config:
        from_attributes = True


class ChatDetail(BaseModel):
    """Детальная информация о чате с историей сообщений."""
    id: int
    partner: PartnerInfo
    announcement_id: int
    announcement_title: Optional[str] = None
    messages: List[MessageItem] = []
    
    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    """Запрос на отправку сообщения."""
    text: Optional[str] = None
    
    
class WebSocketMessage(BaseModel):
    """Формат WebSocket сообщения."""
    type: str = Field(description="Тип: 'message', 'pong', 'error'")
    data: Optional[dict] = None
