import unittest
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

from dotenv import load_dotenv

load_dotenv()  # 加载真实 .env，使用千问 API Key

PDF_PATH = r"C:\Users\AKai\Downloads\简历.pdf"


def _make_token() -> str:
    """用真实 JWT 配置签一个测试用 token"""
    from jose import jwt
    from app.config.auth_config import JWT_ALGORITHM, JWT_SECRET_KEY

    payload = {
        "sub": str(uuid.uuid4()),
        "username": "test_user",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


class ResumeParseTest(unittest.TestCase):

    def setUp(self):
        import importlib
        self.app_module = importlib.import_module("app.main")

    @patch("app.crud.resume.save_resume", new_callable=AsyncMock)
    def test_parse_resume_returns_structured_result(self, mock_save):
        """上传真实简历 PDF，验证 LLM 能返回结构化结果"""
        from fastapi.testclient import TestClient
        from app.schemas.resume import ResumeParseResult

        token = _make_token()

        with open(PDF_PATH, "rb") as f:
            pdf_bytes = f.read()

        client = TestClient(self.app_module.app)
        response = client.post(
            "/api/resume/parse",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("简历.pdf", pdf_bytes, "application/pdf")},
        )

        print("\n========== 响应状态码 ==========")
        print(response.status_code)
        print("========== 响应体 ==========")
        import json
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["code"], 0)

        # 验证返回结构能被 ResumeParseResult 反序列化
        data = response.json().get("data")
        if data:
            result = ResumeParseResult(**data)
            print("\n========== 解析结果 ==========")
            print(result.model_dump_json(indent=2, ensure_ascii=False))

        # 持久化未完成，确认 save_resume 被调用了即可
        mock_save.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
