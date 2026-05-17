"""
文档分块与向量嵌入索引构建。

流程：
  1. 将原始文本按 chunk_size / overlap 切分
  2. 调用 Aliyun text-embedding 接口批量生成向量
  3. 写入 rag.document_chunks（含 embedding 列）
  4. 更新 rag.documents.status = indexed
"""

from openai import AsyncOpenAI

from app.core.config.config import settings
from app.core.log import get_logger
from app.crud import rag_document as rag_crud
from app.db.session import AsyncSessionLocal

log = get_logger(__name__)

# 每个 chunk 的最大字符数
CHUNK_SIZE = 800
# 相邻 chunk 的重叠字符数，保留上下文连贯性
CHUNK_OVERLAP = 100
# 每次批量请求的 chunk 数量，避免超出 API 限制
EMBED_BATCH_SIZE = 25


def _split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """按固定大小切分，带重叠窗口"""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]


async def _embed_texts(texts: list[str]) -> list[list[float]]:
    """调用 Aliyun OpenAI 兼容接口批量获取嵌入向量"""
    client = AsyncOpenAI(
        api_key=settings.EMBEDDING_API_KEY,
        base_url=settings.EMBEDDING_BASE_URL,
    )
    all_vectors: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i: i + EMBED_BATCH_SIZE]
        resp = await client.embeddings.create(
            model=settings.EMBEDDING_MODEL_NAME,
            input=batch,
        )
        all_vectors.extend([item.embedding for item in resp.data])
    return all_vectors


async def build_document_index(doc_id: int) -> None:
    """
    后台任务入口：对指定文档分块、嵌入并写库。
    调用方：admin 上传文档后通过 BackgroundTasks 触发。
    """
    async with AsyncSessionLocal() as session:
        doc = await rag_crud.get_document_by_id(session, doc_id)
        if doc is None:
            log.warning("[rag] build_document_index: doc_id=%s not found", doc_id)
            return

        try:
            chunks = _split_text(doc.original_content)
            log.info("[rag] doc_id=%s split into %d chunks", doc_id, len(chunks))

            vectors = await _embed_texts(chunks)

            chunk_rows = [
                {
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "chunk_text": text,
                    "embedding": vec,
                    "metadata_": {
                        "doc_uuid": str(doc.doc_uuid),
                        "category": doc.category,
                        "chunk_index": idx,
                    },
                }
                for idx, (text, vec) in enumerate(zip(chunks, vectors))
            ]

            # 先清除旧 chunks（重建场景），再写入新的
            await rag_crud.delete_chunks_by_doc(session, doc_id)
            await rag_crud.create_chunks(session, chunk_rows)
            await rag_crud.update_document_status(session, doc_id, "indexed", len(chunk_rows))
            await session.commit()

            log.info("[rag] doc_id=%s indexed successfully, chunks=%d", doc_id, len(chunk_rows))

        except Exception:
            await session.rollback()
            await rag_crud.update_document_status(session, doc_id, "failed")
            await session.commit()
            log.exception("[rag] build_document_index failed for doc_id=%s", doc_id)
