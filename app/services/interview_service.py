import base64
import uuid
from typing import Any
from uuid import UUID

import websockets
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.config.interview_config import build_realtime_ws_config, build_start_session_payload
from app.core.exception import BizException, ErrorCode
from app.core.log import get_logger
from app.crud.session_history import get_session_history_pages
from app.db.session import AsyncSessionLocal
from app.models import InterviewSession
from app.realtime.realtime_service import _build_event_request, _parse_response
from app.schemas import InterviewerInitRequest
from app.schemas.interview_session import SessionHistoryListResponse

log = get_logger(__name__)


class InterviewService:
    async def chat(self, message: str) -> dict[str, Any]:
        session_id = str(uuid.uuid4())
        try:
            log.info(
                "[third_party] Starting realtime interview chat call: session_id=%s input_length=%s",
                session_id,
                len(message),
            )
            ws_config = build_realtime_ws_config()
            start_session_payload = await build_start_session_payload(input_mod="text")

            audio_chunks: list[bytes] = []
            text_fragments: list[str] = []

            async with websockets.connect(
                ws_config["base_url"],
                additional_headers=ws_config["headers"],
                ping_interval=None,
            ) as websocket:
                await websocket.send(_build_event_request(1, None, {}))
                _parse_response(await websocket.recv())

                await websocket.send(_build_event_request(100, session_id, start_session_payload))
                start_response = _parse_response(await websocket.recv())
                if start_response.get("message_type") == "SERVER_ERROR":
                    raise RuntimeError(f"Failed to start realtime session: {start_response}")

                await websocket.send(_build_event_request(501, session_id, {"content": message}))

                while True:
                    response = _parse_response(await websocket.recv())
                    message_type = response.get("message_type")

                    if message_type == "SERVER_ACK":
                        payload_msg = response.get("payload_msg")
                        if isinstance(payload_msg, (bytes, bytearray)):
                            audio_chunks.append(bytes(payload_msg))
                        continue

                    if message_type == "SERVER_ERROR":
                        raise RuntimeError(f"Doubao realtime request failed: {response}")

                    payload_msg = response.get("payload_msg")
                    event = response.get("event")
                    if event == 550 and isinstance(payload_msg, dict):
                        content = payload_msg.get("content")
                        if isinstance(content, str) and content:
                            text_fragments.append(content)

                    if event in {359, 152, 153}:
                        break

                await websocket.send(_build_event_request(102, session_id, {}))
                await websocket.send(_build_event_request(2, None, {}))

            reply = "".join(text_fragments).strip()
            audio_bytes = b"".join(audio_chunks)
            log.info(
                "[third_party] Completed realtime interview chat call: session_id=%s reply_length=%s audio_bytes=%s",
                session_id,
                len(reply),
                len(audio_bytes),
            )

            return {
                "reply": reply,
                "session_id": session_id,
                "audio_base64": base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None,
                "audio_format": "pcm",
                "audio_sample_rate": start_session_payload["tts"]["audio_config"]["sample_rate"] if audio_bytes else None,
            }
        except BizException:
            raise
        except Exception as exc:
            log.exception("[exception] Realtime interview chat call failed: session_id=%s", session_id)
            raise BizException(
                code=ErrorCode.REALTIME_SERVICE_ERROR,
                message="实时面试服务暂时不可用，请稍后再试",
                description="Realtime interview provider call failed while sending or receiving chat events.",
            ) from exc

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
                    "[biz] Interview session created successfully: user_id=%s session_uuid=%s",
                    user_id,
                    interview_session.session_uuid,
                )
                return {
                    "success": True,
                    "session_uuid": str(interview_session.session_uuid),
                }
            except IntegrityError as exc:
                log.exception("[exception] Interview session creation failed with integrity error.")
                raise BizException(
                    code=ErrorCode.INTERNAL_SERVER_ERROR,
                    message="创建面试会话失败",
                    description="Interview session creation failed due to a database integrity error.",
                ) from exc
            except Exception as exc:
                log.exception("[exception] Interview session creation failed with unexpected error.")
                raise BizException(
                    code=ErrorCode.INTERNAL_SERVER_ERROR,
                    message="创建面试会话失败",
                    description="Interview session creation failed due to an unexpected server error.",
                ) from exc

    async def get_session_history(
        self,
        user_id: UUID,
        offset: int,
        session_id: UUID,
        limit: int = 10,
    ) -> SessionHistoryListResponse:
        log.info(
            "[biz] Loading interview session history: user_id=%s session_id=%s offset=%s limit=%s",
            user_id,
            session_id,
            offset,
            limit,
        )
        session_history_list, total = await get_session_history_pages(session_id, user_id, offset, limit)
        return SessionHistoryListResponse(list=session_history_list, total=total)


interview_service = InterviewService()
