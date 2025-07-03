from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.models import Base
from api.views.messages import messages_router
from backend.db_config import engine, get_session
from api.views.users import user_router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

origins = [
    "http://localhost:5173",  # Vite
    "http://127.0.0.1:5173",
    "http://localhost:",  # React
]

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api")
app.include_router(messages_router, prefix="/api")
