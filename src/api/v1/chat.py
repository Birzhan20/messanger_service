from typing import List, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from crud.chat_service import (
    get_or_create_chat, send_message, get_user_chats, get_chat_with_messages
)
from schemas.chat import ChatListResponse, ChatDetailResponse, MessageResponse
from core.s3 import upload_to_s3

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/start/{announcement_id}")
async def start_chat(announcement_id: int, buyer_id: int, seller_id: int, db: AsyncSession = Depends(get_db)):
    chat = await get_or_create_chat(announcement_id, buyer_id, seller_id, db)
    return {"chat_id": chat.id}


@router.get("/my", response_model=List[ChatListResponse])
async def my_chats(
    user_id: int,
    tab: str = Query("all", enum=["all", "buying", "selling"]),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    chats = await get_user_chats(db=db, user_id=user_id, tab=tab, search_query=search)
    return chats


@router.get("/{chat_id}", response_model=ChatDetailResponse)
async def open_chat(chat_id: int, user_id: int, db: AsyncSession = Depends(get_db),):
    chat_data = await get_chat_with_messages(db=db, chat_id=chat_id, user_id=user_id)
    return chat_data


@router.post("/{chat_id}/send", response_model=MessageResponse)
async def send(user_id: int, chat_id: int, text: str = None, file: UploadFile = File(None),
               db: AsyncSession = Depends(get_db)):
    file_url = None
    message_type = "text"

    if file:
        file_bytes = await file.read()
        file_url = await upload_to_s3(file_bytes, file.filename)
        content_type = file.content_type or ""
        if content_type.startswith("image/"):
            message_type = "image"
        elif content_type.startswith("video/"):
            message_type = "video"
        else:
            message_type = "document"

    message = await send_message(db=db, chat_id=chat_id, sender_id=user_id, text=text, file_url=file_url,
                                 message_type=message_type)
    return message