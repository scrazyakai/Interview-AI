from uuid import UUID

from fastapi import File, UploadFile

from app.crud import resume
from app.schemas.resume import ResumeParseResult


class ResumeService:
    async def parse_resume(self,pdf_byte:bytes,user_id:UUID) -> ResumeParseResult:
        """保存解析结果到数据库"""
        extracted =  await self._parse_text(pdf_byte)
        result =  await self._parse_pdf_by_llm(extracted,pdf_byte)
        await resume.save_resume(result,user_id)
        pass
    """通过pdfplumber来解析文本"""
    async def _parse_text(self,pdf_byte:bytes)-> dict:
        pass
    """将文本 + 简历原型发送给大模型"""
    async def _parse_pdf_by_llm(self,text:str,tables:list,pdf_byte:bytes)-> ResumeParseResult:
        pass

resume_service = ResumeService()