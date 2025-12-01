from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    message_text: Optional[str]
    message_type: str
    file_url: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    id: int
    partner_id: int
    partner_name: str
    partner_avatar: Optional[str]
    partner_phone: Optional[str]
    partner_role_id: Optional[int]
    last_message: Optional[str]
    last_message_type: str
    last_message_at: Optional[datetime]
    unread_count: int
    is_online: bool = False

    class Config:
        from_attributes = True


class ChatDetailResponse(BaseModel):
    id: int
    announcement_id: int
    partner_id: int
    partner_name: str
    partner_avatar: Optional[str]
    partner_phone: Optional[str]
    partner_role_id: Optional[int]
    partner_online: bool = False
    messages: List[MessageResponse]

    class Config:
        from_attributes = True
