from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

ROLE_INTERVIEWER = "interviewer"
ROLE_CANDIDATE = "candidate"


class InterviewMessage(Base):
    __tablename__ = "interview_messages"
    __table_args__ = (
        Index("idx_interview_messages_session_id", "session_id"),
        Index("idx_interview_messages_session_round", "session_id", "round_no"),
        Index("idx_interview_messages_session_sequence", "session_id", "sequence_no"),
        {"schema": "interview"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    message_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        default=uuid.uuid4,
    )

    # FK to interview_sessions.id (internal bigint PK, not session_uuid)
    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("interview.interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str | None] = mapped_column(Text, nullable=True)

    round_no: Mapped[int] = mapped_column(Integer, nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)

    # candidate 消息指向其回答的 interviewer 消息 id
    parent_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    token_usage_prompt: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_usage_completion: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_usage_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    extra: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
