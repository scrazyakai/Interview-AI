from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        primary_key=True,
        comment="数据库内部主键，bigint 自增",
    )
    report_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
        comment="对外暴露的报告业务ID，UUID",
    )
    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("interview.interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="所属面试会话内部ID，关联 interview_sessions.id，且一场会话仅一份报告",
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="整场面试的总结性文字",
    )
    strengths: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
        comment="整场面试的优势点列表，JSON数组",
    )
    weaknesses: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
        comment="整场面试的短板列表，JSON数组",
    )
    suggestions: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
        comment="整场面试的改进建议列表，JSON数组",
    )
    average_score: Mapped[Decimal] = mapped_column(
        Numeric(4, 2),
        nullable=False,
        server_default=text("0.00"),
        comment="整场面试的平均分，保留两位小数",
    )
    total_rounds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="整场面试总轮次数",
    )
    report_version: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="报告生成模板或Prompt版本",
    )
    extra: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        comment="扩展信息，如原始汇总数据、可视化数据、调试信息",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        comment="记录创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        comment="记录更新时间",
    )

    session: Mapped["InterviewSession"] = relationship(
        back_populates="report"
    )

    __table_args__ = (
        CheckConstraint(
            "average_score >= 0 AND average_score <= 5.00",
            name="chk_interview_reports_average_score",
        ),
        CheckConstraint(
            "total_rounds >= 0",
            name="chk_interview_reports_total_rounds",
        ),
        Index("idx_interview_reports_created_at", text("created_at DESC")),
        Index(
            "idx_interview_reports_strengths_gin",
            "strengths",
            postgresql_using="gin",
        ),
        Index(
            "idx_interview_reports_weaknesses_gin",
            "weaknesses",
            postgresql_using="gin",
        ),
        Index(
            "idx_interview_reports_suggestions_gin",
            "suggestions",
            postgresql_using="gin",
        ),
        {
            "schema": "interview",
            "comment": "最终面试报告表，保存整场面试的总结报告",
        },
    )