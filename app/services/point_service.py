from fastapi import HTTPException
from starlette import status

from app.common.dependencies import auth_service
from app.crud import point_record
from app.schemas import PointRecordListResponse


class PointService:
    pass


async def get_point_records(session, current_user_id, offset, limit)-> PointRecordListResponse:
    existing = await auth_service.get_user(user_id=current_user_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 计算起始位置，确保不为负数
    skip = max(0, offset - 1) * limit

    items = await point_record.get_point_records(
        session=session,
        user_id=current_user_id,
        offset=skip,
        limit=limit
    )
    total = await point_record.get_records_total(
        session=session,
        user_id=current_user_id
    )
    return PointRecordListResponse(items = items, total = total)