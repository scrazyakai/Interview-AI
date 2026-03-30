from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Identity,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        primary_key=True,
        comment="数据库内部主键，bigint 自增",
    )
    session_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
        comment="对外暴露的面试会话业务ID，UUID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        comment="所属用户的内部ID，关联 users.id",
    )
    job_title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="本次面试的岗位名称，冗余保存避免模板变更影响历史记录",
    )
    job_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="本次面试使用的岗位JD或岗位描述快照",
    )
    resume_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="候选人简历文本，MVP阶段直接存全文",
    )
    mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="面试模式：technical=技术面，behavioral=行为面，mixed=综合面",
    )
    experience_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="面试难度：junior=初级，mid=中级，senior=高级",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'init'"),
        comment="会话状态：init=未开始，asking=提问中，evaluating=评估中，finished=已结束，cancelled=已取消",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="面试开始时间",
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="面试结束时间",
    )
    finish_reason: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="结束原因，如normal_completed、user_cancelled、system_stopped",
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

    __table_args__ = (
        CheckConstraint(
            "mode IN ('technical', 'behavioral', 'mixed')",
            name="chk_interview_sessions_mode",
        ),
        CheckConstraint(
            "difficulty IN ('intern','junior', 'mid', 'senior')",
            name="chk_interview_sessions_difficulty",
        ),
        CheckConstraint(
            "status IN ('interviewing', 'evaluating', 'finished', 'cancelled')",
            name="chk_interview_sessions_status",
        ),
        Index("idx_interview_sessions_user_id", "user_id"),
        Index("idx_interview_sessions_status", "status"),
        Index("idx_interview_sessions_created_at", text("created_at DESC")),
        Index(
            "idx_interview_sessions_user_status_created",
            "user_id",
            "status",
            text("created_at DESC"),
        ),
        {
            "schema": "interview",
            "comment": "面试会话表，一次完整模拟面试的主记录",
        },
    )