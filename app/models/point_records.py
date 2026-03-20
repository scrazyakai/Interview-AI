from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass

class PointRecordModel(Base):
    __tablename__ = "point_records"
    __table_args__ = {"schema": "interview"}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    item: Mapped[str] = mapped_column(String(100), nullable=False, comment="事项")
    change_point: Mapped[int] = mapped_column(Integer, nullable=False, comment="变动积分，正数增加，负数减少")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="详细说明")
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True, comment="金额")
    order_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True, comment="订单号")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="时间"
    )