import os

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "aZkQmLpXvRjHsTdWcYbNfGqEoUiKrPz")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
# Default to 60 minutes (was 10080 = 7 days, too long for security)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "4320"))
# Refresh token expiration (7 days)
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))