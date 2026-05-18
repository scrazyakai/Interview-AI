"""
文档分块与向量嵌入索引构建。

流程：
  1. 清洗原始文本
  2. 三级切分策略：## → ### → 滑动窗口兜底
  3. 调用 Aliyun text-embedding 接口批量生成向量
  4. 写入 rag.document_chunks（含 embedding 列）
  5. 更新 rag.documents.status = indexed
"""

import re

from openai import AsyncOpenAI

from app.core.config.config import settings
from app.core.log import get_logger
from app.crud import rag_document as rag_crud
from app.db.session import AsyncSessionLocal

log = get_logger(__name__)

# ── 客户端初始化 ──────────────────────────────────────────────
# 阿里云 DashScope 兼容 OpenAI 协议，只需替换 base_url 和 api_key
_embedding_client = AsyncOpenAI(
    base_url=settings.EMBEDDING_BASE_URL,
    api_key=settings.EMBEDDING_API_KEY,
)

# text-embedding-v3 单条文本安全字符上限（8192 token，中文约 1~2 字符/token）
_MAX_CHARS = 1500


# ── 数据清洗 ─────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """
    对原始文档文本做详细清洗，输出适合 embedding 的纯净文本。

    清洗顺序很重要：先做字符级标准化，再做结构级清理，最后压缩空白。
    """
    # 1. 统一换行符，消除 Windows \r\n 和老 Mac \r
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. 去除零宽字符、软连字符、BOM
    #    这些字符在复制粘贴或 PDF 提取时容易混入，肉眼不可见但会干扰 tokenizer
    text = re.sub(r"[​‌‍‎‏﻿­]", "", text)

    # 3. 全角数字、字母 → 半角（常见于从 Word/PDF 复制的技术文档）
    #    全角范围 ０(U+FF10) ~ ９(U+FF19)，偏移量固定为 0xFEE0
    text = re.sub(
        r"[０-９Ａ-Ｚａ-ｚ]",
        lambda m: chr(ord(m.group()) - 0xFEE0),
        text,
    )

    # 4. 全角标点 → 半角（仅处理括号、冒号、分号等技术文档常见符号）
    #    保留中文引号「」『』等，它们有语义区分价值
    fullwidth_map = str.maketrans("（）【】：；，。！？", "()[]：；，。！？")
    text = text.translate(fullwidth_map)

    # 5. 去除 HTML 标签（Markdown 文档里偶尔夹杂 <br>、<span> 等）
    text = re.sub(r"<[^>]+>", "", text)

    # 6. 去除 Markdown 图片 ![alt](url) —— 图片信息无法嵌入纯文本向量
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # 7. Markdown 链接 [text](url) → text，保留可读文字，丢弃 URL
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)

    # 8. 去除行内代码反引号 `code` → code
    #    保留代码内容本身，只去掉格式符号（代码块 ``` 保留结构，不处理）
    text = re.sub(r"`([^`\n]+)`", r"\1", text)

    # 9. 去除 Markdown 水平分隔线（--- / *** / ___，单独成行）
    text = re.sub(r"^\s*[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)

    # 10. 去除行内多余的 Markdown 强调符号（加粗 **、斜体 *、删除线 ~~）
    #     只去修饰符号，保留文字内容
    text = re.sub(r"\*{1,3}([^*\n]+)\*{1,3}", r"\1", text)
    text = re.sub(r"~~([^~\n]+)~~", r"\1", text)

    # 11. 去除行尾空白（每行 rstrip）
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # 12. 压缩连续空行：超过 2 个换行 → 2 个（保留段落感，不过度压缩）
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 13. 去除每行仅由空格组成的行（清洗后可能产生的空壳行）
    text = re.sub(r"^\s+$", "", text, flags=re.MULTILINE)

    return text.strip()


# ── 切分辅助函数 ──────────────────────────────────────────────
def _split_by_heading(text: str, level: int) -> list[str]:
    """
    按指定标题级别切分，返回每个 section（含标题行本身）。

    使用前瞻断言 (?=^#{level} ) 切分，确保标题行不会被丢弃。
    level=2 → 按 ##，level=3 → 按 ###
    """
    pattern = rf"(?=^{'#' * level} )"
    sections = re.split(pattern, text, flags=re.MULTILINE)
    # 过滤空串，去掉头尾空白
    return [s.strip() for s in sections if s.strip()]


def _overlap_split(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    滑动窗口兜底切分：当语义边界（标题）无法将文本缩小到限制内时使用。
    """
    step = chunk_size - overlap
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


# ── Step 1：三级切分策略 ──────────────────────────────────────
def split_text(
    text: str,
    max_chars: int = _MAX_CHARS,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    三级切分策略，优先保留语义完整性：

    Level 1 — 按 ##（H2）切分
      每个 H2 section 视为一个独立主题，语义最完整。
    Level 2 — 超限则按 ###（H3）切分
      H2 内容过长时，用 H3 进一步细分。
    Level 3 — 仍超限则滑动窗口兜底
      无结构标题可用时，退化为字符级重叠切块。

    max_chars:  embedding 模型单条安全字符上限
    chunk_size: 滑动窗口每块字符数
    overlap:    滑动窗口重叠字符数
    """
    text = clean_text(text)
    if not text:
        return []

    result: list[str] = []

    # Level 1：按 ## 切分
    h2_sections = _split_by_heading(text, level=2)

    # 如果文档没有任何 ## 标题，把整篇文本当作一个待处理 section
    if not h2_sections:
        h2_sections = [text]

    for h2_section in h2_sections:
        if len(h2_section) <= max_chars:
            # H2 section 在限制内，直接使用
            result.append(h2_section)
            continue

        # Level 2：H2 过长，尝试按 ### 切分
        h3_sections = _split_by_heading(h2_section, level=3)

        if len(h3_sections) <= 1:
            # 该 H2 section 内没有 ### 标题（或本身就是 ### 级），直接兜底
            log.debug("H2 section 超限且无 H3，走滑动窗口: %d chars", len(h2_section))
            result.extend(_overlap_split(h2_section, chunk_size, overlap))
            continue

        for h3_section in h3_sections:
            if len(h3_section) <= max_chars:
                result.append(h3_section)
            else:
                # Level 3：H3 section 仍然超限，滑动窗口兜底
                log.debug("H3 section 超限，走滑动窗口: %d chars", len(h3_section))
                result.extend(_overlap_split(h3_section, chunk_size, overlap))

    return result


# ── Step 2：批量生成 Embedding ────────────────────────────────
async def embed_texts(texts: list[str], batch_size: int = 25) -> list[list[float]]:
    """
    分批调用阿里云 text-embedding API，返回与 texts 等长的向量列表。

    batch_size: 每批最多发送的文本数（阿里云单次限制 25）
    """
    if not texts:
        return []

    all_vectors: list[list[float]] = []

    for batch_start in range(0, len(texts), batch_size):
        batch = texts[batch_start : batch_start + batch_size]

        log.info(
            "embedding batch %d/%d，共 %d 条",
            batch_start // batch_size + 1,
            -(-len(texts) // batch_size),  # ceil(n/b)，等价于 math.ceil
            len(batch),
        )

        response = await _embedding_client.embeddings.create(
            model=settings.EMBEDDING_MODEL_NAME,
            input=batch,
        )

        # 按 index 排序，防御 API 返回乱序（协议保证有序，但显式排序更安全）
        sorted_data = sorted(response.data, key=lambda e: e.index)
        all_vectors.extend(item.embedding for item in sorted_data)

    return all_vectors


# ── Step 3 & 4：主入口 ────────────────────────────────────────
async def build_document_index(doc_id: int) -> None:
    """
    对指定文档执行完整的索引构建流程：
      清洗 → 切块 → embedding → 写 chunks → 更新状态

    由 admin API 以后台任务形式调用，不会阻塞 HTTP 响应。
    """
    async with AsyncSessionLocal() as session:
        doc = await rag_crud.get_document_by_id(session, doc_id)
        if doc is None:
            log.error("build_document_index: doc_id=%d 不存在", doc_id)
            return

        log.info("开始索引构建 doc_id=%d title=%s", doc_id, doc.title)

        try:
            # ① 切块（内含清洗）
            chunks = split_text(doc.original_content)
            if not chunks:
                raise ValueError("文档内容为空，无法切块")

            log.info("切块完成，共 %d 块", len(chunks))

            # ② 批量 Embedding
            vectors = await embed_texts(chunks)

            # ③ 准备 chunk 记录（metadata_ 存 doc_uuid + category，供检索时过滤）
            chunk_rows = [
                {
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "chunk_text": text,
                    "embedding": vector,
                    "metadata_": {
                        "doc_uuid": str(doc.doc_uuid),
                        "category": doc.category,
                    },
                }
                for idx, (text, vector) in enumerate(zip(chunks, vectors))
            ]

            # ④ 先删旧 chunks（支持重新索引），再批量插入
            await rag_crud.delete_chunks_by_doc(session, doc_id)
            await rag_crud.create_chunks(session, chunk_rows)

            # ⑤ 更新状态
            await rag_crud.update_document_status(
                session, doc_id, status="indexed", chunk_count=len(chunks)
            )

            await session.commit()
            log.info("索引构建完成 doc_id=%d，写入 %d 个 chunk", doc_id, len(chunks))

        except Exception as exc:
            await session.rollback()
            await rag_crud.update_document_status(session, doc_id, status="failed")
            await session.commit()
            log.exception("索引构建失败 doc_id=%d: %s", doc_id, exc)
            raise
