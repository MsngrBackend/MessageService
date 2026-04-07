from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from src.repository.chatRepo import ChatRepository
from src.service.message_service import add_message
from src.nats_bus import notify_chat_event, publish_user_status
from .db import get_db

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        # Хранение активных соединений в виде {chat_id: {user_id: WebSocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int, user_id: str):
        """
        Устанавливает соединение с пользователем.
        websocket.accept() — подтверждает подключение.
        """
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = {}
        self.active_connections[chat_id][user_id] = websocket

    def disconnect(self, chat_id: int, user_id: str):
        """
        Закрывает соединение и удаляет его из списка активных подключений.
        Если в комнате больше нет пользователей, удаляет комнату.
        """
        if chat_id in self.active_connections and user_id in self.active_connections[chat_id]:
            del self.active_connections[chat_id][user_id]
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast_typing(self, chat_id: int, sender_id: str):
        """
        Рассылает сообщение всем пользователям в комнате.
        """
        if chat_id in self.active_connections:
            for user_id, connection in self.active_connections[chat_id].items():
                typer = {
                    "sender_id": sender_id
                }
                await connection.send_json(typer)

    async def broadcast_message(self, message: str, chat_id: int, sender_id: str):
        """
        Рассылает сообщение всем пользователям в комнате.
        """
        if chat_id in self.active_connections:
            for user_id, connection in self.active_connections[chat_id].items():
                new_message = {
                    "text": message,
                    "sender_id": sender_id
                }
                await connection.send_json(new_message)


manager = ConnectionManager()


async def dispatch_chat_event(data: dict[str, Any]) -> None:
    """Локальная доставка события чата в WebSocket клиентам этого инстанса."""
    chat_id = int(data["chat_id"])
    etype = data.get("type")
    if etype == "message":
        await manager.broadcast_message(data["text"], chat_id, data["sender_id"])
    elif etype == "typing":
        await manager.broadcast_typing(chat_id, data["sender_id"])
    elif etype == "system":
        await manager.broadcast_message(data["text"], chat_id, data["sender_id"])


@router.websocket("/{chat_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    user_id: str,
    username: str,
    db: AsyncSession = Depends(get_db),
):
    chat_repo = ChatRepository(db)
    member = await chat_repo.get_member(chat_id, user_id)
    if not member:
        await websocket.close()
        return

    await manager.connect(websocket, chat_id, user_id)
    await publish_user_status(user_id, "online")
    await notify_chat_event(
        chat_id,
        {
            "type": "system",
            "text": f"{username} (ID: {user_id}) присоединился к чату.",
            "sender_id": user_id,
        },
    )

    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "message":
                await add_message(db, chat_id, data["text"], user_id)
                await notify_chat_event(
                    chat_id,
                    {"type": "message", "text": data["text"], "sender_id": user_id},
                )

            elif data["type"] == "typing":
                await notify_chat_event(
                    chat_id,
                    {"type": "typing", "sender_id": user_id},
                )

    except WebSocketDisconnect:
        manager.disconnect(chat_id, user_id)
        await publish_user_status(user_id, "offline")
        await notify_chat_event(
            chat_id,
            {
                "type": "system",
                "text": f"{username} (ID: {user_id}) покинул чат.",
                "sender_id": user_id,
            },
        )
