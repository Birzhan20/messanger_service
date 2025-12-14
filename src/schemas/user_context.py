from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MessageOut(BaseModel):
    id: int
    sender_id: int
    text: str = ""    
    type: str = "text"  
    file_url: Optional[str] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ChatHistoryItem(BaseModel):
    chat_id: int
    announcement_id: Optional[int] = None
    role: str
    last_message_text: str = ""
    last_message_type: str = "text"
    last_message_at: Optional[datetime] = None
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True


class ActiveStatusItem(BaseModel):
    chat_id: int
    has_unread: bool = False
    last_message_type: str = "text"
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserAIContextOut(BaseModel):
    id: int
    email: str
    profile_type: int
    announcement_count: int = 0
    history: List[ChatHistoryItem] = []
    active_statuses: List[ActiveStatusItem] = []

    class Config:
        from_attributes = True
