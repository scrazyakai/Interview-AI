from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, UploadFile, File

from app.common.dependencies import get_current_user_id
from app.core.exception import ApiResponse
from app.crud import resume

from app.schemas.resume import ResumeParseResult
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/api/resume", tags=["resume"])
resume_service = ResumeService()
@router.post("/parse", response_model=ApiResponse[ResumeParseResult])
async def parse_resume(user_id: Annotated[UUID,get_current_user_id],file: UploadFile = File(...)) -> ApiResponse[ResumeParseResult]:
    """读取pdf"""
    pdf_bytes = await file.read()
    """解析pdf"""
    await resume_service.parse_resume(pdf_bytes,user_id)

    return ApiResponse.success()
