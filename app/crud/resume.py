from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.models.resume import Resume
from app.models.resume_education import ResumeEducation
from app.models.resume_work_experience import ResumeWorkExperience
from app.schemas.resume import ResumeParseResult


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

