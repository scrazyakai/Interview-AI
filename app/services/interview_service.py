import base64
import threading
from typing import Any
from uuid import UUID

import dashscope
from dashscope.audio.qwen_omni import (
    MultiModality,
    OmniRealtimeCallback,
    OmniRealtimeConversation,
)
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.config.interview_config import build_instructions
from app.core.config.config import settings
from app.core.exception import BizException, ErrorCode
from app.core.log import get_logger
from app.crud.session_history import get_session_history_pages
from app.db.session import AsyncSessionLocal
from app.models import InterviewSession
from app.realtime.realtime_service import _send_raw_event
from app.schemas import InterviewerInitRequest
from app.schemas.interview_session import SessionHistoryListResponse

import asyncio
import json

log = get_logger(__name__)


class _ChatCallback(OmniRealtimeCallback):
    """收集单次问答的文本和音频，完成后通知等待线程"""

    def __init__(self) -> None:
        self._done = threading.Event()
        self.audio_chunks: list[bytes] = []
        self.text: str = ""

    def on_event(self, response: dict) -> None:
        event_type = response.get("type", "")
        if event_type == "response.audio.delta":
            delta_b64 = response.get("delta", "")
            if delta_b64:
                try:
                    self.audio_chunks.append(base64.b64decode(delta_b64))
                except Exception:
                    pass
        elif event_type == "response.audio_transcript.done":
            self.text = response.get("transcript", "") or self.text
        elif event_type == "response.done":
            self._done.set()

    def on_close(self) -> None:
        self._done.set()

    def wait(self, timeout: float = 30.0) -> None:
        self._done.wait(timeout)


class InterviewService:
    async def chat(self, message: str) -> dict[str, Any]:
        dashscope.api_key = settings.QWEN_API_KEY

        callback = _ChatCallback()
        conv = OmniRealtimeConversation(
            model=settings.QWEN_REALTIME_MODEL,
            callback=callback,
            url=settings.QWEN_REALTIME_URL,
        )

        try:
            await asyncio.to_thread(conv.connect)

            conv.update_session(
                output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
                voice=settings.QWEN_REALTIME_VOICE,
                instructions=build_instructions(),
            )

            _send_raw_event(conv, {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": message}],
                },
            })
            _send_raw_event(conv, {"type": "response.create"})

            await asyncio.to_thread(callback.wait, 30.0)

            audio_bytes = b"".join(callback.audio_chunks)
            return {
                "reply": callback.text,
                "audio_base64": base64.b64encode(audio_bytes).decode() if audio_bytes else None,
                "audio_format": "pcm",
                "audio_sample_rate": 24000,
            }
        except BizException:
            raise
        except Exception as exc:
            log.exception("[exception] Realtime chat call failed")
            raise BizException(
                code=ErrorCode.REALTIME_SERVICE_ERROR,
                message="实时面试服务暂时不可用，请稍后再试",
            ) from exc
        finally:
            with __import__("contextlib").suppress(Exception):
                await asyncio.to_thread(conv.close)

    async def create_session(self, interview_init: InterviewerInitRequest, user_id: UUID) -> dict[str, Any]:
        interview_session = InterviewSession(
            user_id=user_id,
            job_title=interview_init.job_title,
            job_description=interview_init.job_description,
            resume_text=interview_init.resume_text,
            mode=interview_init.mode,
            experience_level=interview_init.experience_level,
            status="interviewing",
            started_at=func.now(),
        )
        async with AsyncSessionLocal() as session:
            try:
                session.add(interview_session)
                await session.commit()
                await session.refresh(interview_session)
                log.info(
                    "[biz] Interview session created: user_id=%s session_uuid=%s",
                    user_id, interview_session.session_uuid,
                )
                return {
                    "success": True,
                    "session_uuid": str(interview_session.session_uuid),
                }
            except IntegrityError as exc:
                raise BizException(
                    code=ErrorCode.INTERNAL_SERVER_ERROR,
                    message="创建面试会话失败",
                ) from exc
            except Exception as exc:
                raise BizException(
                    code=ErrorCode.INTERNAL_SERVER_ERROR,
                    message="创建面试会话失败",
                ) from exc

    async def get_session_history(
        self,
        user_id: UUID,
        offset: int,
        session_id: UUID,
        limit: int = 10,
    ) -> SessionHistoryListResponse:
        session_history_list, total = await get_session_history_pages(session_id, user_id, offset, limit)
        return SessionHistoryListResponse(list=session_history_list, total=total)


interview_service = InterviewService()
