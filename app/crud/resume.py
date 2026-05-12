from uuid import UUID

from sqlalchemy import select, delete

from app.db.session import AsyncSessionLocal
from app.models.resume import Resume
from app.models.resume_education import ResumeEducation
from app.models.resume_project import ResumeProject
from app.models.resume_work_experience import ResumeWorkExperience
from app.schemas.resume import ResumeParseResult, WorkExperience, Education


async def create_resume_pending(user_id: UUID, file_name: str) -> int:
    """创建一条 pending 状态的简历记录，返回 id"""
    async with AsyncSessionLocal() as session:
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            parse_status="pending",
        )
        session.add(resume)
        await session.commit()
        await session.refresh(resume)
        return resume.id


async def fill_resume_parsed_data(resume_id: int, result: ResumeParseResult) -> None:
    """将解析结果写入已存在的 resume 记录"""
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Resume).where(Resume.id == resume_id))
        resume = res.scalars().first()
        if resume is None:
            return
        resume.parse_status = "success"
        resume.name = result.name
        resume.email = result.email
        resume.phone = result.phone
        resume.location = result.location
        resume.summary = result.summary
        resume.skills = result.skills
        resume.total_years_exp = result.total_years_exp
        if result.work_experiences:
            for i, w in enumerate(result.work_experiences):
                session.add(ResumeWorkExperience(
                    resume_id=resume_id, company=w.company, title=w.title or "",
                    start_date=w.start_date, end_date=w.end_date,
                    description=w.description, tech_stack=w.tech_stack, sort_order=i,
                ))
        if result.projects:
            for i, p in enumerate(result.projects):
                session.add(ResumeProject(
                    resume_id=resume_id, name=p.name, role=p.role,
                    start_date=p.start_date, end_date=p.end_date,
                    description=p.description, tech_stack=p.tech_stack, sort_order=i,
                ))
        if result.educations:
            for i, e in enumerate(result.educations):
                session.add(ResumeEducation(
                    resume_id=resume_id, school=e.school, degree=e.degree,
                    major=e.major, graduation_year=e.graduation_year, sort_order=i,
                ))
        await session.commit()


async def mark_resume_failed(resume_id: int) -> None:
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Resume).where(Resume.id == resume_id))
        resume = res.scalars().first()
        if resume:
            resume.parse_status = "failed"
            await session.commit()


async def save_resume(result: ResumeParseResult, user_id: UUID, file_name: str = "resume.pdf") -> None:
    async with AsyncSessionLocal() as session:
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            parse_status="success",
            name=result.name,
            email=result.email,
            phone=result.phone,
            location=result.location,
            summary=result.summary,
            skills=result.skills,
            total_years_exp=result.total_years_exp
        )
        session.add(resume)
        await session.flush()
        if result.work_experiences:
            for i,work_experience in enumerate(result.work_experiences):
                session.add(ResumeWorkExperience(
                    resume_id=resume.id,
                    company=work_experience.company,
                    title=work_experience.title or "",
                    start_date=work_experience.start_date,
                    end_date=work_experience.end_date,
                    description=work_experience.description,
                    tech_stack=work_experience.tech_stack,
                    sort_order=i,
                ))
        if result.projects:
            for i, project in enumerate(result.projects):
                session.add(ResumeProject(
                    resume_id=resume.id,
                    name=project.name,
                    role=project.role,
                    start_date=project.start_date,
                    end_date=project.end_date,
                    description=project.description,
                    tech_stack=project.tech_stack,
                    sort_order=i,
                ))
        if result.educations:
            for i,edu in enumerate(result.educations):
                session.add(ResumeEducation(
                    resume_id=resume.id,
                    school=edu.school,
                    degree=edu.degree,
                    major=edu.major,
                    graduation_year=edu.graduation_year,
                    sort_order=i,
                ))
        await session.commit()


async def get_resumes_by_user_id(session, user_id) -> list[Resume]:
    result = await session.execute(
        select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
    )
    return result.scalars().all()

async def get_resume_by_user_id(session, user_id) -> Resume | None:
    result = await session.execute(select(Resume).where(Resume.user_id == user_id))
    return result.scalars().first()

async def get_resume_by_id(session, resume_id: int, user_id: UUID) -> Resume | None:
    result = await session.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    return result.scalars().first()

async def update_resume(session, resume_id: int, user_id: UUID, data: dict) -> Resume | None:
    resume = await get_resume_by_id(session, resume_id, user_id)
    if resume is None:
        return None
    for key, value in data.items():
        setattr(resume, key, value)
    await session.flush()
    return resume

