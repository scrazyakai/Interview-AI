from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import rag_document as doc_crud
from app.crud import user as user_crud
from app.core.exception import BizException, ErrorCode
from app.models.user import UserModel
from app.schemas.admin import AdminStatsResponse


async def get_stats(session: AsyncSession) -> AdminStatsResponse:
    total_users = await user_crud.count_users(session)

    # rag schema 表可能还未初始化，单独捕获避免影响用户数显示
    try:
        total_documents = await doc_crud.count_documents(session)
        total_chunks = await doc_crud.count_chunks(session)
        indexed_documents = await doc_crud.count_indexed_documents(session)
    except Exception:
        total_documents = 0
        total_chunks = 0
        indexed_documents = 0

    return AdminStatsResponse(
        total_users=total_users,
        total_documents=total_documents,
        total_chunks=total_chunks,
        indexed_documents=indexed_documents,
    )


async def list_users(session: AsyncSession, page: int, page_size: int):
    offset = (page - 1) * page_size
    return await user_crud.list_users(session, offset=offset, limit=page_size)


async def update_user_role(session: AsyncSession, user_id: UUID, role_type: int) -> UserModel:
    user = await user_crud.update_user_role(session, user_id, role_type)
    if user is None:
        raise BizException(code=ErrorCode.USER_NOT_FOUND, message="用户不存在")
    return user
