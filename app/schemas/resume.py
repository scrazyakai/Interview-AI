from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class WorkExperience(BaseModel):
    id: Optional[int] = None
    company: str
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    tech_stack: list[str] = []
    resume_id: Optional[int] = None
    sort_order: Optional[int] = None


class WorkExperienceRequest(BaseModel):
    company: str
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    tech_stack: list[str] = []

class Project(BaseModel):
    id: Optional[int] = None
    name: str
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    tech_stack: list[str] = []
    resume_id: Optional[int] = None
    sort_order: Optional[int] = None


class ProjectRequest(BaseModel):
    name: str
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    tech_stack: list[str] = []

class Education(BaseModel):
    id: Optional[int] = None
    school: str
    degree: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[str] = None


class EducationRequest(BaseModel):
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
    projects: list[Project] = []
    educations: list[Education] = []
    total_years_exp: Optional[float] = None
    raw_text: Optional[str] = None


class ResumeListItem(BaseModel):
    id: int
    resume_uuid: UUID
    file_name: str
    parse_status: str
    name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[list[str]] = None
    total_years_exp: Optional[float] = None