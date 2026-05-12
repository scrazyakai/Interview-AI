from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import auth_service, get_current_user_id
from app.core.exception import ApiResponse
from app.db.session import get_session
from app.models.interview_session import InterviewSession
from app.models.user import UserModel
from app.schemas import PointRecordListResponse, UserResponse
from app.schemas.user import UserStatsResponse
from app.crud.point_record import get_records_total
from app.services import point_service

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/point-record/list", response_model=ApiResponse[PointRecordListResponse])
async def get_point_record(
    session: AsyncSession = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[PointRecordListResponse]:
    offset = (page - 1) * page_size
    point_record_response = await point_service.get_point_records(session, current_user_id, offset, page_size)
    return ApiResponse.success(data=point_record_response)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_me(current_user_id: UUID = Depends(get_current_user_id)) -> ApiResponse[UserResponse]:
    user_response = await auth_service.get_user(user_id=current_user_id)
    return ApiResponse.success(data=user_response)


@router.get("/stats", response_model=ApiResponse[UserStatsResponse])
async def get_user_stats(
    session: AsyncSession = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id),
) -> ApiResponse[UserStatsResponse]:
    total_interviews_result = await session.execute(
        select(func.count()).select_from(InterviewSession).where(InterviewSession.user_id == current_user_id)
    )
    total_interviews = total_interviews_result.scalar() or 0

    total_points_result = await session.execute(
        select(UserModel.total_points).where(UserModel.user_id == current_user_id)
    )
    total_points = total_points_result.scalar() or 0

    total_point_records = await get_records_total(session, current_user_id)

    return ApiResponse.success(data=UserStatsResponse(
        total_interviews=total_interviews,
        total_points=total_points,
        total_point_records=total_point_records,
    ))
