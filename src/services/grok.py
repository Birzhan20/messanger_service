import httpx
from core.config import settings
from prompts import read_prompt
from models.support import SupportChat, SenderType

async def call_grok_model(
    message: str,
    user_id: str | None = None,
    history: list[SupportChat] | None = None
) -> dict:
    if not settings.GROK_API_URL:
        raise RuntimeError("GROK_API_URL is not set")

    try:
        system_prompt = read_prompt().strip()
    except Exception as e:
        raise RuntimeError(f"Error reading system prompt: {e}")

    messages_payload = [
        {"role": "system", "content": system_prompt}
    ]

    if history:
        for msg in history:
            role = "user" if msg.sender == SenderType.user else "assistant"
            messages_payload.append({"role": role, "content": msg.message})

    messages_payload.append({"role": "user", "content": message})

    payload = {
        "model": "grok-4-fast-non-reasoning",
        "stream": False,
        "messages": messages_payload
    }

    headers = {"Content-Type": "application/json"}
    if settings.GROK_API_KEY:
        headers["Authorization"] = f"Bearer {settings.GROK_API_KEY}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(settings.GROK_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

