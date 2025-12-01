from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    message: str
    conv_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    raw: Optional[dict] = None

class UpdatePromptRequest(BaseModel):
    content: str