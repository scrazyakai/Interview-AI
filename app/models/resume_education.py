from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import (
    BigInteger,
    DateTime,
    Identity,
    Index,
    Integer,
    String,
    text,
)

from app.db.base import Base
class ResumeEducation(Base):
    __tablename__ = "resume_educations"

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
    school: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="学校名称",
    )
    degree: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="学历：bachelor=本科，master=硕士，doctor=博士，other=其他",
    )
    major: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="专业",
    )
    graduation_year: Mapped[str | None] = mapped_column(
        String(8),
        nullable=True,
        comment="毕业年份，格式 YYYY",
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
        comment="记录创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        comment="记录更新时间，用户编辑后更新",
    )

    __table_args__ = (
        Index("idx_education_resume_id", "resume_id"),
        {
            "schema": "interview",
            "comment": "教育经历表，每条经历独立一行，支持用户单独增删改",
        },
    )
