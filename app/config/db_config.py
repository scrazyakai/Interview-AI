from typing_extensions import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
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

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

