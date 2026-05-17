from datetime import UTC, datetime, timedelta
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config.auth_config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
from app.core.exception import BizException, ErrorCode
from app.core.log import get_logger
from app.db.session import AsyncSessionLocal
from app.models.point_record import PointRecordModel
from app.models.user import UserModel

log = get_logger(__name__)

REGISTER_POINT_REWARD = 200
REGISTER_ITEM = "注册"


class AuthService:
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        self.expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
        self.max_failed_attempts = 5
        self.lockout_minutes = 15

    def create_access_token(self, user: UserModel) -> str:
        expires_delta = timedelta(minutes=self.expire_minutes)
        expire = datetime.now(UTC) + expires_delta

        to_encode = {
            "sub": str(user.user_id),
            "username": user.username,
            "role": user.role_type,
            "exp": expire,
        }

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[dict[str, Any]]:
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
        except JWTError as exc:
            log.warning("[biz] Token decode failed: %s", exc)
            return None
        except Exception as exc:
            log.exception("[exception] Unexpected error decoding token: %s", exc)
            return None

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        payload = self.decode_token(token)
        if payload:
            return payload.get("sub")
        return None

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    async def register_user(self, username: str, password: str) -> UserModel:
        password_hash = self.hash_password(password)
        user = UserModel(username=username, password_hash=password_hash, role_type=1)

        async with AsyncSessionLocal() as session:
            try:
                session.add(user)
                await session.flush()

                point_record = PointRecordModel(
                    user_id=user.user_id,
                    change_point=REGISTER_POINT_REWARD,
                    item=REGISTER_ITEM,
                )
                session.add(point_record)

                user.total_points = (user.total_points or 0) + point_record.change_point

                await session.commit()
                await session.refresh(user)
                log.info(
                    "[biz] User registered successfully: username=%s user_id=%s",
                    user.username,
                    user.user_id,
                )
                return user
            except IntegrityError as exc:
                await session.rollback()
                log.exception("[exception] Integrity error on user register: %s", exc)
                raise BizException(
                    code=ErrorCode.USERNAME_ALREADY_EXISTS,
                    message="用户名已存在",
                    description="The username violated a unique constraint during registration.",
                ) from exc
            except Exception:
                await session.rollback()
                log.exception("[exception] Register failed")
                raise

    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(UserModel.username == username)
            result = await session.execute(stmt)
            user = result.scalars().one_or_none()
            if user:
                await session.refresh(user)
            return user

    async def authenticate(self, username: str, password: str) -> Optional[UserModel]:
        user = await self.get_user_by_username(username)
        if not user:
            log.info("[biz] User login failed because username was not found: username=%s", username)
            return None

        if self.verify_password(password, user.password_hash):
            log.info("[biz] User login succeeded: username=%s user_id=%s", user.username, user.user_id)
            return user

        log.info("[biz] User login failed because password did not match: username=%s", username)
        return None

    async def verify_user(self, username: str, password: str) -> Optional[UserModel]:
        return await self.authenticate(username, password)

    async def get_user(self, user_id: str) -> Optional[UserModel]:
        async with AsyncSessionLocal() as session:
            stmt = select(UserModel).where(UserModel.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalars().one_or_none()