async def delete_resume(session, resume_id: int, user_id: UUID) -> bool:
    resume = await get_resume_by_id(session, resume_id, user_id)
    if resume is None:
        return False
    await session.execute(delete(ResumeWorkExperience).where(ResumeWorkExperience.resume_id == resume_id))
    await session.execute(delete(ResumeProject).where(ResumeProject.resume_id == resume_id))
    await session.execute(delete(ResumeEducation).where(ResumeEducation.resume_id == resume_id))
    await session.delete(resume)
    return True

async def get_educations_by_resume_id(session, resume_id) -> list[ResumeEducation]:
    result = await session.execute(
        select(ResumeEducation)
        .where(ResumeEducation.resume_id == resume_id)
        .order_by(ResumeEducation.sort_order)
    )
    return result.scalars().all()

async def get_work_experiences_by_resume_id(session, resume_id) -> list[ResumeWorkExperience]:
    result = await session.execute(
        select(ResumeWorkExperience)
        .where(ResumeWorkExperience.resume_id == resume_id)
        .order_by(ResumeWorkExperience.sort_order)
    )
    return result.scalars().all()

async def get_projects_by_resume_id(session, resume_id) -> list[ResumeProject]:
    result = await session.execute(
        select(ResumeProject)
        .where(ResumeProject.resume_id == resume_id)
        .order_by(ResumeProject.sort_order)
    )
    return result.scalars().all()


# ── 项目经历 增删改 ──────────────────────────────────────────
async def add_project(session, resume_id: int, data: dict) -> ResumeProject:
    count_result = await session.execute(
        select(ResumeProject).where(ResumeProject.resume_id == resume_id)
    )
    sort_order = len(count_result.scalars().all())
    obj = ResumeProject(resume_id=resume_id, sort_order=sort_order, **data)
    session.add(obj)
    await session.flush()
    return obj

async def update_project(session, project_id: int, resume_id: int, data: dict) -> ResumeProject | None:
    result = await session.execute(
        select(ResumeProject)
        .where(ResumeProject.id == project_id, ResumeProject.resume_id == resume_id)
    )
    obj = result.scalars().first()
    if obj is None:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    await session.flush()
    return obj

async def delete_project(session, project_id: int, resume_id: int) -> bool:
    result = await session.execute(
        select(ResumeProject)
        .where(ResumeProject.id == project_id, ResumeProject.resume_id == resume_id)
    )
    obj = result.scalars().first()
    if obj is None:
        return False
    await session.delete(obj)
    return True


# ── 工作经历 增删改 ──────────────────────────────────────────
async def add_work_experience(session, resume_id: int, data: dict) -> ResumeWorkExperience:
    count_result = await session.execute(
        select(ResumeWorkExperience).where(ResumeWorkExperience.resume_id == resume_id)
    )
    sort_order = len(count_result.scalars().all())
    obj = ResumeWorkExperience(resume_id=resume_id, sort_order=sort_order, **data)
    session.add(obj)
    await session.flush()
    return obj

async def update_work_experience(session, exp_id: int, resume_id: int, data: dict) -> ResumeWorkExperience | None:
    result = await session.execute(
        select(ResumeWorkExperience)
        .where(ResumeWorkExperience.id == exp_id, ResumeWorkExperience.resume_id == resume_id)
    )
    obj = result.scalars().first()
    if obj is None:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    await session.flush()
    return obj

async def delete_work_experience(session, exp_id: int, resume_id: int) -> bool:
    result = await session.execute(
        select(ResumeWorkExperience)
        .where(ResumeWorkExperience.id == exp_id, ResumeWorkExperience.resume_id == resume_id)
    )
    obj = result.scalars().first()
    if obj is None:
        return False
    await session.delete(obj)
    return True


# ── 教育经历 增删改 ──────────────────────────────────────────
async def add_education(session, resume_id: int, data: dict) -> ResumeEducation:
    count_result = await session.execute(
        select(ResumeEducation).where(ResumeEducation.resume_id == resume_id)
    )
    sort_order = len(count_result.scalars().all())
    obj = ResumeEducation(resume_id=resume_id, sort_order=sort_order, **data)
    session.add(obj)
    await session.flush()
    return obj

async def update_education(session, edu_id: int, resume_id: int, data: dict) -> ResumeEducation | None:
    result = await session.execute(
        select(ResumeEducation)
        .where(ResumeEducation.id == edu_id, ResumeEducation.resume_id == resume_id)
    )
    obj = result.scalars().first()
    if obj is None:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    await session.flush()
    return obj

async def delete_education(session, edu_id: int, resume_id: int) -> bool:
    result = await session.execute(
        select(ResumeEducation)
        .where(ResumeEducation.id == edu_id, ResumeEducation.resume_id == resume_id)
    )
    obj = result.scalars().first()
    if obj is None:
        return False
    await session.delete(obj)
    return True
