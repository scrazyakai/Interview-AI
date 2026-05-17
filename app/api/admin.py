"""
管理员专属 API，所有接口通过 get_current_admin 验证 role_type == 3。

接口列表：
  用户管理
    GET  /admin/users                    分页查询用户列表
    PUT  /admin/users/{user_id}/role     修改用户角色

  文档管理
    POST /admin/documents/upload         上传文档（PDF/TXT），触发后台索引
    GET  /admin/documents                分页查询文档列表
    POST /admin/documents/{doc_id}/reindex  重新索引文档
    DELETE /admin/documents/{doc_id}     删除文档及其所有 chunk

  系统统计
    GET  /admin/stats                    返回用户数/文档数/chunk 数等汇总
"""

import pdfplumber
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_current_admin
from app.core.exception import BizException, ErrorCode
from app.core.exception.response import ApiResponse
from app.crud import rag_document as rag_crud
from app.db.session import get_session
from app.rag.index_construction import build_document_index
from app.services import admin_service
from app.schemas.admin import (
    AdminStatsResponse,
    AdminUserListResponse,
    DocumentItem,
    DocumentListResponse,
    DocumentUploadResponse,
    UpdateUserRoleRequest,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

ALLOWED_TYPES = {"application/pdf", "text/plain", "text/markdown"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ── 用户管理 ──────────────────────────────────────────────────

@router.get("/users", response_model=ApiResponse[AdminUserListResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_id: UUID = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    users, total = await admin_service.list_users(session, page=page, page_size=page_size)
    return ApiResponse.success(
        AdminUserListResponse(total=total, items=users),
        message="查询成功",
    )


@router.put("/users/{user_id}/role", response_model=ApiResponse[None])
async def update_user_role(
    user_id: UUID,
    body: UpdateUserRoleRequest,
    admin_id: UUID = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    await admin_service.update_user_role(session, user_id, body.role_type)
    await session.commit()
    return ApiResponse.success(message="角色更新成功")


# ── 文档管理 ──────────────────────────────────────────────────

@router.post("/documents/upload", response_model=ApiResponse[DocumentUploadResponse])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(..., max_length=255),
    category: str = Form("general"),
    admin_id: UUID = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise BizException(
            code=ErrorCode.BAD_REQUEST,
            message="仅支持 PDF / TXT / Markdown 格式",
        )

    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE:
        raise BizException(code=ErrorCode.BAD_REQUEST, message="文件不能超过 10 MB")

    # 提取纯文本，保留原始内容
    if content_type == "application/pdf":
        original_content = _extract_pdf_text(raw)
    else:
        original_content = raw.decode("utf-8", errors="replace")

    if not original_content.strip():
        raise BizException(code=ErrorCode.EMPTY_FILE, message="文档内容为空，无法索引")

    file_ext = (file.filename or "").rsplit(".", 1)[-1].lower() or "txt"
    doc = await rag_crud.create_document(
        session,
        title=title,
        original_content=original_content,
        file_name=file.filename or "upload",
        file_type=file_ext,
        category=category,
        created_by=admin_id,
    )
    await session.commit()
    await session.refresh(doc)

    # 异步触发分块 + 嵌入
    background_tasks.add_task(build_document_index, doc.id)

    return ApiResponse.success(
        DocumentUploadResponse(
            doc_id=doc.id,
            doc_uuid=doc.doc_uuid,
            title=doc.title,
            status=doc.status,
        ),
        message="上传成功，正在后台索引",
    )


@router.get("/documents", response_model=ApiResponse[DocumentListResponse])
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_id: UUID = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    offset = (page - 1) * page_size
    docs, total = await rag_crud.list_documents(session, offset=offset, limit=page_size)
    items = [
        DocumentItem(
            doc_id=d.id,
            doc_uuid=d.doc_uuid,
            title=d.title,
            file_name=d.file_name,
            file_type=d.file_type,
            category=d.category,
            status=d.status,
            chunk_count=d.chunk_count,
            created_by=d.created_by,
            created_at=d.created_at,
        )
        for d in docs
    ]
    return ApiResponse.success(DocumentListResponse(total=total, items=items))


@router.post("/documents/{doc_id}/reindex", response_model=ApiResponse[None])
async def reindex_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    admin_id: UUID = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    doc = await rag_crud.get_document_by_id(session, doc_id)
    if doc is None:
        raise BizException(code=ErrorCode.DOCUMENT_NOT_FOUND, message="文档不存在")
    await rag_crud.update_document_status(session, doc_id, "pending")
    await session.commit()
    background_tasks.add_task(build_document_index, doc_id)
    return ApiResponse.success(message="重新索引任务已提交")


@router.delete("/documents/{doc_id}", response_model=ApiResponse[None])
async def delete_document(
    doc_id: int,
    admin_id: UUID = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    deleted = await rag_crud.delete_document(session, doc_id)
    if not deleted:
        raise BizException(code=ErrorCode.DOCUMENT_NOT_FOUND, message="文档不存在")
    await session.commit()
    return ApiResponse.success(message="删除成功")


# ── 系统统计 ──────────────────────────────────────────────────

@router.get("/stats", response_model=ApiResponse[AdminStatsResponse])
async def get_stats(
    admin_id: UUID = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    stats = await admin_service.get_stats(session)
    return ApiResponse.success(stats)


# ── 内部工具 ──────────────────────────────────────────────────

def _extract_pdf_text(raw: bytes) -> str:
    import io
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n\n".join(text_parts)
