from datetime import timedelta
from typing import Optional

from api.models import User
from api.serializers.user import (Token, UserCreate, UserRead, UserLogin)
from backend.db_config import get_session
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import (OAuth2PasswordBearer, OAuth2PasswordRequestForm,
                              )
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.jwt_token import (ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,
                             SECRET_KEY, create_access_token)

user_router = APIRouter(prefix="/users", tags=["users"])


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


@user_router.post("/", response_model=UserCreate)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    try:
        hashed_password = get_password_hash(data.password)
        new_user = User(username=data.username, password=hashed_password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except Exception as e:
        print(f'problem with creating user: {e}')
        raise e


#

@user_router.post("/login")
async def login_for_access_token(
    data: UserLogin,
    response: Response,
    session: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(session, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES*60,
        secure=False,
        samesite="Lax",
        path='/'

    )

    response_message = {
        "access_token": access_token,
        "token_type": "bearer",
        'cookie': response.headers.get('Set-Cookie')
    }

    return response_message



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











