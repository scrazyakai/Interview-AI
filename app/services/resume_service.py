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
from app.crud.resume import get_resume_by_user_id
from app.db.session import AsyncSessionLocal
from app.schemas.resume import ResumeParseResult, Education, WorkExperience, Project, ResumeListItem, ResumeUpdateRequest, WorkExperienceRequest, EducationRequest, ProjectRequest
from app.core.exception import BizException

log = get_logger(__name__)


class ResumeService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key= settings.QWEN_API_KEY,
            base_url= settings.QWEN_API_URL,
            model= settings.QWEN_MODEL,
        )
    async def get_result(self, user_id: UUID) -> ResumeParseResult:
        async with AsyncSessionLocal() as db:
            resume_obj = await resume.get_resume_by_user_id(db, user_id)
            if resume_obj is None:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="简历不存在")

            educations = await resume.get_educations_by_resume_id(db, resume_obj.id)
            work_experiences = await resume.get_work_experiences_by_resume_id(db, resume_obj.id)
            projects = await resume.get_projects_by_resume_id(db, resume_obj.id)

        return ResumeParseResult(
            name=resume_obj.name,
            email=resume_obj.email,
            phone=resume_obj.phone,
            location=resume_obj.location,
            summary=resume_obj.summary,
            skills=resume_obj.skills or [],
            total_years_exp=resume_obj.total_years_exp,
            work_experiences=[
                WorkExperience(
                    company=w.company,
                    title=w.title,
                    start_date=w.start_date,
                    end_date=w.end_date,
                    description=w.description,
                    tech_stack=w.tech_stack or [],
                    resume_id=w.resume_id,
                    sort_order=w.sort_order,
                )
                for w in work_experiences
            ],
            projects=[
                Project(
                    name=p.name,
                    role=p.role,
                    start_date=p.start_date,
                    end_date=p.end_date,
                    description=p.description,
                    tech_stack=p.tech_stack or [],
                )
                for p in projects
            ],
            educations=[
                Education(
                    school=e.school,
                    degree=e.degree,
                    major=e.major,
                    graduation_year=e.graduation_year,
                )
                for e in educations
            ],
        )
    async def list_resumes(self, user_id: UUID) -> list[ResumeListItem]:
        async with AsyncSessionLocal() as db:
            resumes = await resume.get_resumes_by_user_id(db, user_id)
        return [ResumeListItem.model_validate(r) for r in resumes]

    async def get_result_by_id(self, resume_id: int, user_id: UUID) -> ResumeParseResult:
        async with AsyncSessionLocal() as db:
            resume_obj = await resume.get_resume_by_id(db, resume_id, user_id)
            if resume_obj is None:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="简历不存在")
            educations = await resume.get_educations_by_resume_id(db, resume_obj.id)
            work_experiences = await resume.get_work_experiences_by_resume_id(db, resume_obj.id)
            projects = await resume.get_projects_by_resume_id(db, resume_obj.id)

        return ResumeParseResult(
            name=resume_obj.name,
            email=resume_obj.email,
            phone=resume_obj.phone,
            location=resume_obj.location,
            summary=resume_obj.summary,
            skills=resume_obj.skills or [],
            total_years_exp=resume_obj.total_years_exp,
            work_experiences=[
                WorkExperience(
                    id=w.id, company=w.company, title=w.title, start_date=w.start_date,
                    end_date=w.end_date, description=w.description,
                    tech_stack=w.tech_stack or [], resume_id=w.resume_id, sort_order=w.sort_order,
                ) for w in work_experiences
            ],
            projects=[
                Project(
                    id=p.id, name=p.name, role=p.role, start_date=p.start_date,
                    end_date=p.end_date, description=p.description,
                    tech_stack=p.tech_stack or [], resume_id=p.resume_id, sort_order=p.sort_order,
                ) for p in projects
            ],
            educations=[
                Education(
                    id=e.id, school=e.school, degree=e.degree, major=e.major, graduation_year=e.graduation_year,
                ) for e in educations
            ],
        )

    async def update_resume(self, resume_id: int, user_id: UUID, data: ResumeUpdateRequest) -> bool:
        async with AsyncSessionLocal() as db:
            result = await resume.update_resume(
                db, resume_id, user_id,
                {k: v for k, v in data.model_dump().items() if v is not None}
            )
            if result is None:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="简历不存在")
            await db.commit()
        return True

    async def delete_resume(self, resume_id: int, user_id: UUID) -> bool:
        async with AsyncSessionLocal() as db:
            success = await resume.delete_resume(db, resume_id, user_id)
            if not success:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="简历不存在")
            await db.commit()
        return True

    # ── 工作经历 ──────────────────────────────────────────────
    async def add_work_experience(self, resume_id: int, user_id: UUID, data: WorkExperienceRequest) -> WorkExperience:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            obj = await resume.add_work_experience(db, resume_id, data.model_dump())
            await db.commit()
            return WorkExperience(id=obj.id, company=obj.company, title=obj.title,
                                  start_date=obj.start_date, end_date=obj.end_date,
                                  description=obj.description, tech_stack=obj.tech_stack or [],
                                  resume_id=obj.resume_id, sort_order=obj.sort_order)

    async def update_work_experience(self, resume_id: int, exp_id: int, user_id: UUID, data: WorkExperienceRequest) -> bool:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            obj = await resume.update_work_experience(db, exp_id, resume_id, data.model_dump())
            if obj is None:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="工作经历不存在")
            await db.commit()
        return True

    async def delete_work_experience(self, resume_id: int, exp_id: int, user_id: UUID) -> bool:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            success = await resume.delete_work_experience(db, exp_id, resume_id)
            if not success:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="工作经历不存在")
            await db.commit()
        return True

    # ── 教育经历 ──────────────────────────────────────────────
    async def add_education(self, resume_id: int, user_id: UUID, data: EducationRequest) -> Education:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            obj = await resume.add_education(db, resume_id, data.model_dump())
            await db.commit()
            return Education(id=obj.id, school=obj.school, degree=obj.degree,
                             major=obj.major, graduation_year=obj.graduation_year)

    async def update_education(self, resume_id: int, edu_id: int, user_id: UUID, data: EducationRequest) -> bool:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            obj = await resume.update_education(db, edu_id, resume_id, data.model_dump())
            if obj is None:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="教育经历不存在")
            await db.commit()
        return True

    async def delete_education(self, resume_id: int, edu_id: int, user_id: UUID) -> bool:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            success = await resume.delete_education(db, edu_id, resume_id)
            if not success:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="教育经历不存在")
            await db.commit()
        return True

    # ── 项目经历 ──────────────────────────────────────────────
    async def add_project(self, resume_id: int, user_id: UUID, data: ProjectRequest) -> Project:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            obj = await resume.add_project(db, resume_id, data.model_dump())
            await db.commit()
            return Project(id=obj.id, name=obj.name, role=obj.role,
                           start_date=obj.start_date, end_date=obj.end_date,
                           description=obj.description, tech_stack=obj.tech_stack or [],
                           resume_id=obj.resume_id, sort_order=obj.sort_order)

    async def update_project(self, resume_id: int, project_id: int, user_id: UUID, data: ProjectRequest) -> bool:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            obj = await resume.update_project(db, project_id, resume_id, data.model_dump())
            if obj is None:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="项目经历不存在")
            await db.commit()
        return True

    async def delete_project(self, resume_id: int, project_id: int, user_id: UUID) -> bool:
        async with AsyncSessionLocal() as db:
            await self._check_resume_owner(db, resume_id, user_id)
            success = await resume.delete_project(db, project_id, resume_id)
            if not success:
                raise BizException(code=ErrorCode.RESUME_IS_NONE, message="项目经历不存在")
            await db.commit()
        return True

    async def _check_resume_owner(self, db, resume_id: int, user_id: UUID):
        obj = await resume.get_resume_by_id(db, resume_id, user_id)
        if obj is None:
            raise BizException(code=ErrorCode.RESUME_IS_NONE, message="简历不存在")

    async def create_pending_resume(self, pdf_byte: bytes, user_id: UUID, file_name: str = "resume.pdf") -> int:
        """立即创建 pending 记录并返回 id，供后台任务使用"""
        if pdf_byte is None:
            raise BizException(code=ErrorCode.RESUME_IS_NONE, message="简历不能为空")
        return await resume.create_resume_pending(user_id, file_name)

    async def parse_resume_background(self, resume_id: int, pdf_byte: bytes) -> None:
        """后台异步解析，解析完成后更新数据库"""
        try:
            extracted = await self._parse_text(pdf_byte)
            result = await self._parse_pdf_by_llm(extracted, pdf_byte)
            await resume.fill_resume_parsed_data(resume_id, result)
        except Exception as e:
            log.error("Background resume parse failed for resume_id=%s: %s", resume_id, e)
            await resume.mark_resume_failed(resume_id)

    async def parse_resume(self, pdf_byte: bytes, user_id: UUID, file_name: str = "resume.pdf") -> bool:
        extracted = await self._parse_text(pdf_byte)
        result = await self._parse_pdf_by_llm(extracted, pdf_byte)
        await resume.save_resume(result, user_id, file_name)
        return True
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
                '  "projects": [{"name": "项目名称", "role": "担任角色", "start_date": "2023-01", "end_date": "2023-06", "description": "项目描述", "tech_stack": ["Vue", "FastAPI"]}],\n'
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