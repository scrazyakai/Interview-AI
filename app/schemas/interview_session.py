from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.models.session_history import MessageSourceEnum


class SessionHistoryResponse(BaseModel):
    message: str
    message_source: MessageSourceEnum
    created_at: datetime
class SessionHistoryListResponse(BaseModel):
    list: List[SessionHistoryResponse]
    total: int