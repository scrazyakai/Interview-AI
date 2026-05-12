import importlib
import os
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


def ensure_test_env() -> None:
    prompt_path = os.path.join(tempfile.gettempdir(), "interview-ai-test-prompt.md")
    if not os.path.exists(prompt_path):
        with open(prompt_path, "w", encoding="utf-8") as file:
            file.write("You are a helpful interviewer.")

    env = {
        "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres",
        "JWT_SECRET_KEY": "test-secret-key",
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        "VOLC_API_KEY": "test",
        "VOLC_BASE_URL": "https://example.com",
        "VOLC_MODEL": "test-model",
        "VOLC_REALTIME_APP_ID": "test-app-id",
        "VOLC_REALTIME_ACCESS_KEY": "test-access-key",
        "VOLC_REALTIME_URL": "wss://example.com/realtime",
        "VOLC_REALTIME_RESOURCE_ID": "test-resource-id",
        "VOLC_REALTIME_APP_KEY": "test-app-key",
        "VOLC_REALTIME_SPEAKER": "test-speaker",
        "VOLC_REALTIME_OUTPUT_FORMAT": "pcm",
        "VOLC_REALTIME_OUTPUT_SAMPLE_RATE": "16000",
        "VOLC_REALTIME_END_SMOOTH_WINDOW_MS": "500",
        "VOLC_REALTIME_RECV_TIMEOUT": "30",
        "VOLC_REALTIME_BOT_NAME": "test-bot",
        "VOLC_REALTIME_SYSTEM_ROLE": prompt_path,
        "VOLC_REALTIME_SPEAKING_STYLE": "default",
        "VOLC_REALTIME_INPUT_FORMAT": "pcm",
        "VOLC_REALTIME_INPUT_SAMPLE_RATE": "16000",
        "EMBEDDING_MODEL_NAME": "test-embedding",
    }
    os.environ.update(env)


class PayloadModel(BaseModel):
    name: str


class ExceptionSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        ensure_test_env()

    def test_api_response_success_envelope(self) -> None:
        from app.core.exception import ApiResponse

        response = ApiResponse.success(data={"name": "alice"})

        self.assertEqual(response.code, 0)
        self.assertEqual(response.message, "success")
        self.assertEqual(response.data, {"name": "alice"})

    def test_biz_exception_handler_returns_envelope(self) -> None:
        from app.core.exception import BizException, ErrorCode, register_exception_handlers

        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/secure")
        async def secure() -> None:
            raise BizException(
                code=ErrorCode.INVALID_TOKEN,
                message="登录已失效，请重新登录",
                description="Token is expired in test.",
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/secure")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "code": ErrorCode.INVALID_TOKEN,
                "message": "登录已失效，请重新登录",
                "data": None,
            },
        )

    def test_global_handler_masks_unexpected_error(self) -> None:
        from app.core.exception import ErrorCode, register_exception_handlers

        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/boom")
        async def boom() -> None:
            raise RuntimeError("raw database error")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/boom")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], ErrorCode.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json()["message"], "服务器开小差了，请稍后再试")
        self.assertIsNone(response.json()["data"])

    def test_validation_error_returns_unified_envelope(self) -> None:
        from app.core.exception import ErrorCode, register_exception_handlers

        app = FastAPI()
        register_exception_handlers(app)

        @app.post("/payload")
        async def payload(body: PayloadModel) -> dict:
            return {"name": body.name}

        client = TestClient(app)
        response = client.post("/payload", json={})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["code"], ErrorCode.REQUEST_VALIDATION_ERROR)
        self.assertEqual(response.json()["message"], "请求参数不合法")
        self.assertIsNotNone(response.json()["data"])

    def test_chat_empty_message_returns_unified_bad_request(self) -> None:
        from app.core.exception import ErrorCode

        main_module = importlib.import_module("app.main")
        client = TestClient(main_module.app)
        response = client.post("/api/interview/chat", json={"message": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "code": ErrorCode.EMPTY_MESSAGE,
                "message": "message cannot be empty",
                "data": None,
            },
        )

    def test_upload_empty_file_returns_unified_bad_request(self) -> None:
        from app.core.exception import ErrorCode

        main_module = importlib.import_module("app.main")
        client = TestClient(main_module.app)
        response = client.post(
            "/api/interview/upload",
            files={"file": ("resume.pdf", b"", "application/pdf")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "code": ErrorCode.EMPTY_FILE,
                "message": "File is empty",
                "data": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
