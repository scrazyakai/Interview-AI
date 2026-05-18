import asyncio
import base64
import json
from contextlib import suppress
from uuid import UUID

import dashscope
from dashscope.audio.qwen_omni import (
    MultiModality,
    OmniRealtimeCallback,
    OmniRealtimeConversation,
)
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.config.interview_config import build_instructions
from app.core.config.config import settings
from app.core.log import get_logger
from app.db.session import AsyncSessionLocal
from app.models import InterviewMessage, InterviewSession
from app.models.interview_message import ROLE_CANDIDATE, ROLE_INTERVIEWER

log = get_logger(__name__)

_CLOSED = object()  # 队列哨兵，标志 SDK 连接已关闭

FIRST_RESPONSE_INSTRUCTIONS = "请立即开始面试，先向候选人打招呼，然后请他们做自我介绍。"


# ── SDK 回调桥 ────────────────────────────────────────────────

class _QwenBridgeCallback(OmniRealtimeCallback):
    """把 SDK 的同步 on_event 回调转发到 asyncio 队列"""

    def __init__(self, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue):
        self._loop = loop
        self._queue = queue

    def on_open(self) -> None:
        pass

    def on_event(self, response: dict) -> None:
        asyncio.run_coroutine_threadsafe(self._queue.put(response), self._loop)

    def on_close(self) -> None:
        asyncio.run_coroutine_threadsafe(self._queue.put(_CLOSED), self._loop)


# ── 消息追踪 ──────────────────────────────────────────────────

class _MessageTracker:
    def __init__(self, session_db_id: int) -> None:
        self.session_db_id = session_db_id
        self._sequence = 0
        self.round_no = 1
        self.last_interviewer_id: int | None = None

    def next_seq(self) -> int:
        self._sequence += 1
        return self._sequence

    def on_candidate_turn_done(self) -> None:
        self.round_no += 1
        self.last_interviewer_id = None


async def _persist_interview_message(
    tracker: _MessageTracker,
    role: str,
    content: str,
    *,
    parent_message_id: int | None = None,
) -> int | None:
    content = content.strip()
    if not content:
        return None

    async with AsyncSessionLocal() as db:
        try:
            msg = InterviewMessage(
                session_id=tracker.session_db_id,
                role=role,
                content=content,
                round_no=tracker.round_no,
                sequence_no=tracker.next_seq(),
                parent_message_id=parent_message_id,
            )
            db.add(msg)
            await db.flush()
            msg_id = msg.id
            await db.commit()
            log.info(
                "interview_message persisted role=%s session=%s round=%s len=%s",
                role, tracker.session_db_id, tracker.round_no, len(content),
            )
            return msg_id
        except Exception:
            with suppress(Exception):
                await db.rollback()
            log.exception("failed to persist interview_message role=%s", role)
            return None


# ── 上行事件转发 ──────────────────────────────────────────────

async def _forward_upstream_messages(
    queue: asyncio.Queue,
    client_ws: WebSocket,
    tracker: _MessageTracker,
) -> None:
    assistant_text_buffer: list[str] = []

    while True:
        event = await queue.get()

        if event is _CLOSED:
            log.info("Qwen SDK connection closed.")
            return

        event_type = event.get("type", "")

        if event_type == "response.audio.delta":
            delta_b64 = event.get("delta", "")
            if delta_b64:
                try:
                    await client_ws.send_bytes(base64.b64decode(delta_b64))
                except Exception:
                    log.warning("failed to decode audio delta")

        elif event_type in ("response.audio_transcript.delta", "response.text.delta"):
            text = event.get("delta", "")
            if text:
                assistant_text_buffer.append(text)
                await client_ws.send_json({"type": "assistant_text", "text": text})

        elif event_type == "response.audio_transcript.done":
            # 用完整 transcript 覆盖增量片段，更准确
            transcript = event.get("transcript", "")
            if transcript:
                assistant_text_buffer = [transcript]

        elif event_type == "response.done":
            if assistant_text_buffer:
                assistant_text = "".join(assistant_text_buffer).strip()
                if assistant_text:
                    msg_id = await _persist_interview_message(tracker, ROLE_INTERVIEWER, assistant_text)
                    tracker.last_interviewer_id = msg_id
                assistant_text_buffer.clear()
            await client_ws.send_json({"type": "assistant_done"})

        elif event_type == "conversation.item.input_audio_transcription.completed":
            text = event.get("transcript", "")
            if text:
                await client_ws.send_json({"type": "user_text", "text": text})
                await _persist_interview_message(
                    tracker, ROLE_CANDIDATE, text,
                    parent_message_id=tracker.last_interviewer_id,
                )
                tracker.on_candidate_turn_done()

        elif event_type == "input_audio_buffer.speech_started":
            await client_ws.send_json({"type": "user_speaking"})

        elif event_type == "input_audio_buffer.speech_stopped":
            await client_ws.send_json({"type": "user_done"})

        elif event_type == "error":
            log.error("Qwen realtime error: %s", event)
            await client_ws.send_json({"type": "error", "detail": str(event.get("message", event))})
            return

        else:
            log.debug("unhandled upstream event type=%s", event_type)


