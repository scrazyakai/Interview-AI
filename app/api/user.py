from uuid import UUID

from fastapi import APIRouter, Depends

from app.common.dependencies import get_current_user_id, auth_service
from app.config.db_config import get_session
from app.schemas import UserResponse, PointRecordListResponse
from app.services import point_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/point-record/list",response_model=PointRecordListResponse)
async def get_point_record(
    session: AsyncSession = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id),
    offset: int = 1,
    limit: int = 10
):
    point_record_response =  await point_service.get_point_records(session, current_user_id, offset, limit)
    return point_record_response
@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user_id: UUID = Depends(get_current_user_id)
):
    user_response = await auth_service.get_user(user_id=current_user_id)
    return user_response