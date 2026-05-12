from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, File

from app.common.dependencies import get_current_user_id
from app.core.exception import ApiResponse

from app.schemas.resume import ResumeParseResult, ResumeListItem, ResumeUpdateRequest, WorkExperience, WorkExperienceRequest, Education, EducationRequest, Project, ProjectRequest
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/api/resume", tags=["resume"])
resume_service = ResumeService()


@router.post("/parse", response_model=ApiResponse[int])
async def parse_resume(
    background_tasks: BackgroundTasks,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    file: UploadFile = File(...),
) -> ApiResponse[int]:
    pdf_bytes = await file.read()
    file_name = file.filename or "resume.pdf"
    resume_id = await resume_service.create_pending_resume(pdf_bytes, user_id, file_name)
    background_tasks.add_task(resume_service.parse_resume_background, resume_id, pdf_bytes)
    return ApiResponse.success(resume_id, message="上传成功，正在后台解析")


@router.get("/list", response_model=ApiResponse[list[ResumeListItem]])
async def list_resumes(user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[list[ResumeListItem]]:
    result = await resume_service.list_resumes(user_id)
    return ApiResponse.success(result)


@router.get("/result/{resume_id}", response_model=ApiResponse[ResumeParseResult])
async def get_parse_result(resume_id: int, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[ResumeParseResult]:
    result = await resume_service.get_result_by_id(resume_id, user_id)
    return ApiResponse.success(result)


@router.post("/{resume_id}/update", response_model=ApiResponse[bool])
async def update_resume(resume_id: int, data: ResumeUpdateRequest, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[bool]:
    result = await resume_service.update_resume(resume_id, user_id, data)
    return ApiResponse.success(result, message="更新成功")


@router.post("/{resume_id}/delete", response_model=ApiResponse[bool])
async def delete_resume(resume_id: int, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[bool]:
    result = await resume_service.delete_resume(resume_id, user_id)
    return ApiResponse.success(result, message="删除成功")


# ── 工作经历 ──────────────────────────────────────────────────
@router.post("/{resume_id}/work-experience/add", response_model=ApiResponse[WorkExperience])
async def add_work_experience(resume_id: int, data: WorkExperienceRequest, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[WorkExperience]:
    result = await resume_service.add_work_experience(resume_id, user_id, data)
    return ApiResponse.success(result, message="添加成功")

@router.post("/{resume_id}/work-experience/{exp_id}/update", response_model=ApiResponse[bool])
async def update_work_experience(resume_id: int, exp_id: int, data: WorkExperienceRequest, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[bool]:
    result = await resume_service.update_work_experience(resume_id, exp_id, user_id, data)
    return ApiResponse.success(result, message="更新成功")

@router.post("/{resume_id}/work-experience/{exp_id}/delete", response_model=ApiResponse[bool])
async def delete_work_experience(resume_id: int, exp_id: int, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[bool]:
    result = await resume_service.delete_work_experience(resume_id, exp_id, user_id)
    return ApiResponse.success(result, message="删除成功")


# ── 教育经历 ──────────────────────────────────────────────────
@router.post("/{resume_id}/education/add", response_model=ApiResponse[Education])
async def add_education(resume_id: int, data: EducationRequest, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[Education]:
    result = await resume_service.add_education(resume_id, user_id, data)
    return ApiResponse.success(result, message="添加成功")

@router.post("/{resume_id}/education/{edu_id}/update", response_model=ApiResponse[bool])
async def update_education(resume_id: int, edu_id: int, data: EducationRequest, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[bool]:
    result = await resume_service.update_education(resume_id, edu_id, user_id, data)
    return ApiResponse.success(result, message="更新成功")

@router.post("/{resume_id}/education/{edu_id}/delete", response_model=ApiResponse[bool])
async def delete_education(resume_id: int, edu_id: int, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[bool]:
    result = await resume_service.delete_education(resume_id, edu_id, user_id)
    return ApiResponse.success(result, message="删除成功")


# ── 项目经历 ──────────────────────────────────────────────────
@router.post("/{resume_id}/project/add", response_model=ApiResponse[Project])
async def add_project(resume_id: int, data: ProjectRequest, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[Project]:
    result = await resume_service.add_project(resume_id, user_id, data)
    return ApiResponse.success(result, message="添加成功")

@router.post("/{resume_id}/project/{project_id}/update", response_model=ApiResponse[bool])
async def update_project(resume_id: int, project_id: int, data: ProjectRequest, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[bool]:
    result = await resume_service.update_project(resume_id, project_id, user_id, data)
    return ApiResponse.success(result, message="更新成功")

@router.post("/{resume_id}/project/{project_id}/delete", response_model=ApiResponse[bool])
async def delete_project(resume_id: int, project_id: int, user_id: Annotated[UUID, Depends(get_current_user_id)]) -> ApiResponse[bool]:
    result = await resume_service.delete_project(resume_id, project_id, user_id)
    return ApiResponse.success(result, message="删除成功")
