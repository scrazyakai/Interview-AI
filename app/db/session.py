from time import perf_counter

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.log import get_logger

log = get_logger(__name__)

ASYNC_DB_URL = settings.DATABASE_URL

if not ASYNC_DB_URL:
    raise ValueError(
        "Database URL not configured. Please set DATABASE_URL or ASYNC_DB_URL environment variable. "
        "Example: postgresql+asyncpg://user:password@host:port/database"
    )

async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    pool_size=10,
    max_overflow=10,
    connect_args={
        "server_settings": {
            "search_path": "interview",
        }
    },
)


@event.listens_for(async_engine.sync_engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany) -> None:
    conn.info.setdefault("query_start_time", []).append(perf_counter())
    log.info(
        "[sql] start: statement=%s parameters=%s executemany=%s",
        statement,
        parameters,
        executemany,
    )


@event.listens_for(async_engine.sync_engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany) -> None:
    start_time = conn.info.get("query_start_time", []).pop() if conn.info.get("query_start_time") else None
    duration_ms = (perf_counter() - start_time) * 1000 if start_time is not None else -1
    log.info(
        "[sql] done: rowcount=%s duration_ms=%.2f statement=%s",
        cursor.rowcount,
        duration_ms,
        statement,
    )


AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
