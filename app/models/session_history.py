from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.db.base import Base


class MessageSourceEnum(str, enum.Enum):
    AI = "ai"
    USER = "user"


class SessionHistory(Base):
    __tablename__ = "session_history"
    __table_args__ = (
        Index("idx_session_history_session_created", "session_id", "created_at"),
        Index("idx_session_history_user_id", "user_id"),
        {"schema": "interview"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview.interview_sessions.session_uuid"),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview.users.user_id"),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    message_source: Mapped[MessageSourceEnum] = mapped_column(
        Enum(
            MessageSourceEnum,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            name="message_source_enum",
            schema="interview",
            native_enum=True,
        ),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
