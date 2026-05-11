from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Identity,
    Index,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        primary_key=True,
        comment="数据库内部主键，bigint 自增",
    )
    resume_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),
        comment="对外暴露的简历业务ID，UUID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        comment="所属用户ID，关联 users.id",
    )
    file_name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="上传时的原始文件名",
    )
    parse_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'pending'"),
        comment="解析状态：pending=待解析，success=成功，failed=失败",
    )
    # LLM 解析出的基本信息，允许用户二次编辑
    name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="姓名",
    )
    email: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        comment="邮箱",
    )
    phone: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="手机号",
    )
    location: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="所在城市",
    )
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="个人简介 / 求职意向",
    )
    skills: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        comment="技能标签列表，string[]",
    )
    total_years_exp: Mapped[float | None] = mapped_column(
        Numeric(4, 1),
        nullable=True,
        comment="总工作年限，用户可修改",
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
        comment="记录更新时间，用户编辑后更新",
    )

    __table_args__ = (
        Index("idx_resumes_user_id", "user_id"),
        Index("idx_resumes_user_id_created_at", "user_id", text("created_at DESC")),
        {
            "schema": "interview",
            "comment": "简历主表，存储 LLM 解析后的结构化简历，支持用户二次编辑",
        },
    )

