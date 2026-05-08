import logging
from typing import List

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from app.core.config.config import settings
from app.core.exception import BizException, ErrorCode

logger = logging.getLogger(__name__)


class IndexConstructionModule:
    """Build and reuse a PGVector-backed vector index."""

    def __init__(
        self,
        collection_name: str = "interview_question_bank",
        connection_string: str | None = None,
        pre_delete_collection: bool = False,
    ):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.collection_name = collection_name
        self.connection_string = self._resolve_connection_string(connection_string)
        self.pre_delete_collection = pre_delete_collection
        self.embeddings = None
        self.vectorstore = None
        self.setup_embeddings()

    def setup_embeddings(self) -> None:
        if not settings.EMBEDDING_API_KEY:
            raise BizException(message="EMBEDDING_API_KEY 未配置，无法初始化 text-embedding-v3。")
        if not settings.EMBEDDING_BASE_URL:
            raise BizException(message="EMBEDDING_BASE_URL 未配置，无法初始化 text-embedding-v3。")

        kwargs = {
            "model": self.model_name,
            "api_key": settings.EMBEDDING_API_KEY,
            "base_url": settings.EMBEDDING_BASE_URL,
        }
        if settings.EMBEDDING_DIMENSION is not None:
            kwargs["dimensions"] = settings.EMBEDDING_DIMENSION

        self.embeddings = OpenAIEmbeddings(**kwargs)

    def build_vector_index(self, chunks: List[Document]) -> PGVector:
        if not chunks:
            raise BizException(
                code=ErrorCode.CHUNCK_IS_NONE,
                message="文档块列表不能为空",
            )

        self.vectorstore = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.connection_string,
            use_jsonb=True,
            pre_delete_collection=self.pre_delete_collection,
        )
        self.vectorstore.add_documents(documents=chunks)
        logger.info(
            "Persisted %s document(s) into PGVector collection '%s'.",
            len(chunks),
            self.collection_name,
        )
        return self.vectorstore

    def load_index(self) -> PGVector:
        if not self.embeddings:
            self.setup_embeddings()

        self.vectorstore = PGVector.from_existing_index(
            embedding=self.embeddings,
            collection_name=self.collection_name,
            connection=self.connection_string,
            use_jsonb=True,
        )
        logger.info("PGVector collection '%s' has been loaded.", self.collection_name)
        return self.vectorstore

    def _resolve_connection_string(self, connection_string: str | None) -> str:
        raw_connection = (
            connection_string
            or settings.PGVECTOR_CONNECTION_STRING
            or settings.DATABASE_URL
        )
        if not raw_connection:
            raise BizException(
                message="未配置 PGVector 数据库连接，请设置 PGVECTOR_CONNECTION_STRING 或 DATABASE_URL。",
            )

        return self._normalize_pgvector_connection(raw_connection)

    @staticmethod
    def _normalize_pgvector_connection(connection_string: str) -> str:
        if "postgresql+asyncpg://" in connection_string:
            return connection_string.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
        if connection_string.startswith("postgresql://"):
            return connection_string.replace("postgresql://", "postgresql+psycopg://", 1)
        if connection_string.startswith("postgres://"):
            return connection_string.replace("postgres://", "postgresql+psycopg://", 1)
        return connection_string
