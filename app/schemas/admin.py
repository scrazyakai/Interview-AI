from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── 用户管理 ──────────────────────────────────────────────────

class AdminUserItem(BaseModel):
    user_id: UUID
    username: str
    role_type: int
    total_points: int
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    total: int
    items: list[AdminUserItem]


class UpdateUserRoleRequest(BaseModel):
    role_type: int = Field(..., ge=1, le=3, description="1=普通用户 2=VIP 3=管理员")


# ── 文档管理 ──────────────────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    doc_id: int
    doc_uuid: UUID
    title: str
    status: str


class DocumentItem(BaseModel):
    doc_id: int
    doc_uuid: UUID
    title: str
    file_name: str
    file_type: str
    category: str
    status: str
    chunk_count: int
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    total: int
    items: list[DocumentItem]


# ── 系统统计 ──────────────────────────────────────────────────

class AdminStatsResponse(BaseModel):
    total_users: int
    total_documents: int
    total_chunks: int
    indexed_documents: int
