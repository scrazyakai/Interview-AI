from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import (
    BigInteger,
    DateTime,
    Identity,
    Index,
    Integer,
    String,
    Text,
    text, JSON,
)

from app.db.base import Base


class ResumeWorkExperience(Base):
    __tablename__ = "resume_work_experiences"

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
    company: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="公司名称",
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="职位名称",
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
        comment="工作内容描述",
    )
    tech_stack: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        comment="该段经历涉及的技术栈，string[]",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="排序顺序，数字越小越靠前，支持用户拖拽排序",
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
        Index("idx_work_exp_resume_id", "resume_id"),
        {
            "schema": "interview",
            "comment": "工作经历表，每条经历独立一行，支持用户单独增删改",
        },
    )
