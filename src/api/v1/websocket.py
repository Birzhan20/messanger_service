from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from crud.chat_service import get_chat_with_messages

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Управляет WebSocket соединениями по chat_id."""

    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int):
        """Подключает WebSocket к чату."""
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = set()
        self.active_connections[chat_id].add(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: int):
        """Отключает WebSocket от чата."""
        if chat_id in self.active_connections:
            self.active_connections[chat_id].discard(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, chat_id: int, message: dict):
        """Отправляет сообщение всем подключенным к чату."""
        if chat_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[chat_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.add(connection)
            # Удаляем мёртвые соединения
            for dead in dead_connections:
                self.disconnect(dead, chat_id)


manager = ConnectionManager()


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    user_id: int = Query(...),
):
    """
    WebSocket endpoint для real-time сообщений в чате.
    
    Подключение: ws://host/ws/{chat_id}?user_id={user_id}
    
    Входящие сообщения (от клиента):
    - {"type": "ping"} - проверка соединения
    
    Исходящие сообщения (от сервера):
    - {"type": "message", "data": {...}} - новое сообщение
    - {"type": "pong"} - ответ на ping
    """
    # Проверяем доступ пользователя к чату
    async with get_db().__anext__() as db:
        try:
            await get_chat_with_messages(chat_id=chat_id, user_id=user_id, db=db)
        except Exception:
            await websocket.close(code=4003, reason="Access denied")
            return

    await manager.connect(websocket, chat_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)
    except Exception:
        manager.disconnect(websocket, chat_id)


def get_manager() -> ConnectionManager:
    """Возвращает singleton ConnectionManager для использования в других модулях."""
    return manager
