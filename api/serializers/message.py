from pydantic import BaseModel

from api.serializers.user import UserRead


class MessageCreate(BaseModel):
    content: str



class MessageUpdate(BaseModel):
    content: str
    sender_id: int


class MessageRead(BaseModel):
    id: int
    content: str
    sender: UserRead

    class Config:
        from_attributes = True