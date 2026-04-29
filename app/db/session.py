from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


# 从环境变量读取数据库连接信息
ASYNC_DB_URL = settings.DATABASE_URL

if not ASYNC_DB_URL:
    raise ValueError(
        "Database URL not configured. Please set DATABASE_URL or ASYNC_DB_URL environment variable. "
        "Example: postgresql+asyncpg://user:password@host:port/database"
    )

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

