from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    username: str
    user_id: UUID
    avatar_url: Optional[str] = None
    total_points: int


class PointRecordResponse(BaseModel):
    item: str
    change_point: int
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    order_no: Optional[str] = None
    created_at: datetime


class PointRecordListResponse(BaseModel):
    total: int
    items: List[PointRecordResponse]


class UserStatsResponse(BaseModel):
    total_interviews: int
    total_points: int
    total_point_records: int
