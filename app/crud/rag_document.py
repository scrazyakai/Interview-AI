from uuid import UUID

from sqlalchemy import delete, func, select, update

from app.models.rag_document import RagDocument
from app.models.rag_document_chunk import RagDocumentChunk
from app.models.user import UserModel


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


# ── 用户管理（admin 视角） ─────────────────────────────────────

async def list_users(
    session, offset: int = 0, limit: int = 20
) -> tuple[list[UserModel], int]:
    count_result = await session.execute(select(func.count()).select_from(UserModel))
    total = count_result.scalar_one()
    result = await session.execute(
        select(UserModel)
        .order_by(UserModel.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all(), total


async def update_user_role(session, user_id: UUID, role_type: int) -> UserModel | None:
    result = await session.execute(
        select(UserModel).where(UserModel.user_id == user_id)
    )
    user = result.scalars().first()
    if user is None:
        return None
    user.role_type = role_type
    await session.flush()
    return user


# ── 统计 ─────────────────────────────────────────────────────

async def get_stats(session) -> dict:
    total_users = (
        await session.execute(select(func.count()).select_from(UserModel))
    ).scalar_one()
    total_docs = (
        await session.execute(select(func.count()).select_from(RagDocument))
    ).scalar_one()
    total_chunks = (
        await session.execute(select(func.count()).select_from(RagDocumentChunk))
    ).scalar_one()
    indexed_docs = (
        await session.execute(
            select(func.count()).select_from(RagDocument).where(RagDocument.status == "indexed")
        )
    ).scalar_one()
    return {
        "total_users": total_users,
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "indexed_documents": indexed_docs,
    }
