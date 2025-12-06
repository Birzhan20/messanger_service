import pytest
from unittest.mock import MagicMock, Mock, patch, AsyncMock
from pathlib import Path
import core.config

from src.crud import support as crud_support
from src.services import grok as services_grok
from src.prompts import read_prompt, write_prompt, upload_prompt


# CRUD unit tests

@pytest.mark.asyncio
async def test_get_or_create_room_existing():
    room = crud_support.Room(id=1, user_id=42)

    scalars_result = MagicMock()
    scalars_result.first.return_value = room

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_result

    db = AsyncMock()
    db.execute = AsyncMock(return_value=execute_result)

    result = await crud_support.get_or_create_room(42, db)

    assert result == room

@pytest.mark.asyncio
async def test_get_or_create_room_new():
    db = AsyncMock()

    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = None
    db.execute.return_value = fake_result

    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = AsyncMock()

    result = await crud_support.get_or_create_room(99, db)

    assert result.user_id == 99
    db.commit.assert_awaited()
    db.refresh.assert_awaited()
    db.add.assert_awaited()



@pytest.mark.asyncio
async def test_save_message():
    db = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = Mock()

    msg = await crud_support.save_message(
        room_id=1,
        sender=crud_support.SenderType.user,
        message="Hello",
        db=db
    )

    assert msg.message == "Hello"
    db.commit.assert_awaited()
    db.refresh.assert_awaited()


# Grok unit tests

import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch("src.services.grok.settings")
@patch("src.services.grok.read_prompt", return_value="system prompt")
@patch("httpx.AsyncClient")
async def test_call_grok_model(mock_client, mock_read_prompt, mock_settings):
    mock_settings.GROK_API_URL = "http://fake.url"
    mock_settings. GROK_API_KEY = None  

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"reply": "Hi"})
    mock_response.raise_for_status = Mock()

    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

    from src.services import grok as services_grok

    result = await services_grok.call_grok_model("Hello", "42", [])

    assert result == {"reply": "Hi"}
    assert result["reply"] == "Hi"

    mock_read_prompt.assert_called_once()
    mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
        mock_settings.GROK_API_URL,
        json={
            "model": "grok-4-fast-reasoning",
            "stream": False,
            "messages": [{"role": "system", "content": "system prompt"}, {"role": "user", "content": "Hello"}],
        },
        headers={"Content-Type": "application/json"},
    )



# Prompts unit tests

def test_read_prompt_cached():
    mock_redis = MagicMock()
    mock_redis.get.return_value = "cached prompt"

    with patch("src.prompts.get_redis", return_value=mock_redis):
        result = read_prompt()

    assert result == "cached prompt"
    mock_redis.get.assert_called_once_with("support_prompt")

@patch("src.prompts.settings")
@patch("src.prompts.get_redis")
@patch("pathlib.Path.write_text")
def test_write_prompt(mock_write, mock_get_redis, mock_settings):
    mock_settings.SUPPORT_PROMPT_PATH = "test_prompt.txt"

    mock_redis = MagicMock()
    mock_get_redis.return_value = mock_redis

    write_prompt("hello")

    mock_write.assert_called_once()
    mock_redis.set.assert_called_once_with("support_prompt", "hello")


def test_upload_prompt():
    mock_redis = MagicMock()

    temp = Path("temp.txt")
    temp.write_text("abc")

    with patch("src.prompts.get_redis", return_value=mock_redis), \
         patch("src.prompts.settings") as mock_settings, \
         patch("pathlib.Path.write_text") as mock_write:
        
        mock_settings.SUPPORT_PROMPT_PATH = "test_prompt.txt"

        result = upload_prompt(temp)

        assert result == "abc"
        mock_write.assert_called_once()
        mock_redis.set.assert_called_once_with("support_prompt", "abc")