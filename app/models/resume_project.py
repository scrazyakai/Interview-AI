from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Identity, Index, Integer, String, Text, text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResumeProject(Base):
    __tablename__ = "resume_projects"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False),
        primary_key=True,
        comment="数据库内部主键",
    )
    resume_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="关联 resumes.id",
    )
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="项目名称",
    )
    role: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="担任角色",
    )
    start_date: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
        comment="开始时间，格式 YYYY-MM",
    )
    end_date: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
        comment="结束时间，格式 YYYY-MM，NULL 表示至今",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="项目描述",
    )
    tech_stack: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        comment="技术栈，string[]",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="排序顺序，数字越小越靠前",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    __table_args__ = (
        Index("idx_project_resume_id", "resume_id"),
        {
            "schema": "interview",
            "comment": "项目经历表",
        },
    )
