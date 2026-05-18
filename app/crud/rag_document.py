from uuid import UUID

from sqlalchemy import delete, func, select, update

from app.models.rag_document import RagDocument
from app.models.rag_document_chunk import RagDocumentChunk


# ── 向量检索 ─────────────────────────────────────────────────

async def search_similar_chunks(
    session,
    query_vector: list[float],
    top_k: int = 5,
    category: str | None = None,
    distance_threshold: float = 0.5,
) -> list[tuple[RagDocumentChunk, float]]:
    """
    用余弦距离（<=>）在 pgvector 中检索最相似的 chunks。

    返回 (chunk, distance) 元组列表，distance 越小越相似（0 = 完全相同）。

    category:           不传则搜索全部类别
    distance_threshold: 超过此距离的结果丢弃（余弦距离范围 0~2）
    """
    # cosine_distance() 是 pgvector SQLAlchemy 扩展注册的列方法
    distance_col = RagDocumentChunk.embedding.cosine_distance(query_vector).label("distance")

    stmt = (
        select(RagDocumentChunk, distance_col)
        .where(RagDocumentChunk.embedding.isnot(None))
        .order_by(distance_col)
        .limit(top_k)
    )

    # 按 category 过滤：metadata_ 是 JSONB，用 ->> 取文本值比较
    if category:
        stmt = stmt.where(
            RagDocumentChunk.metadata_["category"].astext == category
        )

    rows = (await session.execute(stmt)).all()

    # 过滤掉距离过大的结果，再返回
    return [(chunk, dist) for chunk, dist in rows if dist <= distance_threshold]


# ── 文档 ─────────────────────────────────────────────────────

async def create_document(
    session,
    title: str,
    original_content: str,
    file_name: str,
    file_type: str,
    category: str,
    created_by: UUID,
) -> RagDocument:
    doc = RagDocument(
        title=title,
        original_content=original_content,
        file_name=file_name,
        file_type=file_type,
        category=category,
        created_by=created_by,
        status="pending",
    )
    session.add(doc)
    await session.flush()
    return doc


async def get_document_by_id(session, doc_id: int) -> RagDocument | None:
    result = await session.execute(select(RagDocument).where(RagDocument.id == doc_id))
    return result.scalars().first()


async def list_documents(
    session, offset: int = 0, limit: int = 20
) -> tuple[list[RagDocument], int]:
    count_result = await session.execute(select(func.count()).select_from(RagDocument))
    total = count_result.scalar_one()
    result = await session.execute(
        select(RagDocument)
        .order_by(RagDocument.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total


async def update_document_status(
    session, doc_id: int, status: str, chunk_count: int = 0
) -> None:
    await session.execute(
        update(RagDocument)
        .where(RagDocument.id == doc_id)
        .values(status=status, chunk_count=chunk_count)
    )


async def delete_document(session, doc_id: int) -> bool:
    doc = await get_document_by_id(session, doc_id)
    if doc is None:
        return False
    # chunks 通过 CASCADE 自动删除
    await session.delete(doc)
    return True


# ── 分块 ─────────────────────────────────────────────────────

async def create_chunks(
    session, chunks: list[dict]
) -> list[RagDocumentChunk]:
    """批量写入 chunks，chunks 每项含 doc_id/chunk_index/chunk_text/embedding/metadata_"""
    objs = [RagDocumentChunk(**c) for c in chunks]
    session.add_all(objs)
    await session.flush()
    return objs


async def delete_chunks_by_doc(session, doc_id: int) -> None:
    await session.execute(
        delete(RagDocumentChunk).where(RagDocumentChunk.doc_id == doc_id)
    )


# ── 文档统计 ─────────────────────────────────────────────────

async def count_documents(session) -> int:
    result = await session.execute(select(func.count()).select_from(RagDocument))
    return result.scalar_one()


async def count_chunks(session) -> int:
    result = await session.execute(select(func.count()).select_from(RagDocumentChunk))
    return result.scalar_one()


async def count_indexed_documents(session) -> int:
    result = await session.execute(
        select(func.count()).select_from(RagDocument).where(RagDocument.status == "indexed")
    )
    return result.scalar_one()
