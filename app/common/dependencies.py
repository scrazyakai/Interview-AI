from typing import Optional
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exception import BizException, ErrorCode
from app.services.auth_service import AuthService

security = HTTPBearer(auto_error=False)
auth_service = AuthService()

ROLE_ADMIN = 3


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UUID:
    if not credentials:
        raise BizException(
            code=ErrorCode.INVALID_TOKEN,
            message="登录已失效，请重新登录",
            description="Authorization header is missing.",
        )

    token = credentials.credentials
    user_id_str = auth_service.get_user_id_from_token(token)

    if not user_id_str:
        raise BizException(
            code=ErrorCode.INVALID_TOKEN,
            message="登录已失效，请重新登录",
            description="Token parsing failed or token payload did not contain a user id.",
        )

    try:
        return UUID(user_id_str)
    except ValueError as exc:
        raise BizException(
            code=ErrorCode.INVALID_USER_ID,
            message="登录信息无效，请重新登录",
            description="Token payload contained an invalid UUID string for the user id.",
        ) from exc


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[UUID]:
    if not credentials:
        return None

    token = credentials.credentials
    user_id_str = auth_service.get_user_id_from_token(token)

    if not user_id_str:
        return None

    try:
        return UUID(user_id_str)
    except ValueError:
        return None


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UUID:
    if not credentials:
        raise BizException(
            code=ErrorCode.INVALID_TOKEN,
            message="登录已失效，请重新登录",
        )
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    if not payload:
        raise BizException(code=ErrorCode.INVALID_TOKEN, message="登录已失效，请重新登录")
    if payload.get("role") != ROLE_ADMIN:
        raise BizException(code=ErrorCode.ADMIN_REQUIRED, message="无权限，需要管理员身份")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise BizException(code=ErrorCode.INVALID_TOKEN, message="登录信息无效")
    try:
        return UUID(user_id_str)
    except ValueError as exc:
        raise BizException(code=ErrorCode.INVALID_USER_ID, message="登录信息无效") from exc


def parse_user_id_from_token(token: str) -> UUID:
    user_id_str = auth_service.get_user_id_from_token(token)

    if not user_id_str:
        raise BizException(
            code=ErrorCode.INVALID_TOKEN,
            message="登录已失效，请重新登录",
            description="Token parsing failed or token payload did not contain a user id.",
        )

    try:
        return UUID(user_id_str)
    except ValueError as exc:
        raise BizException(
            code=ErrorCode.INVALID_USER_ID,
            message="登录信息无效，请重新登录",
            description="Token payload contained an invalid UUID string for the user id.",
        ) from exc
