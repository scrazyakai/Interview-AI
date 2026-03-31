
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.sql.functions import func
from starlette import status

from app.config.db_config import AsyncSessionLocal
from app.models import InterviewSession
from app.models.session_history import SessionHistory
from app.schemas.interview_session import SessionHistoryResponse


async def get_session_history_pages(session_id: UUID,user_id: UUID, offset: int = 0, limit: int = 10)-> tuple[list[SessionHistoryResponse], int]:
    async with AsyncSessionLocal() as session:
        # 判断会话是否存在
        stmt = select(InterviewSession).where(
            InterviewSession.session_uuid == session_id
        )
        result = await session.execute(stmt)
        interview_session = result.scalars().one_or_none()
        """判断会话是否存在"""
        if interview_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该会话不存在"
            )
        """判断是否有查看权限"""
        if interview_session.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_UNAUTHORIZED,
                                detail="无权限访问该会话"
                                )

            # 查询总数
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
                created_at=record.created_at
            )
            for record in records
        ]

        return items, total

