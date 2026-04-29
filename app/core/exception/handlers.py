import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from app.core.exception.error_code import ErrorCode
from app.core.exception.exceptions import AppException
from app.core.exception.response import ApiResponse

logger = logging.getLogger(__name__)


def _build_response(
    *,
    http_status: int,
    code: int,
    message: str,
    data: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=http_status,
        content=ApiResponse.failure(code=code, message=message, data=data).model_dump(),
        headers=headers,
    )


def _http_exception_code(status_code: int) -> int:
    if status_code == status.HTTP_400_BAD_REQUEST:
        return ErrorCode.BAD_REQUEST
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return ErrorCode.UNAUTHORIZED
    if status_code == status.HTTP_403_FORBIDDEN:
        return ErrorCode.FORBIDDEN
    if status_code == status.HTTP_404_NOT_FOUND:
        return ErrorCode.NOT_FOUND
    if status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        return ErrorCode.REQUEST_VALIDATION_ERROR
    if status_code == status.HTTP_502_BAD_GATEWAY:
        return ErrorCode.EXTERNAL_SERVICE_ERROR
    return ErrorCode.INTERNAL_SERVER_ERROR


def _http_exception_message(status_code: int, detail: Any) -> str:
    if status_code >= 500:
        return "服务器开小差了，请稍后再试"
    if isinstance(detail, str) and detail:
        return detail
    return "请求失败"


def _format_validation_errors(exc: RequestValidationError) -> list[dict[str, Any]]:
    return [
        {
            "loc": list(error.get("loc", ())),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        for error in exc.errors()
    ]


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        if exc.description:
            logger.warning(
                "Business exception raised: code=%s message=%s description=%s",
                exc.code,
                exc.message,
                exc.description,
            )
        return _build_response(
            http_status=exc.http_status,
            code=exc.code,
            message=exc.message,
            data=exc.data,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _build_response(
            http_status=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code=ErrorCode.REQUEST_VALIDATION_ERROR,
            message="请求参数不合法",
            data={"errors": _format_validation_errors(exc)},
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        return _build_response(
            http_status=exc.status_code,
            code=_http_exception_code(exc.status_code),
            message=_http_exception_message(exc.status_code, exc.detail),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application exception", exc_info=exc)
        return _build_response(
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="服务器开小差了，请稍后再试",
        )
