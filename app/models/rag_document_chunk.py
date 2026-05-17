from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.core.config.config import settings

EMBEDDING_DIM: int = settings.EMBEDDING_DIMENSION or 1024


class RagDocumentChunk(Base):
    """文档分块及其向量嵌入"""

    __tablename__ = "document_chunks"
    __table_args__ = {"schema": "rag"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    doc_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("rag.documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    # pgvector 列，存储 embedding
    embedding: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )

    # 存储 chunk 元数据：doc_uuid、category、chunk_index 等
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )
