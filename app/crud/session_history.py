from uuid import UUID

from sqlalchemy import select
from sqlalchemy.sql.functions import func

from app.core.exception import BizException, ErrorCode
from app.db.session import AsyncSessionLocal
from app.models import InterviewSession
from app.models.session_history import SessionHistory
from app.schemas.interview_session import SessionHistoryResponse


async def get_session_history_pages(
    session_id: UUID,
    user_id: UUID,
    offset: int = 0,
    limit: int = 10,
) -> tuple[list[SessionHistoryResponse], int]:
    async with AsyncSessionLocal() as session:
        stmt = select(InterviewSession).where(
            InterviewSession.session_uuid == session_id
        )
        result = await session.execute(stmt)
        interview_session = result.scalars().one_or_none()
        if interview_session is None:
            raise BizException(
                code=ErrorCode.INTERVIEW_SESSION_NOT_FOUND,
                message="该会话不存在",
                description="No interview session matched the requested session UUID.",
            )
        if interview_session.user_id != user_id:
            raise BizException(
                code=ErrorCode.SESSION_ACCESS_DENIED,
                message="无权限访问该会话",
                description="The requested session belongs to a different user.",
            )

        count_stmt = select(func.count()).where(
            SessionHistory.session_id == session_id
        )
        count_result = await session.execute(count_stmt)
        total = count_result.scalar_one()

        history_stmt = (
            select(SessionHistory)
            .where(SessionHistory.session_id == session_id)
            .order_by(SessionHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        history_result = await session.execute(history_stmt)
        records = history_result.scalars().all()

        items = [
            SessionHistoryResponse(
                message=record.message,
                message_source=record.message_source,
                created_at=record.created_at,
            )
            for record in records
        ]

        return items, total
