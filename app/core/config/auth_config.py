import os

# JWT 密钥必须从环境变量获取，不提供默认值以确保安全性
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY not configured. Please set JWT_SECRET_KEY environment variable. "
        "Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
# Default to 60 minutes (was 10080 = 7 days, too long for security)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
# Refresh token expiration (7 days)
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))