from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import text, String, Integer, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "interview"}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        unique=True,
        server_default=text("gen_random_uuid()"),
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    total_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )