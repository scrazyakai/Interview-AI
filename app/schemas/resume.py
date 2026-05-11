from typing import Optional

from pydantic import BaseModel

class WorkExperience(BaseModel):
    company: str
    title: str
    start_date: Optional[str]       # "2022-03" 格式，可选
    end_date: Optional[str]         # None 表示至今
    description: Optional[str]      # 工作内容摘要
    tech_stack: list[str] = []      # 技术栈关键词
class Education(BaseModel):
    school: str
    degree: Optional[str]           # 本科 / 硕士 / 博士
    major: Optional[str]            # 专业
    graduation_year: Optional[str]  # 毕业年份
class ResumeParseResult(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    summary: Optional[str]          # 个人简介 / 求职意向
    skills: list[str] = []          # 技能标签列表
    work_experiences: list[WorkExperience] = []
    educations: list[Education] = []
    total_years_exp: Optional[float]    #  总工作年限
    raw_text: Optional[str]             # pdfplumber 原始文本（调试用）