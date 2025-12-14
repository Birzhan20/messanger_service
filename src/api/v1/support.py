import logging
from fastapi import APIRouter, HTTPException, status, File, UploadFile, Depends
from schemas.support import ChatRequest, ChatResponse, UpdatePromptRequest, SupportMessageOut
from services.grok import call_grok_model
from services.prompts import read_prompt, write_prompt, upload_prompt
from pathlib import Path
from core.config import settings
from crud.support import get_or_create_room, get_last_messages, save_message
from core.database import get_db
from models.support import SenderType
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_context import UserAIContextOut
from services.get_user_info_ai import get_user_ai_context

logger = logging.getLogger("api.support")

router = APIRouter(prefix="/support", tags=["Support"])


@router.get("/chat/{user_id}", response_model=list[SupportMessageOut])
async def get_support_messages(user_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает историю сообщений поддержки."""
    logger.info(f"Запрос GET /chat/{user_id}")
    try:
        room = await get_or_create_room(user_id, db)
        messages = await get_last_messages(room.id, db)
        logger.debug(f"Получено {len(messages)} сообщений для room_id={room.id}")
        return messages
    except Exception as e:
        logger.exception(f"Ошибка при получении сообщений для user_id={user_id}: {e}")
        raise HTTPException(500, f"Внутренняя ошибка: {e}")


# @router.post("/chat", response_model=ChatResponse)
# async def support_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
#     """Отправляет сообщение в поддержку и возвращает ответ."""
#     logger.info(f"Запрос POST /chat user_id={req.user_id}")
#     if not req.user_id:
#         logger.warning("Отсутствует user_id в запросе")
#         raise HTTPException(400, "user_id is required")

#     room = await get_or_create_room(req.user_id, db)

#     await save_message(room_id=room.id, sender=SenderType.user, message=req.message, db=db)
#     logger.debug(f"Сохранено сообщение от пользователя для room_id={room.id}")

#     history = await get_last_messages(room.id, db)

#     try:
#         model_resp = await call_grok_model(message=req.message, user_id=req.user_id, history=history, db=db)
#     except Exception as e:
#         logger.exception(f"Ошибка модели Grok для user_id={req.user_id}: {e}")
#         raise HTTPException(500, f"Grok model error: {e}")

#     reply = model_resp.get("reply") or model_resp.get("text") or model_resp.get("message") or str(model_resp)

#     await save_message(room_id=room.id, sender=SenderType.assistant, message=reply, db=db)
#     logger.info(f"Отправлен ответ пользователю user_id={req.user_id} для room_id={room.id}")

#     return ChatResponse(reply=reply, raw=model_resp)


@router.put("/prompt", status_code=status.HTTP_204_NO_CONTENT)
async def update_prompt(req: UpdatePromptRequest):
    """Обновляет системный промпт."""
    logger.info("Запрос PUT /prompt на обновление")
    try:
        write_prompt(req.content)
        logger.info("Prompt успешно обновлён")
    except Exception as e:
        logger.exception(f"Ошибка при записи prompt: {e}")
        raise HTTPException(500, f"Prompt error: {e}")


@router.get("/prompt")
async def get_prompt():
    """Возвращает текущий системный промпт."""
    logger.info("Запрос GET /prompt")
    try:
        content = read_prompt()
        logger.debug(f"Прочитан prompt длиной {len(content)} символов")
        return {"content": content}
    except Exception as e:
        logger.exception(f"Ошибка при чтении prompt: {e}")
        raise HTTPException(500, f"Prompt read error: {e}")


@router.post("/prompt/upload", status_code=status.HTTP_201_CREATED)
async def upload_file_prompt(file: UploadFile = File(...)):
    """Загружает файл промпта (.txt, .md, .docx)."""
    logger.info(f"Запрос POST /prompt/upload файл={file.filename}")
    try:
        temp_path = Path(settings.SUPPORT_PROMPT_PATH).parent / file.filename
        content_bytes = await file.read()
        temp_path.write_bytes(content_bytes)
        content = upload_prompt(temp_path)
        logger.info(f"Файл {file.filename} загружен, длина контента: {len(content)}")
    except Exception as e:
        logger.exception(f"Ошибка при загрузке prompt: {e}")
        raise HTTPException(500, f"Prompt upload error: {e}")

    return {"filename": file.filename, "status": "uploaded", "content_length": len(content)}

@router.get("/ai-context/{user_id}", response_model=UserAIContextOut)
async def get_ai_context(user_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает AI-контекст пользователя: объявления, чаты, историю сообщений."""
    logger.info(f"GET /support/ai-context/{user_id}")

    try:
        result = await get_user_ai_context(user_id=user_id, db=db)
        if not result:
            logger.warning(f"User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")

        return result

    except Exception as e:
        logger.exception(f"Ошибка в get_user_ai_context для user_id={user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

from crud.support import activate_agent

from crud.support import get_or_create_room, get_last_messages, save_message, activate_agent, deactivate_agent

@router.post("/chat", response_model=ChatResponse)
async def support_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    logger.info(f"POST /chat user_id={req.user_id}")

    if not req.user_id:
        raise HTTPException(400, "user_id is required")

    # 1. Получаем или создаём комнату
    room = await get_or_create_room(req.user_id, db)

    # 2. Сохраняем сообщение пользователя
    await save_message(
        room_id=room.id,
        sender=SenderType.user,
        message=req.message,
        db=db
    )

    # 3. Если уже оператор — ИИ не участвует
    if room.is_agent_active:
        logger.info(f"Room {room.id} already handled by human")
        return ChatResponse(
            reply=None,
            raw={"status": "agent_active"}
        )

    # 4. История сообщений
    history = await get_last_messages(room.id, db)

    # 5. Вызов ИИ
    model_resp = await call_grok_model(
        message=req.message,
        user_id=req.user_id,
        history=history,
        db=db
    )

    # 6. HANDOVER — первым и без ответа ИИ
    if model_resp.get("handover") is True:
        service_msg = "Подключаю модератора к чату, пожалуйста, ожидайте несколько секунд."

        await save_message(
            room_id=room.id,
            sender=SenderType.assistant,
            message=service_msg,
            db=db
        )

        await activate_agent(room.id, db)
        logger.info(f"Room {room.id} switched to human agent")

        return ChatResponse(
            reply=service_msg,
            raw={"status": "agent_active"}
        )

    # 7. Обычный ответ ИИ
    reply = (
        model_resp.get("reply")
        or model_resp.get("text")
        or model_resp.get("message")
        or ""
    )

    await save_message(
        room_id=room.id,
        sender=SenderType.assistant,
        message=reply,
        db=db
    )

    return ChatResponse(
        reply=reply,
        raw=model_resp
    )

