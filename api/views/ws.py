import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from api.models import User, Message
from api.serializers.message import MessageUpdate, MessageRead
from api.serializers.user import UserRead
from backend.db_config import get_session
from utils.post_message_permission import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession


websocket_router = APIRouter(prefix='/ws')


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()


@websocket_router.websocket('/')
async def websocket_endpoint(
        websocket: WebSocket,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content")
            if not content:
                continue

            message = Message(
                content=content,
                created=datetime.utcnow(),
                sender_id=current_user.id,
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)

            message_dto = MessageRead(
                id=message.id,
                content=message.content,
                created=message.created,
                sender=UserRead(
                    id=current_user.id,
                    username=current_user.username,
                ),
            )

            await manager.broadcast(message_dto.dict())

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        await manager.disconnect(websocket)
        print(e)


