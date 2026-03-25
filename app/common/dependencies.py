from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import AuthService

security = HTTPBearer()
auth_service = AuthService()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    从请求头中获取当前登录用户的 user_id

    Args:
        credentials: HTTP Bearer 认证凭据

    Returns:
        当前用户的 user_id (UUID)

    Raises:
        HTTPException: 当 token 无效或解析失败时
    """
    token = credentials.credentials
    user_id_str = auth_service.get_user_id_from_token(token)

    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
        return user_id
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UUID]:
    """
    可选的认证依赖，返回当前用户的 user_id 或 None

    Args:
        credentials: 可选的 HTTP Bearer 认证凭据

    Returns:
        当前用户的 user_id (UUID) 或 None
    """
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
def parse_user_id_from_token(token: str) -> UUID:
    user_id_str = auth_service.get_user_id_from_token(token)

    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )