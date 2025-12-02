import httpx
from core.config import settings
from prompts import read_prompt


async def call_grok_model(message: str, user_id: str | None, conv_id: str | None) -> dict:
    if not settings.GROK_API_URL:
        raise RuntimeError("GROK_API_URL is not set")


    try:
        system_prompt = read_prompt().strip()
    except Exception as e:
        raise RuntimeError(f"Error reading system prompt: {e}")
    

    payload = {
        "model": "grok-4-fast-reasoning",
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }
    if settings.GROK_API_KEY:
        headers["Authorization"] = f"Bearer {settings.GROK_API_KEY}"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(settings.GROK_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
