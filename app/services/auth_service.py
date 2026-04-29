import logging
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config.auth_config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.db.session import AsyncSessionLocal
from app.models.point_record import PointRecordModel
from app.models.user import UserModel

logger = logging.getLogger(__name__)

REGISTER_POINT_REWARD = 200
REGISTER_ITEM = "注册"


class AuthService:
    """认证服务类"""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        self.expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.max_failed_attempts = 5
        self.lockout_minutes = 15

    def create_access_token(self, user: UserModel) -> str:
        """创建访问令牌"""
        expires_delta = timedelta(minutes=self.expire_minutes)
        expire = datetime.now(UTC) + expires_delta

        to_encode = {
            "sub": str(user.user_id),
            "username": user.username,
            "exp": expire,
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token decode failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error decoding token: {e}")
            return None

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        从 token 中提取 user_id

        Args:
            token: JWT token 字符串

        Returns:
            user_id 字符串，如果解析失败则返回 None
        """
        payload = self.decode_token(token)
        if payload:
            return payload.get("sub")
        return None

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    async def register_user(self, username: str, password: str) -> UserModel:
        password_hash = self.hash_password(password)
        user = UserModel(username=username, password_hash=password_hash)

        async with AsyncSessionLocal() as session:
            try:
                session.add(user)
                await session.flush()

                point_record = PointRecordModel(
                    user_id=user.user_id,
                    change_point=REGISTER_POINT_REWARD,
                    item=REGISTER_ITEM
                )
                session.add(point_record)

                user.total_points = (user.total_points or 0) + point_record.change_point

                await session.commit()
                await session.refresh(user)
                return user

            except IntegrityError as exc:
                await session.rollback()
                logger.exception("Integrity error on user register: %s", exc)
                raise ValueError("Username already exists")

            except Exception:
                await session.rollback()
                logger.exception("Register failed")
                raise

    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """根据用户名获取用户"""
        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(UserModel.username == username)
            result = await session.execute(stmt)
            user = result.scalars().one_or_none()
            if user:
                # 确保所有属性都已加载，避免session关闭后出现延迟加载错误
                await session.refresh(user)
            return user

    async def authenticate(self, username: str, password: str) -> Optional[UserModel]:
        user = await self.get_user_by_username(username)
        if not user:
            return None

        if self.verify_password(password, user.password_hash):
            return user

        return None

    async def verify_user(self, username: str, password: str) -> Optional[UserModel]:
        """验证用户凭据"""
        return await self.authenticate(username, password)

    async def get_user(self, user_id: str) -> Optional[UserModel]:
        """根据user_id获取用户"""
        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().one_or_none()
            return user