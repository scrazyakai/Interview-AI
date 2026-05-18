from pathlib import Path

from app.core.config.config import settings
from app.core.log import get_logger
from app.models.interview_session import InterviewSession
from app.rag.retrieval import format_context, retrieve

log = get_logger(__name__)


async def build_instructions(interview: InterviewSession | None = None) -> str:
    prompt_path = settings.QWEN_REALTIME_SYSTEM_ROLE
    if not prompt_path:
        raise ValueError("Missing QWEN_REALTIME_SYSTEM_ROLE")

    template = Path(prompt_path).read_text(encoding="utf-8").strip()

    # ── RAG 检索 ──────────────────────────────────────────────
    # 用 job_title + job_description 前 300 字拼成查询，覆盖岗位的核心技术域
    # job_description 截断是为了避免查询向量被过长文本稀释，重点放在核心词上
    rag_context = ""
    if interview:
        job_title = getattr(interview, "job_title", "") or ""
        job_desc = getattr(interview, "job_description", "") or ""
        query = f"{job_title} {job_desc[:300]}".strip()

        if query:
            try:
                chunks = await retrieve(query, top_k=6)
                raw_context = format_context(chunks, max_chars=3000)
                # 只有检索到内容时才生成区块标题，避免 prompt 出现空段落
                if raw_context:
                    rag_context = (
                        "以下内容来自知识库，可作为出题和评估参考，"
                        "优先结合以下知识点进行提问：\n\n"
                        + raw_context
                    )
            except Exception:
                # 检索失败不应中断面试，降级为无知识库模式
                log.exception("RAG 检索失败，降级为无知识库模式")

    return template.format(
        job_function=getattr(interview, "job_function", "") or "",
        job_title=getattr(interview, "job_title", "") or "",
        job_description=getattr(interview, "job_description", "") or "",
        experience_level=getattr(interview, "experience_level", "") or "",
        mode=getattr(interview, "mode", "") or "",
        resume_text=getattr(interview, "resume_text", "") or "",
        rag_context=rag_context,
    )
