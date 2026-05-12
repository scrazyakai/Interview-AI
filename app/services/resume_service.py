import asyncio
import io
from uuid import UUID

import pdfplumber
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from openai import  AsyncOpenAI
from pydantic import ValidationError

from app.core.config.config import settings
from app.core.exception import ErrorCode
from app.core.log import get_logger
from app.crud import resume
from app.schemas.resume import ResumeParseResult
from app.core.exception import BizException

log = get_logger(__name__)


class ResumeService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key= settings.QWEN_API_KEY,
            base_url= settings.QWEN_API_URL,
            model= settings.QWEN_MODEL,
        )
    async def parse_resume(self, pdf_byte: bytes, user_id: UUID, file_name: str = "resume.pdf") -> ResumeParseResult:
        extracted = await self._parse_text(pdf_byte)
        result = await self._parse_pdf_by_llm(extracted, pdf_byte)
        await resume.save_resume(result, user_id, file_name)
        return result
    """通过pdfplumber来解析文本"""
    async def _parse_text(self,pdf_byte:bytes)-> str:

        if pdf_byte is None:
            raise BizException(code=ErrorCode.RESUME_IS_NONE,message="简历不能为空")
        text_parts =[]
        with pdfplumber.open(io.BytesIO(pdf_byte)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
        return "\n\n".join(text_parts)


    """将文本 + 简历原型发送给大模型"""
    async def _parse_pdf_by_llm(self,text:str,pdf_byte:bytes)-> ResumeParseResult:
        if text is None:
            raise BizException(code=ErrorCode.RESUME_TEXT_IS_NONE,message="未提取到简历内容")
        if pdf_byte is None:
            raise BizException(code=ErrorCode.RESUME_IS_NOT_UPLOAD,message="简历未上传")
        client = AsyncOpenAI(api_key=settings.QWEN_API_KEY, base_url=settings.QWEN_API_URL)

        uploaded = await client.files.create(
            file=("resume.pdf", pdf_byte, "application/pdf"),
            purpose="file-extract",
        )

        structured_llm = self.llm.with_structured_output(ResumeParseResult)
        message = [
            SystemMessage(
                f"fileid://{uploaded.id}\n\n"
                "你是一个简历解析助手。请从简历中提取信息，严格按照以下平铺 JSON 结构返回，"
                "不要嵌套子对象，缺失字段填 null：\n"
                "{\n"
                '  "name": "姓名",\n'
                '  "email": "邮箱",\n'
                '  "phone": "电话",\n'
                '  "location": "所在城市",\n'
                '  "summary": "个人简介或求职意向",\n'
                '  "skills": ["技能1", "技能2"],\n'
                '  "work_experiences": [{"company": "公司名", "title": "职位", "start_date": "2022-03", "end_date": "2024-01", "description": "工作描述", "tech_stack": []}],\n'
                '  "educations": [{"school": "学校名", "degree": "学历", "major": "专业", "graduation_year": "2020"}],\n'
                '  "total_years_exp": 3.5,\n'
                '  "raw_text": null\n'
                "}"
            ),
            HumanMessage(content=f"以下是从 PDF 提取的备用文本供参考：\n\n{text}"),
        ]
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                return await structured_llm.ainvoke(message)
            except (OutputParserException, ValidationError) as e:
                last_error = e
                log.warning("Resume structured output attempt %d/3 failed: %s", attempt + 1, e)
                if attempt < 2:
                    await asyncio.sleep(1)
        log.error("All 3 resume parse attempts failed, last error: %s", last_error)
        raise BizException(code=ErrorCode.RESUME_PARSE_FILED, message="简历解析失败")


resume_service = ResumeService()