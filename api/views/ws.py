import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from api.models import User, Message
from backend.db_config import get_session
from utils.post_message_permission import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession



websocket_router = APIRouter(prefix='/ws')
active_connections = set()

@websocket_router.websocket("/wss")
async def websocket_message(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            content = data.get("content")

            if not content:
                continue

            # Сохраняем сообщение в БД
            message = Message(
                content=content,
                sender_id=current_user.id,
                created=datetime.now()
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)

            # Формируем сообщение
            msg_out = {
                "id": message.id,
                "content": message.content,
                "created": message.created.isoformat(),
                "sender": current_user.username,
            }

            # Рассылаем всем подключённым
            for conn in active_connections:
                await conn.send_text(json.dumps(msg_out))

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Пользователь {current_user.username} отключился")

@websocket_router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")