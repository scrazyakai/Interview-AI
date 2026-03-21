from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class InterviewMessage(Base):
    __tablename__ = "interview_messages"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        primary_key=True,
        comment="数据库内部主键，bigint 自增",
    )
    message_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
        comment="对外暴露的消息业务ID，UUID",
    )
    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("interview.interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属面试会话内部ID，关联 interview_sessions.id",
    )
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="消息角色：system=系统，interviewer=面试官，candidate=候选人，evaluator=评估器",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="消息正文内容",
    )
    question_type: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="问题类型，如 intro、project、technical、behavioral、scenario",
    )
    round_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="当前消息属于第几轮面试",
    )
    sequence_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="消息在整场会话中的顺序号，必须严格递增",
    )
    parent_message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("interview.interview_messages.id"),
        nullable=True,
        comment="父消息ID，通常用于标记回答对应的问题消息",
    )
    token_usage_prompt: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="本次模型调用的输入token数",
    )
    token_usage_completion: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="本次模型调用的输出token数",
    )
    token_usage_total: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="本次模型调用的总token数",
    )
    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="本次消息生成或处理耗时，单位毫秒",
    )
    extra: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        comment="扩展信息，如原始模型输出、结构化标签、调试信息",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        comment="记录创建时间",
    )

    session: Mapped["InterviewSession"] = relationship(
        back_populates="messages"
    )
    parent_message: Mapped["InterviewMessage | None"] = relationship(
        remote_side="InterviewMessage.id",
        back_populates="children",
    )
    children: Mapped[list["InterviewMessage"]] = relationship(
        back_populates="parent_message"
    )
    evaluation_result: Mapped["EvaluationResult | None"] = relationship(
        back_populates="message",
        uselist=False,
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('system', 'interviewer', 'candidate', 'evaluator')",
            name="chk_interview_messages_role",
        ),
        CheckConstraint(
            "round_no > 0",
            name="chk_interview_messages_round_no",
        ),
        CheckConstraint(
            "sequence_no > 0",
            name="chk_interview_messages_sequence_no",
        ),
        CheckConstraint(
            "token_usage_prompt IS NULL OR token_usage_prompt >= 0",
            name="chk_interview_messages_token_usage_prompt",
        ),
        CheckConstraint(
            "token_usage_completion IS NULL OR token_usage_completion >= 0",
            name="chk_interview_messages_token_usage_completion",
        ),
        CheckConstraint(
            "token_usage_total IS NULL OR token_usage_total >= 0",
            name="chk_interview_messages_token_usage_total",
        ),
        CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name="chk_interview_messages_latency_ms",
        ),
        Index("idx_interview_messages_session_id", "session_id"),
        Index(
            "idx_interview_messages_session_sequence",
            "session_id",
            "sequence_no",
        ),
        Index(
            "idx_interview_messages_session_round",
            "session_id",
            "round_no",
        ),
        Index("idx_interview_messages_role", "role"),
        Index("idx_interview_messages_created_at", text("created_at DESC")),
        Index(
            "idx_interview_messages_extra_gin",
            "extra",
            postgresql_using="gin",
        ),
        {
            "schema": "interview",
            "comment": "面试消息表，存储整场面试中的所有问答消息",
        },
    )