from datetime import datetime

from sqlalchemy import SmallInteger, func, VARCHAR
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(Base):
    __tablename__ = "user_role"
    __table_args__ = {"schema": "interview"}

    # 1=普通用户  2=VIP  3=管理员
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    description: Mapped[str] = mapped_column(
        VARCHAR(255),
    )
