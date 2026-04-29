from typing import Any

from app.core.exception.error_code import ErrorCode


def infer_http_status(code: int) -> int:
    if code == ErrorCode.SUCCESS:
        return 200
    if 40100 <= code <= 40199:
        return 401
    if 40300 <= code <= 40399:
        return 403
    if 40400 <= code <= 40499:
        return 404
    if 42200 <= code <= 42299:
        return 422
    if 50200 <= code <= 50299:
        return 502
    if 50000 <= code <= 50999:
        return 500
    if 40000 <= code <= 40999:
        return 400
    return 500


class AppException(Exception):
    def __init__(
        self,
        *,
        message: str,
        code: int,
        description: str | None = None,
        data: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.description = description
        self.data = data
        self.http_status = infer_http_status(code)


class BizException(AppException):
    def __init__(
        self,
        *,
        message: str,
        code: int = ErrorCode.BAD_REQUEST,
        description: str | None = None,
        data: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            description=description,
            data=data,
        )
