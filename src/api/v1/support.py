from fastapi import APIRouter, HTTPException, status
from schemas.support import (
    ChatRequest,
    ChatResponse,
    UpdatePromptRequest
)
from services.grok import call_grok_model
from prompts import read_prompt, write_prompt

router = APIRouter(prefix="/support", tags=["Support"])


@router.post("/chat", response_model=ChatResponse)
async def support_chat(req: ChatRequest):
    try:
        base_prompt = read_prompt()
    except Exception as e:
        raise HTTPException(500, f"Prompt read error: {e}")

    full_msg = (base_prompt + "\n\n" if base_prompt.strip() else "") + req.message

    try:
        model_resp = await call_grok_model(
            full_msg,
            user_id=req.user_id,
            conv_id=req.conv_id
        )
    except Exception as e:
        raise HTTPException(500, f"Grok model error: {e}")

    reply = (
        model_resp.get("reply")
        or model_resp.get("text")
        or model_resp.get("message")
        or str(model_resp)
    )

    return ChatResponse(reply=reply, raw=model_resp)


@router.put("/prompt", status_code=status.HTTP_204_NO_CONTENT)
async def update_prompt(req: UpdatePromptRequest):
    try:
        write_prompt(req.content)
    except Exception as e:
        raise HTTPException(500, f"Prompt write error: {e}")


@router.get("/prompt")
async def get_prompt():
    try:
        content = read_prompt()
        return {"content": content}
    except Exception as e:
        raise HTTPException(500, f"Prompt read error: {e}")
