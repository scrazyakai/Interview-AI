from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class JobProfile(Base):
    __tablename__ = "job_profiles"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        primary_key=True,
        comment="数据库内部主键，bigint 自增",
    )
    profile_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
        comment="对外暴露的岗位模板业务ID，UUID",
    )
    job_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="岗位名称，如 Python后端开发工程师",
    )
    category: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="岗位分类，如后端、前端、产品、测试",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="岗位说明或JD正文",
    )
    core_skills: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
        comment="岗位核心技能列表，JSON数组",
    )
    question_strategy: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        comment="面试出题策略，JSON对象",
    )
    difficulty_levels: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
        comment="支持的难度级别列表，JSON数组",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("TRUE"),
        comment="是否启用该岗位模板",
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

    interview_sessions: Mapped[list["InterviewSession"]] = relationship(
        back_populates="job_profile"
    )

    __table_args__ = (
        Index("idx_job_profiles_job_name", "job_name"),
        Index("idx_job_profiles_category", "category"),
        Index("idx_job_profiles_is_active", "is_active"),
        Index(
            "idx_job_profiles_core_skills_gin",
            "core_skills",
            postgresql_using="gin",
        ),
        {
            "schema": "interview",
            "comment": "岗位模板表，存储岗位画像、技能要求和出题策略",
        },
    )