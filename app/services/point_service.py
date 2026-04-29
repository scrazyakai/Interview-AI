from app.common.dependencies import auth_service
from app.core.exception import BizException, ErrorCode
from app.core.log import get_logger
from app.crud import point_record
from app.schemas import PointRecordListResponse

log = get_logger(__name__)


class PointService:
    pass


async def get_point_records(session, current_user_id, offset, limit) -> PointRecordListResponse:
    log.info(
        "[biz] Loading point records: user_id=%s offset=%s limit=%s",
        current_user_id,
        offset,
        limit,
    )
    existing = await auth_service.get_user(user_id=current_user_id)
    if existing is None:
        raise BizException(
            code=ErrorCode.USER_NOT_FOUND,
            message="用户不存在",
            description="No user record matched the authenticated user id while loading point records.",
        )

    items = await point_record.get_point_records(
        session=session,
        user_id=current_user_id,
        offset=offset,
        limit=limit,
    )
    total = await point_record.get_records_total(
        session=session,
        user_id=current_user_id,
    )
    return PointRecordListResponse(items=items, total=total)
