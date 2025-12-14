from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.support import SenderType


class ChatRequest(BaseModel):
    """Запрос на отправку сообщения в поддержку."""
    user_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    """Ответ от поддержки."""
    reply: Optional[str]
    raw: Optional[dict] = None


class UpdatePromptRequest(BaseModel):
    """Запрос на обновление промпта."""
    content: str


class SupportMessageOut(BaseModel):
    """Формат сообщения поддержки для вывода."""
    id: int
    sender: SenderType
    message: str
    created_at: datetime

    class Config:
        orm_mode = True
