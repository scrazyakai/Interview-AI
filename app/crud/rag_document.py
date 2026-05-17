from uuid import UUID

from sqlalchemy import delete, func, select, update

from app.models.rag_document import RagDocument
from app.models.rag_document_chunk import RagDocumentChunk


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
