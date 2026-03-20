import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config.auth_config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.config.db_config import get_session
from app.models.point_records import PointRecordModel
from app.models.user import UserModel

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        self.expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.max_failed_attempts = 5
        self.lockout_minutes = 15

    async def create_access_token(self, user: UserModel) -> str:
        """创建访问令牌"""
        expires_delta = timedelta(minutes=self.expire_minutes)
        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "exp": expire,
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    """用户注册"""
    async def register_user(self, username: str, password: str) -> UserModel:
        password_hash = self.hash_password(password)
        user = UserModel(username=username, password_hash=password_hash)
        point_record = PointRecordModel()
        async with get_session() as session:
            session.add(user)
            try:
                await session.flush()
                await session.commit()
                await session.refresh(user)
            except IntegrityError as exc:
                await session.rollback()
                logger.warning("Integrity error on user register: %s", exc)
                raise ValueError("Username already exists")
            logger.info("Created user %s", username)
            return user

    """加密密码"""
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    """验证密码"""
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    """用户认证"""
    async def authenticate(self, username: str, password: str) -> Optional[UserModel]:
        user = await self.get_user_by_username(username)
        if not user:
            return None

        if self.verify_password(password, user.password_hash):
            return user

        return None

    """获取用户"""
    async def verify_user(self, username: str, password: str) -> Optional[UserModel]:
        """验证用户凭据"""
        return await self.authenticate(username, password)

    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """根据用户名获取用户"""
        async with get_session() as session:
            smt = select(UserModel).where(UserModel.username == username)
            result = await session.execute(smt)
            user = result.scalars().one_or_none()
            # 在会话关闭前获取用户数据
            if user:
                return UserModel(id=user.id, username=user.username, password_hash=user.password_hash)
            return None
