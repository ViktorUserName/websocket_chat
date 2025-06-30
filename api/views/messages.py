from fastapi import APIRouter, Depends
from sqlalchemy.future import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.models import Message
from api.serializers.message import MessageRead, MessageCreate
from backend.db_config import get_session

messages_router = APIRouter(prefix="/messages", tags=["messages"])


@messages_router.get('/ping')
async def ping():
    return {"ping": "pong"}


@messages_router.get('/', response_model=list[MessageRead])
async def get_messages(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Message).options(joinedload(Message.sender))
    )
    messages = result.scalars().all()
    return messages


@messages_router.post('/', response_model=MessageRead)
async def create_message(data: MessageCreate, session: AsyncSession = Depends(get_session)):
    new_message = Message(content=data.content, sender_id=data.sender_id)
    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)
    # Принудительно загрузить sender
    await session.refresh(new_message, attribute_names=["sender"])
    return new_message
