from datetime import datetime
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import String, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlmodel import SQLModel, Field, Session
from typing import Optional
from typing_extensions import Annotated

from app.models import user

app = FastAPI()

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


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "interview"}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[UUID] = Field(
        sa_type=PG_UUID(as_uuid=True),
        nullable=False,
        unique=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    username: str = Field(sa_type=String(50), nullable=False, unique=True)
    password_hash: str = Field(sa_type=String(255), nullable=False)
    avatar_url: Optional[str] = Field(default=None, sa_type=String(255))
    created_at: datetime = Field(
        sa_type=TIMESTAMP,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )
    updated_at: datetime = Field(
        sa_type=TIMESTAMP,
        nullable=False,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
    )


# 用户创建请求模型（只包含需要客户端提供的字段）
class UserCreate(SQLModel):
    username: str
    password_hash: str
    avatar_url: Optional[str] = None


# 用户响应模型（包含所有返回字段）
class UserRead(SQLModel):
    username: str
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


async def get_session():
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.post("/users/", response_model=UserRead)
async def create_user(user_data: UserCreate, session: SessionDep):
    # 创建数据库记录，只设置客户端提供的字段
    db_user = User(
        username=user_data.username,
        password_hash=user_data.password_hash,
        avatar_url=user_data.avatar_url,
        # id、user_id、created_at、updated_at 由数据库自动生成
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@app.get("/users/{id}", response_model=UserRead)
async def get_user(id: int, session: SessionDep):
    user = await session.get(User,id)
    user_read = user.model_validate(user)
    return user_read
@app.post("/users/delete/{id}")
async def delete_user(id: int, session: SessionDep):
    db_user = await session.get(User,id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await session.delete(db_user)
    await session.commit()
    return True;
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}