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

    """豆包实时语音对话配置"""
    VOLC_REALTIME_APP_ID: str
    VOLC_REALTIME_ACCESS_KEY: str
    VOLC_REALTIME_URL: str
    VOLC_REALTIME_RESOURCE_ID: str
    VOLC_REALTIME_APP_KEY: str
    VOLC_REALTIME_SPEAKER: str
    VOLC_REALTIME_OUTPUT_FORMAT: str
    VOLC_REALTIME_OUTPUT_SAMPLE_RATE: int
    VOLC_REALTIME_END_SMOOTH_WINDOW_MS: int
    VOLC_REALTIME_RECV_TIMEOUT: int
    VOLC_REALTIME_BOT_NAME: str
    VOLC_REALTIME_SYSTEM_ROLE: str
    VOLC_REALTIME_SPEAKING_STYLE: str
    VOLC_REALTIME_INPUT_FORMAT:str
    VOLC_REALTIME_INPUT_SAMPLE_RATE:str
    """Embedding 模型配置"""
    EMBEDDING_PROVIDER: Optional[str] = None
    EMBEDDING_MODEL_NAME: str
    EMBEDDING_BASE_URL: Optional[str] = None
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_DIMENSION: Optional[int] = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
