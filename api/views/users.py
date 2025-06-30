from http.client import HTTPException
from os import access
from typing import Annotated
from api.serializers.user import Token

from fastapi import APIRouter, Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import User
from backend.db_config import get_session

from api.serializers.user import UserRead, UserCreate, UserLogin, oauth2_scheme
from utils.jwt_token import create_access_token

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/ping")
async def ping():
    return {"ping": "pong"}


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



@user_router.post("/", response_model=UserCreate)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        hashed_password = hash_password(data.password)
        new_user = User(username=data.username, password=hashed_password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except Exception as e:
        print(f'problem with creating user: {e}')
        raise e


#

@user_router.post("/login", response_model=Token)
async def login_user(data: UserLogin, session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(User).filter_by(username=data.username))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(data.password, user.password):
            raise HTTPException(status_code=404, detail="Incorrect password")

        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
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











