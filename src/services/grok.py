import logging
import json
import httpx
from core.config import settings
from services.prompts import read_prompt
from models.support import SupportChat, SenderType
from sqlalchemy.ext.asyncio import AsyncSession
from services.get_user_info_ai import get_user_ai_context

logger = logging.getLogger("services.grok")


async def call_grok_model(
    message: str,
    user_id: int | None = None,
    db: AsyncSession | None = None,
    history: list[SupportChat] | None = None,
    debug_return_payload: bool = False
) -> dict:
    """
    Отправляет запрос к Grok API и возвращает ответ.
    Автоматически выставляет 'handover': True, если нужно подключить человека.
    """

    if not settings.GROK_API_URL:
        logger.error("Не задан GROK_API_URL в настройках")
        raise RuntimeError("GROK_API_URL is not set")

    try:
        system_prompt = read_prompt().strip()
    except Exception as e:
        logger.exception(f"Ошибка при чтении системного prompt: {e}")
        raise RuntimeError(f"Ошибка при чтении системного prompt: {e}")

    # Подгружаем контекст пользователя
    user_context = {}
    if user_id and db:
        try:
            user_context = await get_user_ai_context(user_id, db)
            logger.debug(f"Подгружен контекст пользователя user_id={user_id}")
        except Exception as e:
            logger.warning(f"Не удалось получить контекст для user_id={user_id}: {e}")

    messages_payload = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"USER_CONTEXT: {user_context}"}
    ]

    if history:
        for msg in history:
            role = "user" if msg.sender == SenderType.user else "assistant"
            messages_payload.append({"role": role, "content": msg.message})
        logger.debug(f"Добавлено {len(history)} сообщений из истории для user_id={user_id}")

    messages_payload.append({"role": "user", "content": message})

    payload = {
        "model": "grok-4-1-fast-non-reasoning",
        "stream": False,
        "messages": messages_payload
    }

    logger.info(f"Payload для Grok (user_id={user_id}):\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    if debug_return_payload:
        logger.info("DEBUG: возвращаем payload без запроса к Grok")
        return payload

    headers = {"Content-Type": "application/json"}
    if settings.GROK_API_KEY:
        headers["Authorization"] = f"Bearer {settings.GROK_API_KEY}"

    logger.info(f"Отправка запроса к модели Grok для user_id={user_id} с {len(messages_payload)} сообщениями")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(settings.GROK_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            logger.debug(f"Ответ от Grok для user_id={user_id}: {result}")

            # --- Автоматическая логика handover ---
            user_request_for_human = any(
                kw in message.lower() for kw in ["человек", "оператор", "живой агент", "поговорить с человеком"]
            )
            if user_request_for_human:
                logger.info(f"user_id={user_id} запросил живого оператора — выставляем handover=True")
                result["handover"] = True
                result["reply"] = "Подключаю модератора к чату, пожалуйста, ожидайте несколько секунд."

            return result
        except httpx.HTTPStatusError as e:
            logger.exception(f"HTTP ошибка при вызове Grok для user_id={user_id}: {e}")
            raise
        except httpx.RequestError as e:
            logger.exception(f"Ошибка запроса к Grok для user_id={user_id}: {e}")
            raise
