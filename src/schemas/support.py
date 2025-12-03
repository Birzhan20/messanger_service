from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ChatRequest(BaseModel):
    user_id: Optional[int] = None
    message: str

class ChatResponse(BaseModel):
    reply: str
    raw: Optional[dict] = None

class UpdatePromptRequest(BaseModel):
    content: str

class SenderType(str, Enum):
    user = "user"
    assistant = "assistant"

class SupportMessageOut(BaseModel):
    id: int
    sender: SenderType
    message: str
    created_at: datetime

    class Config:
        orm_mode = True