from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.point_record import PointRecordModel
from app.schemas import PointRecordResponse


async def get_point_records(session: AsyncSession, user_id: UUID, offset: int = 1, limit: int = 10) -> List[PointRecordResponse]:
    stmt = (select(PointRecordModel)
            .where(PointRecordModel.user_id == user_id)
            .order_by(PointRecordModel.created_at.desc())
            .offset(offset)
            .limit(limit))

    results = await session.execute(stmt)
    records = results.scalars().all()
    return [
        PointRecordResponse(
            item=record.item,
            change_point=record.change_point,
            description=record.description,
            amount=record.amount,
            order_no=record.order_no,
            created_at=record.created_at,
        )
        for record in records
    ]
async def get_records_total(session: AsyncSession,user_id: UUID):
    stmt = select(PointRecordModel).where(PointRecordModel.user_id == user_id)
    results = await session.execute(stmt)
    return len(results.scalars().all())