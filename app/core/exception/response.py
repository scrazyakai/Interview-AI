from typing import Generic, TypeVar

from pydantic import BaseModel

from app.core.exception.error_code import ErrorCode

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: T | None = None

    @classmethod
    def success(cls, data: T | None = None, message: str = "success") -> "ApiResponse[T]":
        return cls(code=ErrorCode.SUCCESS, message=message, data=data)

    @classmethod
    def failure(
        cls,
        code: int,
        message: str,
        data: T | None = None,
    ) -> "ApiResponse[T]":
        return cls(code=code, message=message, data=data)
