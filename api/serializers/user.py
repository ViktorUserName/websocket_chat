from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/users/login",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)

class Token(BaseModel):
    access_token: str
    token_type: str