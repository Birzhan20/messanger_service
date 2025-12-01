import httpx
from core.config import settings


async def call_grok_model(message: str, user_id: str | None, conv_id: str | None) -> dict:
    if not settings.GROK_API_URL:
        raise RuntimeError("GROK_API_URL is not set")

    payload = {
        "message": message,
        "user_id": user_id,
        "conv_id": conv_id
    }

    headers = {}
    if settings.GROK_API_KEY:
        headers["Authorization"] = f"Bearer {settings.GROK_API_KEY}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(settings.GROK_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