# ── 下行消息转发 ──────────────────────────────────────────────

async def _forward_client_messages(
    client_ws: WebSocket,
    conv: OmniRealtimeConversation,
) -> None:
    while True:
        message = await client_ws.receive()

        if message.get("type") == "websocket.disconnect":
            raise WebSocketDisconnect()

        audio_bytes = message.get("bytes")
        if audio_bytes:
            conv.append_audio(base64.b64encode(audio_bytes).decode("ascii"))
            continue

        text_data = message.get("text")
        if not text_data:
            continue

        data = json.loads(text_data)
        data_type = data.get("type")

        if data_type == "text":
            content = str(data.get("content", "")).strip()
            if content:
                # 发送文本输入，并触发响应
                _send_raw_event(conv, {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": content}],
                    },
                })
                _send_raw_event(conv, {"type": "response.create"})

        elif data_type == "stop":
            return


def _send_raw_event(conv: OmniRealtimeConversation, event: dict) -> None:
    """通过 SDK 的底层 WebSocket 发送原始事件（用于 SDK 未封装的方法）"""
    ws = getattr(conv, "_ws", None)
    if ws is None:
        log.warning("_send_raw_event: cannot access SDK websocket, event dropped: %s", event.get("type"))
        return
    try:
        ws.send(json.dumps(event))
    except Exception:
        log.exception("_send_raw_event failed for event type=%s", event.get("type"))


# ── Session 查询 ──────────────────────────────────────────────

async def _get_interview_session(user_id: UUID, session_uuid: UUID) -> InterviewSession:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(InterviewSession).where(
                InterviewSession.user_id == user_id,
                InterviewSession.session_uuid == session_uuid,
            )
        )
        interview = result.scalars().first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found")

    return interview


# ── 主服务 ────────────────────────────────────────────────────

class RealtimeService:
    async def bridge_websocket(self, client_ws: WebSocket, user_id: UUID, session_uuid: UUID) -> None:
        interview = await _get_interview_session(user_id, session_uuid)
        tracker = _MessageTracker(session_db_id=interview.id)

        dashscope.api_key = settings.QWEN_API_KEY
        instructions = await build_instructions(interview)

        loop = asyncio.get_event_loop()
        event_queue: asyncio.Queue = asyncio.Queue()
        callback = _QwenBridgeCallback(loop, event_queue)

        conv = OmniRealtimeConversation(
            model=settings.QWEN_REALTIME_MODEL,
            callback=callback,
            url=settings.QWEN_REALTIME_URL,
        )

        # connect() 是阻塞调用，放到线程池执行
        await asyncio.to_thread(conv.connect)

        conv.update_session(
            output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
            voice=settings.QWEN_REALTIME_VOICE,
            instructions=instructions,
        )

        await client_ws.send_json({
            "type": "ready",
            "sampleRate": 24000,
            "audioFormat": "pcm",
        })

        # 触发 AI 开场白
        _send_raw_event(conv, {
            "type": "response.create",
            "response": {"instructions": FIRST_RESPONSE_INSTRUCTIONS},
        })

        upstream_task = None
        client_task = None
        try:
            upstream_task = asyncio.create_task(
                _forward_upstream_messages(event_queue, client_ws, tracker)
            )
            client_task = asyncio.create_task(
                _forward_client_messages(client_ws, conv)
            )
            done, pending = await asyncio.wait(
                {upstream_task, client_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in done:
                task.result()
            for task in pending:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
        finally:
            with suppress(Exception):
                await asyncio.to_thread(conv.close)
            with suppress(Exception):
                await client_ws.close()


realtime_service = RealtimeService()
