from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.future import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.models import Message, User
from api.serializers.message import MessageRead, MessageCreate
from backend.db_config import get_session
from utils.post_message_permission import get_current_user

messages_router = APIRouter(prefix="/messages", tags=["messages"])


@messages_router.get('/ping')
async def ping():
    return {"ping": "pong"}


@messages_router.get('/', response_model=list[MessageRead])
async def get_messages(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Message).options(joinedload(Message.sender)).order_by(desc(Message.id))
    )
    messages = result.scalars().all()
    return messages[:3]


@messages_router.post('/', response_model=MessageRead)
async def create_message(
        data: MessageCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    new_message = Message(content=data.content, sender_id=current_user.id)
    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)

    # Дополнительный запрос, чтобы загрузить sender вместе с сообщением
    result = await session.execute(
        select(Message)
        .options(joinedload(Message.sender))
        .where(Message.id == new_message.id)
    )
    message_with_sender = result.scalar_one()

    return message_with_sender


# @messages_router.post('/', response_model=MessageRead)
# async def create_message(data: MessageCreate, session: AsyncSession = Depends(get_session)):
#     new_message = Message(content=data.content, sender_id=data.sender_id)
#     session.add(new_message)
#     await session.commit()
#     await session.refresh(new_message)
#     # Принудительно загрузить sender
#     await session.refresh(new_message, attribute_names=["sender"])
#     return new_message