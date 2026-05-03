import os

from app.core.config.config import settings
from app.core.exception import BizException

# JWT 密钥必须从环境变量获取，不提供默认值以确保安全性
JWT_SECRET_KEY: str = settings.JWT_SECRET_KEY
if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY not configured. Please set JWT_SECRET_KEY environment variable. "
        "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

JWT_ALGORITHM: str = settings.JWT_ALGORITHM
# Default to 60 minutes (was 10080 = 7 days, too long for security)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
# Refresh token expiration (7 days)
REFRESH_TOKEN_EXPIRE_DAYS: int = int(settings.REFRESH_TOKEN_EXPIRE_DAYS)