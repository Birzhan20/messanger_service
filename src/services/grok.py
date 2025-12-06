import logging
import httpx
from core.config import settings
from prompts import read_prompt
from models.support import SupportChat, SenderType

logger = logging.getLogger("services.grok")

async def call_grok_model(
    message: str,
    user_id: str | None = None,
    history: list[SupportChat] | None = None
) -> dict:
    if not settings.GROK_API_URL:
        logger.error("Не задан GROK_API_URL в настройках")
        raise RuntimeError("GROK_API_URL is not set")

    try:
        system_prompt = read_prompt().strip()
    except Exception as e:
        logger.exception(f"Ошибка при чтении системного prompt: {e}")
        raise RuntimeError(f"Ошибка при чтении системного prompt: {e}")

    messages_payload = [{"role": "system", "content": system_prompt}]
    if history:
        for msg in history:
            role = "user" if msg.sender == SenderType.user else "assistant"
            messages_payload.append({"role": role, "content": msg.message})
        logger.debug(f"Добавлено {len(history)} сообщений из истории для user_id={user_id}")
    messages_payload.append({"role": "user", "content": message})

    payload = {"model": "grok-4-fast-reasoning", "stream": False, "messages": messages_payload}
    headers = {"Content-Type": "application/json"}
    if settings.GROK_API_KEY:
        headers["Authorization"] = f"Bearer {settings.GROK_API_KEY}"

    logger.info(f"Отправка запроса к модели Grok для user_id={user_id} с {len(messages_payload)} сообщениями")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(settings.GROK_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            result = await resp.json()
            logger.debug(f"Ответ от Grok для user_id={user_id}: {result}")
            return result
        except httpx.HTTPStatusError as e:
            logger.exception(f"HTTP ошибка при вызове Grok для user_id={user_id}: {e}")
            raise
        except httpx.RequestError as e:
            logger.exception(f"Ошибка запроса к Grok для user_id={user_id}: {e}")
            raise
