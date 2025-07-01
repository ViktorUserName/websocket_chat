from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    messages = relationship("Message", back_populates="sender")





class Message(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)

    sender_id = Column(Integer, ForeignKey("users.id"))
    sender = relationship("User", back_populates="messages")