from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RagDocument(Base):
    """上传的原始文档，保留完整内容"""

    __tablename__ = "rag_documents"
    __table_args__ = {"schema": "interview"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    doc_uuid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        unique=True,
        server_default=text("gen_random_uuid()"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # 保留原始内容，方便二次检索和审计
    original_content: Mapped[str] = mapped_column(Text, nullable=False)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # pdf / txt / md
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # frontend / backend / database / algorithm / behavioral / general
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default=text("'general'")
    )

    # pending / indexed / failed
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pending'")
    )

    chunk_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
