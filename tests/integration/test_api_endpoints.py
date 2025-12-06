import pytest
from unittest.mock import AsyncMock
from fastapi import FastAPI
from httpx import AsyncClient
from models.support import Room
from api import support as api_support
from crud import support as crud_support
from services import grok as services_grok

# -------------------
# FastAPI App
# -------------------
app = FastAPI()
app.include_router(api_support.router)

# -------------------
# Integration Tests
# -------------------
@pytest.mark.asyncio
async def test_get_chat_endpoint(monkeypatch):
    monkeypatch.setattr(crud_support, "get_or_create_room", lambda user_id, db: Room(id=1, user_id=user_id))
    monkeypatch.setattr(crud_support, "get_last_messages", lambda room_id, db, limit=20: [])

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/support/chat/42")
        assert response.status_code == 200
        assert response.json() == []

@pytest.mark.asyncio
async def test_support_chat_endpoint(monkeypatch):
    monkeypatch.setattr(crud_support, "get_or_create_room", lambda user_id, db: Room(id=1, user_id=user_id))
    monkeypatch.setattr(crud_support, "save_message", AsyncMock())
    monkeypatch.setattr(crud_support, "get_last_messages", AsyncMock(return_value=[]))
    monkeypatch.setattr(services_grok, "call_grok_model", AsyncMock(return_value={"reply": "Hello"}))

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/support/chat", json={"user_id": 42, "message": "Hi"})
        assert response.status_code == 200
        assert response.json()["reply"] == "Hello"

@pytest.mark.asyncio
async def test_get_prompt_endpoint(monkeypatch):
    monkeypatch.setattr("prompts.read_prompt", lambda: "Prompt content")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/support/prompt")
        assert response.status_code == 200
        assert response.json()["content"] == "Prompt content"

@pytest.mark.asyncio
async def test_update_prompt_endpoint(monkeypatch):
    monkeypatch.setattr("prompts.write_prompt", lambda content: None)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/support/prompt", json={"content": "New prompt"})
        assert response.status_code == 204

@pytest.mark.asyncio
async def test_upload_prompt_endpoint(tmp_path, monkeypatch):
    prompt_file = tmp_path / "upload.txt"
    prompt_file.write_text("Upload content")
    monkeypatch.setattr("prompts.upload_prompt", lambda path: "Upload content")

    async with AsyncClient(app=app, base_url="http://test") as ac:
        with open(prompt_file, "rb") as f:
            response = await ac.post("/support/prompt/upload", files={"file": ("upload.txt", f, "text/plain")})
        assert response.status_code == 201
        assert response.json()["content_length"] == len("Upload content")
