from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.models import User
from backend.db_config import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")

SECRET_KEY = "твой-секретный-ключ"
ALGORITHM = "HS256"

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await session.execute(select(User).where(User.username == username))
        user = user.scalar_one_or_none()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception








