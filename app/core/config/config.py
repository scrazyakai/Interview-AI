from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """数据库配置"""
    DATABASE_URL: str
    PGVECTOR_CONNECTION_STRING: Optional[str] = None
    PGVECTOR_COLLECTION_NAME: str = "interview_question_bank"

    """JWT 配置"""
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    """火山引擎 / 豆包文本模型配置"""
    VOLC_API_KEY: str
    VOLC_BASE_URL: str
    VOLC_MODEL: str

    """千问实时语音对话配置"""
    QWEN_REALTIME_URL: str = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    QWEN_REALTIME_MODEL: str = "qwen3.5-omni-flash-realtime"
    QWEN_REALTIME_SYSTEM_ROLE: Optional[str] = "app/prompt/interviewer-system-prompt.md"
    QWEN_REALTIME_VOICE: str = "Ethan"
    """Embedding 模型配置"""
    EMBEDDING_PROVIDER: Optional[str] = None
    EMBEDDING_MODEL_NAME: str
    EMBEDDING_BASE_URL: Optional[str] = None
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_DIMENSION: Optional[int] = None
    """千问模型：解析简历"""
    QWEN_API_KEY:str
    QWEN_MODEL:str
    QWEN_API_URL:str
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
