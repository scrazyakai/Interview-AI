from typing import Optional

from pydantic import BaseModel

class WorkExperience(BaseModel):
    company: str
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    tech_stack: list[str] = []

class Education(BaseModel):
    school: str
    degree: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[str] = None

class ResumeParseResult(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = []
    work_experiences: list[WorkExperience] = []
    educations: list[Education] = []
    total_years_exp: Optional[float] = None
    raw_text: Optional[str] = None