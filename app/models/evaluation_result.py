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
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        primary_key=True,
        comment="数据库内部主键，bigint 自增",
    )
    evaluation_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
        comment="对外暴露的评估结果业务ID，UUID",
    )
    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("interview.interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属面试会话内部ID，关联 interview_sessions.id",
    )
    message_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("interview.interview_messages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="对应的候选人回答消息内部ID，关联 interview_messages.id",
    )
    round_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="该评估属于第几轮面试",
    )
    score_overall: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="总分，范围 1 到 5",
    )
    score_communication: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="表达清晰度评分，范围 1 到 5",
    )
    score_technical: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="技术准确性或技术能力评分，范围 1 到 5",
    )
    score_problem_solving: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="问题解决能力评分，范围 1 到 5",
    )
    score_depth: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="回答深度评分，范围 1 到 5",
    )
    strengths: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="本轮回答的主要优点",
    )
    weaknesses: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="本轮回答的主要不足",
    )
    improvement_suggestion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="针对本轮回答的改进建议",
    )
    rubric_detail: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        comment="更细粒度的评分细则和标签，JSON对象",
    )
    model_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="执行评估的模型名称或模型ID",
    )
    prompt_version: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="评估Prompt版本号",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        comment="记录创建时间",
    )

    session: Mapped["InterviewSession"] = relationship(
        back_populates="evaluation_results"
    )
    message: Mapped["InterviewMessage"] = relationship(
        back_populates="evaluation_result"
    )

    __table_args__ = (
        UniqueConstraint("message_id", name="uq_evaluation_results_message_id"),
        CheckConstraint(
            "round_no > 0",
            name="chk_evaluation_results_round_no",
        ),
        CheckConstraint(
            "score_overall BETWEEN 1 AND 5",
            name="chk_score_overall",
        ),
        CheckConstraint(
            "score_communication BETWEEN 1 AND 5",
            name="chk_score_communication",
        ),
        CheckConstraint(
            "score_technical BETWEEN 1 AND 5",
            name="chk_score_technical",
        ),
        CheckConstraint(
            "score_problem_solving BETWEEN 1 AND 5",
            name="chk_score_problem_solving",
        ),
        CheckConstraint(
            "score_depth BETWEEN 1 AND 5",
            name="chk_score_depth",
        ),
        Index("idx_evaluation_results_session_id", "session_id"),
        Index("idx_evaluation_results_round_no", "round_no"),
        Index("idx_evaluation_results_created_at", text("created_at DESC")),
        Index(
            "idx_evaluation_results_rubric_detail_gin",
            "rubric_detail",
            postgresql_using="gin",
        ),
        {
            "schema": "interview",
            "comment": "单轮评估结果表，记录每次候选人回答后的结构化评分",
        },
    )