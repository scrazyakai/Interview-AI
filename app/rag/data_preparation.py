import logging
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DataPreparation:
    """Load, split, and enrich question-bank documents for RAG."""

    MAX_QUESTION_CHUNK_SIZE = 1800
    FALLBACK_CHUNK_SIZE = 1000
    FALLBACK_CHUNK_OVERLAP = 120

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.documents: List[Document] = []

        self.tech_keywords = {
            "Java": ["java", "jvm", "spring", "mybatis", "hibernate"],
            "Python": ["python", "django", "flask", "fastapi"],
            "数据库": ["mysql", "redis", "mongodb", "postgresql", "sql"],
            "并发": ["线程", "并发", "锁", "synchronized", "volatile", "cas"],
            "网络": ["tcp", "http", "网络", "socket"],
            "算法": ["算法", "数据结构", "链表", "树", "排序"],
            "设计模式": ["设计模式", "单例", "工厂", "观察者", "策略"],
            "分布式": ["分布式", "微服务", "消息队列", "kafka", "rocketmq"],
        }

        self.difficulty_keywords = {
            "easy": ["基础", "简单", "入门", "什么是"],
            "medium": ["原理", "机制", "如何", "为什么", "区别"],
            "hard": ["优化", "调优", "源码", "底层", "实现"],
        }

    def load_documents(self) -> List[Document]:
        logger.info("Loading documents from %s", self.data_path)

        data_path_obj = Path(self.data_path)
        if not data_path_obj.is_absolute() and not data_path_obj.exists():
            project_root = Path(__file__).parent.parent.parent
            data_path_obj = project_root / self.data_path

        if data_path_obj.is_file():
            self.documents = self._load_single_file(data_path_obj)
        elif data_path_obj.is_dir():
            self.documents = self._load_directory(data_path_obj)
        else:
            raise ValueError(
                f"Path does not exist: {self.data_path} "
                f"(resolved to {data_path_obj.absolute()})"
            )

        logger.info("Loaded %s document chunks", len(self.documents))
        return self.documents

    def _load_single_file(self, file_path: Path) -> List[Document]:
        logger.info("Loading file: %s", file_path)

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        content = self._clean_text(content)
        chunks = self._split_by_questions(content)

        documents: List[Document] = []
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            question_title = self._extract_question_title(chunk)
            doc_id = str(uuid.uuid4())

            doc = Document(
                page_content=chunk,
                metadata={
                    "source": str(file_path),
                    "doc_id": doc_id,
                    "chunk_index": idx,
                    "question_title": question_title,
                },
            )

            self._enhance_metadata(doc)
            documents.append(doc)

        return documents

    def _load_directory(self, dir_path: Path) -> List[Document]:
        documents: List[Document] = []

        for md_file in dir_path.rglob("*.md"):
            logger.info("Processing file: %s", md_file)
            documents.extend(self._load_single_file(md_file))

        return documents

    def _clean_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n")
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        lines = [line.rstrip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    def _split_by_questions(self, content: str) -> List[str]:
        """Split a markdown question bank into question-level chunks.

        Each chunk starts with a `## ` heading. Nested `### ` sections such as
        answers or explanations remain in the same chunk.
        """
        if not content.strip():
            return []

        chunks = re.split(r"(?=^##\s+)", content, flags=re.MULTILINE)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

        if not chunks:
            return []

        question_chunks = [chunk for chunk in chunks if re.match(r"^##\s+", chunk)]
        ignored_chunk_count = len(chunks) - len(question_chunks)

        if question_chunks:
            if ignored_chunk_count > 0:
                logger.warning(
                    "Ignored %s non-question chunk(s) before the first '##' heading.",
                    ignored_chunk_count,
                )
            return self._apply_large_chunk_fallback(question_chunks)

        logger.warning("No '##' headings found; returning the whole document as one chunk.")
        return self._apply_large_chunk_fallback([content.strip()])

    def _apply_large_chunk_fallback(self, chunks: List[str]) -> List[str]:
        normalized_chunks: List[str] = []
        for chunk in chunks:
            normalized_chunks.extend(self._split_large_question_chunk(chunk))
        return normalized_chunks

    def _split_large_question_chunk(self, chunk: str) -> List[str]:
        if len(chunk) <= self.MAX_QUESTION_CHUNK_SIZE:
            return [chunk]

        title_match = re.match(r"^(##\s+.+?)(?:\n+|$)", chunk, re.MULTILINE)
        if not title_match:
            return self._force_split_with_overlap(chunk)

        title_line = title_match.group(1).strip()
        remainder = chunk[title_match.end():].strip()

        if not remainder:
            return [chunk]

        logger.warning(
            "Question chunk exceeds %s chars; applying fallback split for '%s'.",
            self.MAX_QUESTION_CHUNK_SIZE,
            title_line,
        )

        sections = self._split_preserving_delimiter(remainder, r"(?=^###\s+)")
        if len(sections) <= 1:
            sections = self._split_preserving_delimiter(remainder, r"(?=\n\n)")

        body_chunks = self._merge_segments_with_limit(sections, self.MAX_QUESTION_CHUNK_SIZE - len(title_line) - 2)
        result: List[str] = []
        for body_chunk in body_chunks:
            candidate = f"{title_line}\n\n{body_chunk.strip()}".strip()
            if len(candidate) <= self.MAX_QUESTION_CHUNK_SIZE:
                result.append(candidate)
            else:
                result.extend(self._force_split_with_overlap(candidate))

        return result or [chunk]

    def _split_preserving_delimiter(self, text: str, pattern: str) -> List[str]:
        parts = re.split(pattern, text, flags=re.MULTILINE)
        return [part.strip() for part in parts if part.strip()]

    def _merge_segments_with_limit(self, segments: List[str], limit: int) -> List[str]:
        if limit <= 0:
            return segments

        merged: List[str] = []
        current = ""

        for segment in segments:
            if len(segment) > limit:
                if current:
                    merged.append(current.strip())
                    current = ""
                merged.extend(self._force_split_with_overlap(segment, limit))
                continue

            candidate = segment if not current else f"{current}\n\n{segment}"
            if len(candidate) <= limit:
                current = candidate
            else:
                merged.append(current.strip())
                current = segment

        if current:
            merged.append(current.strip())

        return merged

    def _force_split_with_overlap(self, text: str, chunk_size: int | None = None) -> List[str]:
        size = chunk_size or self.FALLBACK_CHUNK_SIZE
        overlap = min(self.FALLBACK_CHUNK_OVERLAP, max(size // 4, 0))

        if len(text) <= size:
            return [text.strip()]

        pieces: List[str] = []
        start = 0
        text = text.strip()

        while start < len(text):
            end = min(start + size, len(text))
            if end < len(text):
                split_at = text.rfind("\n\n", start, end)
                if split_at <= start:
                    split_at = text.rfind("\n", start, end)
                if split_at > start:
                    end = split_at

            piece = text[start:end].strip()
            if piece:
                pieces.append(piece)

            if end >= len(text):
                break

            start = max(end - overlap, start + 1)

        return pieces or [text]

    def _extract_question_title(self, chunk: str) -> str:
        match = re.match(r"^##\s+(.+)$", chunk, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "未知题目"

    def _enhance_metadata(self, doc: Document) -> None:
        content = doc.page_content.lower()
        question_title = doc.metadata.get("question_title", "").lower()

        skills = []
        for tech, keywords in self.tech_keywords.items():
            if any(keyword in content or keyword in question_title for keyword in keywords):
                skills.append(tech)
        doc.metadata["skills"] = skills if skills else ["通用"]

        difficulty = "medium"
        for level, keywords in self.difficulty_keywords.items():
            if any(keyword in question_title for keyword in keywords):
                difficulty = level
                break
        doc.metadata["difficulty"] = difficulty

        doc.metadata["question_type"] = self._identify_question_type(question_title)
        doc.metadata["keywords"] = self._extract_keywords(content, question_title)

    def _identify_question_type(self, title: str) -> str:
        title_lower = title.lower()

        if any(word in title_lower for word in ["什么是", "定义", "概念"]):
            return "概念题"
        if any(word in title_lower for word in ["区别", "对比", "比较"]):
            return "对比题"
        if any(word in title_lower for word in ["原理", "机制", "如何实现"]):
            return "原理题"
        if any(word in title_lower for word in ["场景", "应用", "使用"]):
            return "场景题"
        if any(word in title_lower for word in ["优化", "调优", "性能"]):
            return "优化题"
        return "综合题"

    def _extract_keywords(self, content: str, title: str) -> List[str]:
        keywords = set()

        title_words = re.findall(r"[\u4e00-\u9fa5a-zA-Z]+", title)
        keywords.update(word for word in title_words if len(word) > 1)

        for tech_keywords in self.tech_keywords.values():
            for keyword in tech_keywords:
                if keyword in content:
                    keywords.add(keyword)

        return list(keywords)[:10]

    def get_documents_by_skill(self, skill: str) -> List[Document]:
        return [doc for doc in self.documents if skill in doc.metadata.get("skills", [])]

    def get_documents_by_difficulty(self, difficulty: str) -> List[Document]:
        return [
            doc
            for doc in self.documents
            if doc.metadata.get("difficulty") == difficulty
        ]

    def get_statistics(self) -> Dict[str, Any]:
        if not self.documents:
            return {}

        skill_count: Dict[str, int] = {}
        for doc in self.documents:
            for skill in doc.metadata.get("skills", []):
                skill_count[skill] = skill_count.get(skill, 0) + 1

        difficulty_count: Dict[str, int] = {}
        for doc in self.documents:
            difficulty = doc.metadata.get("difficulty", "unknown")
            difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1

        type_count: Dict[str, int] = {}
        for doc in self.documents:
            question_type = doc.metadata.get("question_type", "unknown")
            type_count[question_type] = type_count.get(question_type, 0) + 1

        return {
            "total_questions": len(self.documents),
            "skill_distribution": skill_count,
            "difficulty_distribution": difficulty_count,
            "type_distribution": type_count,
        }
