from uuid import UUID

from sqlalchemy import func, select

from app.models.user import UserModel


async def count_users(session) -> int:
    result = await session.execute(select(func.count()).select_from(UserModel))
    return result.scalar_one()


async def get_user_by_user_id(session, user_id: UUID) -> UserModel | None:
    result = await session.execute(
        select(UserModel).where(UserModel.user_id == user_id)
    )
    return result.scalars().first()


async def list_users(session, offset: int = 0, limit: int = 20) -> tuple[list[UserModel], int]:
    total = await count_users(session)
    result = await session.execute(
        select(UserModel).order_by(UserModel.created_at.desc()).offset(offset).limit(limit)
    )
    return result.scalars().all(), total


async def update_user_role(session, user_id: UUID, role_type: int) -> UserModel | None:
    user = await get_user_by_user_id(session, user_id)
    if user is None:
        return None
    user.role_type = role_type
    await session.flush()
    return user
