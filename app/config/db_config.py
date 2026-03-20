from contextlib import asynccontextmanager
from typing_extensions import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm.session import sessionmaker

ASYNC_DB_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres"

async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=True,
    pool_size=10,
    max_overflow=10,
    connect_args={
        "server_settings": {
            "search_path": "interview"
        }
    },
)

async_session = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_session():
    async with async_session() as session:
        yield session

# FastAPI dependency
async def get_session_dep():
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session_dep)]
