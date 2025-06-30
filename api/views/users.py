from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import User
from backend.db_config import get_session

from api.serializers.user import UserRead, UserCreate

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/ping")
async def ping():
    return {"ping": "pong"}

@user_router.post("/", response_model=UserCreate)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        new_user = User(username=data.username, password=data.password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except Exception as e:
        print(f'problem with creating user: {e}')
        raise e

@user_router.get("/", response_model=list[UserRead])
async def get_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users

@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    return user

# -----------

