"""
RAG 检索模块。

流程：
  1. 对用户问题调用 embedding API，得到查询向量
  2. 用余弦距离在 pgvector 中检索最相似的 document chunks
  3. 过滤低相关结果，组装成可注入 prompt 的上下文文本
"""

from dataclasses import dataclass

from app.core.log import get_logger
from app.crud import rag_document as rag_crud
from app.db.session import AsyncSessionLocal
from app.rag.index_construction import embed_texts

log = get_logger(__name__)


# ── 返回数据结构 ───────────────────────────────────────────────
@dataclass
class RetrievedChunk:
    """
    单条检索结果。

    使用 dataclass 而非 Pydantic：这是内部数据结构，不需要序列化校验，
    dataclass 开销更小，且字段含义一目了然。
    """
    chunk_text: str
    distance: float          # 余弦距离，越小越相似（0 = 完全相同）
    similarity: float        # 1 - distance，更直觉的相似度表示
    category: str | None
    doc_uuid: str | None
    chunk_index: int


# ── 主检索函数 ────────────────────────────────────────────────
async def retrieve(
    query: str,
    top_k: int = 5,
    category: str | None = None,
    distance_threshold: float = 0.5,
) -> list[RetrievedChunk]:
    """
    对 query 做全流程检索，返回相关 chunk 列表（按相似度降序）。

    query:              用户提问或面试问题文本
    top_k:              最多返回几条（数据库层已限制，这里是最终上限）
    category:           限定检索范围（frontend/backend/algorithm 等）
    distance_threshold: 余弦距离上限，超过则丢弃（默认 0.5，相似度 ≥ 0.5）
    """
    if not query or not query.strip():
        return []

    # ① 将 query 向量化（embed_texts 接受列表，返回列表；取第 0 个）
    query_vectors = await embed_texts([query.strip()])
    query_vector = query_vectors[0]

    # ② 数据库向量检索
    async with AsyncSessionLocal() as session:
        rows = await rag_crud.search_similar_chunks(
            session,
            query_vector=query_vector,
            top_k=top_k,
            category=category,
            distance_threshold=distance_threshold,
        )

    if not rows:
        log.info("retrieve: 未找到相关 chunk，query=%r category=%s", query[:50], category)
        return []

    # ③ 转换为结构化结果，distance 越小 → similarity 越高 → 排在前面
    results = [
        RetrievedChunk(
            chunk_text=chunk.chunk_text,
            distance=round(dist, 4),
            similarity=round(1 - dist, 4),
            category=chunk.metadata_.get("category") if chunk.metadata_ else None,
            doc_uuid=chunk.metadata_.get("doc_uuid") if chunk.metadata_ else None,
            chunk_index=chunk.chunk_index,
        )
        for chunk, dist in rows
    ]

    log.info(
        "retrieve: 找到 %d 条结果，top similarity=%.4f，query=%r",
        len(results),
        results[0].similarity,
        query[:50],
    )

    return results


# ── 上下文组装 ────────────────────────────────────────────────
def format_context(chunks: list[RetrievedChunk], max_chars: int = 3000) -> str:
    """
    将检索到的 chunks 组装成可注入 prompt 的上下文字符串。

    max_chars: 防止上下文过长撑爆 LLM 的 context window，超出后截断。

    格式示例：
      [参考资料 1]（相似度 0.87）
      内容...

      [参考资料 2]（相似度 0.76）
      内容...
    """
    if not chunks:
        return ""

    parts: list[str] = []
    total = 0

    for i, chunk in enumerate(chunks, start=1):
        header = f"[参考资料 {i}]（相似度 {chunk.similarity:.2f}）"
        block = f"{header}\n{chunk.chunk_text}"

        # 超出总字符限制时截断当前块，然后停止
        remaining = max_chars - total
        if remaining <= 0:
            break
        if len(block) > remaining:
            block = block[:remaining] + "…"
            parts.append(block)
            break

        parts.append(block)
        total += len(block)

    return "\n\n".join(parts)
