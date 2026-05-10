import asyncio
import gzip
import json
import uuid
from contextlib import suppress
from typing import Any
from uuid import UUID

import websockets
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.config.interview_config import build_realtime_ws_config, build_start_session_payload
from app.core.log import get_logger
from app.models import InterviewMessage, InterviewSession
from app.models.interview_message import ROLE_CANDIDATE, ROLE_INTERVIEWER

PROTOCOL_VERSION = 0b0001
CLIENT_FULL_REQUEST = 0b0001
CLIENT_AUDIO_ONLY_REQUEST = 0b0010
SERVER_FULL_RESPONSE = 0b1001
SERVER_ACK = 0b1011
SERVER_ERROR_RESPONSE = 0b1111
MSG_WITH_EVENT = 0b0100
JSON_SERIALIZATION = 0b0001
NO_SERIALIZATION = 0b0000
GZIP_COMPRESSION = 0b0001
FIRST_RESPONSE_CONTENT = "你好，先做下自我介绍吧。"
log = get_logger(__name__)

USER_TRANSCRIPT_RESULT_TYPES = {
    "conversation.item.input_audio_transcription.result",
}
USER_TRANSCRIPT_COMPLETED_TYPES = {
    "conversation.item.input_audio_transcription.completed",
}
ASSISTANT_TEXT_DELTA_TYPES = {
    "response.text.delta",
    "response.output_text.delta",
    "response.audio_transcript.delta",
}
ASSISTANT_DONE_TYPES = {
    "response.done",
    "response.output_text.done",
    "response.text.done",
}
USER_SPEAKING_TYPES = {
    "input_audio_buffer.speech_started",
}
USER_DONE_TYPES = {
    "input_audio_buffer.speech_stopped",
}


def _generate_header(
    message_type: int = CLIENT_FULL_REQUEST,
    message_type_specific_flags: int = MSG_WITH_EVENT,
    serial_method: int = JSON_SERIALIZATION,
    compression_type: int = GZIP_COMPRESSION,
) -> bytearray:
    header = bytearray()
    header.append((PROTOCOL_VERSION << 4) | 0b0001)
    header.append((message_type << 4) | message_type_specific_flags)
    header.append((serial_method << 4) | compression_type)
    header.append(0x00)
    return header


def _build_event_request(
    event: int,
    session_id: str | None,
    payload: dict[str, Any],
    *,
    message_type: int = CLIENT_FULL_REQUEST,
    serial_method: int = JSON_SERIALIZATION,
) -> bytes:
    message = bytearray(
        _generate_header(
            message_type=message_type,
            serial_method=serial_method,
        )
    )
    message.extend(int(event).to_bytes(4, "big"))

    if session_id is not None:
        session_id_bytes = session_id.encode("utf-8")
        message.extend(len(session_id_bytes).to_bytes(4, "big"))
        message.extend(session_id_bytes)

    if serial_method == NO_SERIALIZATION:
        payload_bytes = gzip.compress(payload.get("audio", b""))
    else:
        payload_bytes = gzip.compress(json.dumps(payload).encode("utf-8"))

    message.extend(len(payload_bytes).to_bytes(4, "big"))
    message.extend(payload_bytes)
    return bytes(message)


def _build_audio_request(session_id: str, audio: bytes) -> bytes:
    return _build_event_request(
        200,
        session_id,
        {"audio": audio},
        message_type=CLIENT_AUDIO_ONLY_REQUEST,
        serial_method=NO_SERIALIZATION,
    )


def _parse_response(raw: Any) -> dict[str, Any]:
    if isinstance(raw, str):
        return {}

    header_size = raw[0] & 0x0F
    message_type = raw[1] >> 4
    message_flags = raw[1] & 0x0F
    serialization_method = raw[2] >> 4
    compression_method = raw[2] & 0x0F
    payload = raw[header_size * 4 :]

    result: dict[str, Any] = {}
    start = 0
    payload_msg: bytes | None = None

    if message_type in {SERVER_FULL_RESPONSE, SERVER_ACK}:
        result["message_type"] = "SERVER_ACK" if message_type == SERVER_ACK else "SERVER_FULL_RESPONSE"
        if message_flags & 0b0010:
            result["seq"] = int.from_bytes(payload[:4], "big", signed=False)
            start += 4
        if message_flags & MSG_WITH_EVENT:
            result["event"] = int.from_bytes(payload[start : start + 4], "big", signed=False)
            start += 4

        payload = payload[start:]
        session_id_size = int.from_bytes(payload[:4], "big", signed=True)
        session_id = payload[4 : 4 + session_id_size]
        result["session_id"] = session_id.decode("utf-8", errors="ignore")
        payload = payload[4 + session_id_size :]
        payload_size = int.from_bytes(payload[:4], "big", signed=False)
        payload_msg = payload[4 : 4 + payload_size]
        result["payload_size"] = payload_size
    elif message_type == SERVER_ERROR_RESPONSE:
        result["message_type"] = "SERVER_ERROR"
        result["code"] = int.from_bytes(payload[:4], "big", signed=False)
        payload_size = int.from_bytes(payload[4:8], "big", signed=False)
        payload_msg = payload[8 : 8 + payload_size]
        result["payload_size"] = payload_size
    else:
        return result

    if payload_msg is None:
        return result

    if compression_method == GZIP_COMPRESSION:
        payload_msg = gzip.decompress(payload_msg)

    if serialization_method == JSON_SERIALIZATION:
        result["payload_msg"] = json.loads(payload_msg.decode("utf-8"))
    else:
        result["payload_msg"] = payload_msg

    return result


def _extract_text_from_payload(payload: Any) -> str | None:
    if isinstance(payload, str):
        value = payload.strip()
        return value or None

    if isinstance(payload, list):
        fragments = [fragment for item in payload if (fragment := _extract_text_from_payload(item))]
        if fragments:
            return "".join(fragments).strip() or None
        return None

    if not isinstance(payload, dict):
        return None

    results = payload.get("results")
    if isinstance(results, list):
        fragments: list[str] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            value = item.get("text")
            if isinstance(value, str) and value.strip():
                fragments.append(value.strip())
        if fragments:
            return "".join(fragments).strip() or None

    preferred_keys = (
        "delta",
        "content",
        "text",
        "message",
        "transcript",
        "utterance",
        "value",
    )
    for key in preferred_keys:
        value = payload.get(key)
        text_value = _extract_text_from_payload(value)
        if text_value:
            return text_value

    nested_keys = (
        "data",
        "result",
        "payload",
        "transcription",
        "asr",
        "recognition",
        "sentence",
        "item",
        "response",
    )
    for key in nested_keys:
        nested = payload.get(key)
        text_value = _extract_text_from_payload(nested)
        if text_value:
            return text_value

    return None


def _payload_preview(payload: Any, limit: int = 400) -> str:
    try:
        preview = json.dumps(payload, ensure_ascii=False)
    except TypeError:
        preview = repr(payload)
    if len(preview) > limit:
        return f"{preview[:limit]}..."
    return preview


def _looks_like_user_transcript_payload(payload: Any) -> bool:
    return _extract_text_from_payload(payload) is not None


def _normalize_json_upstream_event(raw_text: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "normalized_type": "unknown",
            "upstream_type": None,
            "text": None,
            "is_final": False,
            "is_legacy": False,
            "message_type": None,
            "event": None,
            "payload": raw_text,
        }

    if not isinstance(payload, dict):
        return {
            "normalized_type": "unknown",
            "upstream_type": None,
            "text": None,
            "is_final": False,
            "is_legacy": False,
            "message_type": None,
            "event": None,
            "payload": payload,
        }

    upstream_type = payload.get("type")
    text = _extract_text_from_payload(payload)

    normalized_type = "unknown"
    is_final = False

    if upstream_type in USER_TRANSCRIPT_RESULT_TYPES:
        normalized_type = "user_transcript_delta"
    elif upstream_type in USER_TRANSCRIPT_COMPLETED_TYPES:
        normalized_type = "user_transcript_final"
        is_final = True
    elif upstream_type in ASSISTANT_TEXT_DELTA_TYPES:
        normalized_type = "assistant_text_delta"
    elif upstream_type in ASSISTANT_DONE_TYPES:
        normalized_type = "assistant_done"
        is_final = True
    elif upstream_type in USER_SPEAKING_TYPES:
        normalized_type = "user_speaking"
    elif upstream_type in USER_DONE_TYPES:
        normalized_type = "user_done"

    return {
        "normalized_type": normalized_type,
        "upstream_type": upstream_type,
        "text": text,
        "is_final": is_final,
        "is_legacy": False,
        "message_type": None,
        "event": None,
        "payload": payload,
    }


def _normalize_legacy_upstream_event(raw: Any) -> dict[str, Any]:
    response = _parse_response(raw)
    message_type = response.get("message_type")
    event = response.get("event")
    payload = response.get("payload_msg")

    normalized_type = "unknown"
    is_final = False
    text = _extract_text_from_payload(payload)

    if message_type == "SERVER_ERROR":
        normalized_type = "error"
    elif message_type == "SERVER_ACK" and event == 352 and isinstance(payload, (bytes, bytearray)):
        normalized_type = "assistant_audio"
    elif event == 550:
        normalized_type = "assistant_text_delta"
    elif event == 451:
        normalized_type = "user_transcript_delta"
    elif event == 458:
        normalized_type = "user_transcript_final"
        is_final = True
    elif event == 359:
        normalized_type = "assistant_done"
        is_final = True
    elif event == 450:
        normalized_type = "user_speaking"
    elif event == 459:
        normalized_type = "user_done"

    return {
        "normalized_type": normalized_type,
        "upstream_type": None,
        "text": text,
        "is_final": is_final,
        "is_legacy": True,
        "message_type": message_type,
        "event": event,
        "payload": payload,
        "response": response,
    }


def _normalize_upstream_event(raw: Any) -> dict[str, Any]:
    if isinstance(raw, str):
        return _normalize_json_upstream_event(raw)
    return _normalize_legacy_upstream_event(raw)


def _merge_transcript_fragments(fragments: list[str]) -> str:
    cleaned = [item.strip() for item in fragments if item and item.strip()]
    if not cleaned:
        return ""

    merged = cleaned[0]
    for piece in cleaned[1:]:
        if piece.startswith(merged):
            merged = piece
        elif merged.startswith(piece):
            continue
        else:
            merged = f"{merged}{piece}"
    return merged.strip()


class _MessageTracker:
    """每场面试的消息序号和轮次状态，非线程安全，仅在单个 websocket 协程中使用。"""

    def __init__(self, session_db_id: int) -> None:
        self.session_db_id = session_db_id
        self._sequence = 0
        self.round_no = 1
        # 当前轮次面试官消息的 db id，candidate 回答时作为 parent_message_id
        self.last_interviewer_id: int | None = None

    def next_seq(self) -> int:
        self._sequence += 1
        return self._sequence

    def on_candidate_turn_done(self) -> None:
        """candidate 回答落库后调用，准备进入下一轮。"""
        self.round_no += 1
        self.last_interviewer_id = None


async def _persist_interview_message(
    tracker: _MessageTracker,
    role: str,
    content: str,
    *,
    parent_message_id: int | None = None,
) -> int | None:
    """写入 interview_messages，返回插入行的 id；失败返回 None，不中断对话。"""
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
                "interview_message persisted role=%s session_db_id=%s round=%s seq=%s len=%s",
                role,
                tracker.session_db_id,
                tracker.round_no,
                msg.sequence_no,
                len(content),
            )
            return msg_id
        except Exception:
            with suppress(Exception):
                await db.rollback()
            log.exception(
                "failed to persist interview_message role=%s session_db_id=%s",
                role,
                tracker.session_db_id,
            )
            return None


async def _forward_upstream_messages(
    upstream_ws: websockets.ClientConnection,
    client_ws: WebSocket,
    tracker: _MessageTracker,
) -> None:
    saw_user_transcript = False
    assistant_text_buffer: list[str] = []
    user_text_buffer: list[str] = []
    user_turn_persisted = False

    while True:
        try:
            raw = await upstream_ws.recv()
        except websockets.exceptions.ConnectionClosedOK:
            log.info("upstream websocket closed normally.")
            return
        except websockets.exceptions.ConnectionClosedError:
            log.warning("upstream websocket closed with error.")
            return
        normalized = _normalize_upstream_event(raw)

        normalized_type = normalized["normalized_type"]
        upstream_type = normalized.get("upstream_type")
        text = normalized.get("text")
        message_type = normalized.get("message_type")
        event = normalized.get("event")
        payload = normalized.get("payload")
        is_legacy = normalized.get("is_legacy", False)

        log.info(
            "upstream normalized_type=%s upstream_type=%s legacy=%s event=%s message_type=%s text_len=%s payload=%s",
            normalized_type,
            upstream_type,
            is_legacy,
            event,
            message_type,
            len(text or ""),
            _payload_preview(payload),
        )

        if normalized_type == "error":
            response = normalized.get("response", {})
            log.error("Doubao realtime upstream error: %s", _payload_preview(response))
            await client_ws.send_json(
                {
                    "type": "error",
                    "detail": f"Doubao realtime request failed: {response}",
                }
            )
            return

        if normalized_type == "assistant_audio" and isinstance(payload, (bytes, bytearray)):
            await client_ws.send_bytes(bytes(payload))
            continue

        if normalized_type == "assistant_text_delta":
            if text:
                assistant_text_buffer.append(text)
                await client_ws.send_json({"type": "assistant_text", "text": text})
            continue

        if normalized_type == "user_transcript_delta":
            if text:
                saw_user_transcript = True
                user_text_buffer.append(text)
                await client_ws.send_json({"type": "user_text_delta", "text": text})
            continue

        if normalized_type == "user_transcript_final":
            if text:
                saw_user_transcript = True
                user_text_buffer = [text]
                await client_ws.send_json({"type": "user_text", "text": text})
                await _persist_interview_message(
                    tracker,
                    ROLE_CANDIDATE,
                    text,
                    parent_message_id=tracker.last_interviewer_id,
                )
                tracker.on_candidate_turn_done()
                user_turn_persisted = True
            continue

        if normalized_type == "assistant_done":
            if assistant_text_buffer:
                assistant_text = "".join(assistant_text_buffer).strip()
                if assistant_text:
                    msg_id = await _persist_interview_message(tracker, ROLE_INTERVIEWER, assistant_text)
                    tracker.last_interviewer_id = msg_id
                assistant_text_buffer.clear()
            await client_ws.send_json({"type": "assistant_done"})
            continue

        if normalized_type == "user_speaking":
            await client_ws.send_json({"type": "user_speaking"})
            continue

        if normalized_type == "user_done":
            if not user_turn_persisted:
                fallback_user_text = _merge_transcript_fragments(user_text_buffer)
                if fallback_user_text:
                    await _persist_interview_message(
                        tracker,
                        ROLE_CANDIDATE,
                        fallback_user_text,
                        parent_message_id=tracker.last_interviewer_id,
                    )
                    tracker.on_candidate_turn_done()
                    log.info(
                        "persisted candidate transcript on user_done fallback session_db_id=%s len=%s",
                        tracker.session_db_id,
                        len(fallback_user_text),
                    )
            if not saw_user_transcript:
                log.warning(
                    "upstream user turn finished without transcript. payload=%s",
                    _payload_preview(payload),
                )
            await client_ws.send_json({"type": "user_done"})
            saw_user_transcript = False
            user_turn_persisted = False
            user_text_buffer.clear()
            continue

        if is_legacy and event is not None:
            log.warning(
                "legacy numeric event fallback in use event=%s payload=%s",
                event,
                _payload_preview(payload),
            )
            continue

        if _looks_like_user_transcript_payload(payload):
            log.warning(
                "unmapped transcript-like upstream event type=%s payload=%s",
                upstream_type,
                _payload_preview(payload),
            )
            continue

        log.warning(
            "unknown upstream event type=%s event=%s payload=%s",
            upstream_type,
            event,
            _payload_preview(payload),
        )


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


class RealtimeService:
    async def bridge_websocket(self, client_ws: WebSocket, user_id: UUID, session_uuid: UUID) -> None:
        interview = await _get_interview_session(user_id, session_uuid)
        tracker = _MessageTracker(session_db_id=interview.id)

        session_id = str(uuid.uuid4())
        ws_config = build_realtime_ws_config()
        start_session_payload = await build_start_session_payload(interview, input_mod="audio")
        start_session_payload["input_audio_transcription"] = {"enabled": True}

        async with websockets.connect(
            ws_config["base_url"],
            additional_headers=ws_config["headers"],
            ping_interval=None,
        ) as upstream_ws:
            await upstream_ws.send(_build_event_request(1, None, {"content": start_session_payload}))
            _parse_response(await upstream_ws.recv())

            await upstream_ws.send(_build_event_request(100, session_id, start_session_payload))
            start_response = _parse_response(await upstream_ws.recv())
            if start_response.get("message_type") == "SERVER_ERROR":
                raise RuntimeError(f"Failed to start realtime session: {start_response}")

            await client_ws.send_json(
                {
                    "type": "ready",
                    "sessionId": session_id,
                    "sampleRate": start_session_payload["tts"]["audio_config"]["sample_rate"],
                    "audioFormat": start_session_payload["tts"]["audio_config"]["format"],
                }
            )
            await upstream_ws.send(_build_event_request(300, session_id, {"content": FIRST_RESPONSE_CONTENT}))

            upstream_task = None
            client_task = None
            try:
                upstream_task = asyncio.create_task(
                    _forward_upstream_messages(upstream_ws, client_ws, tracker)
                )
                client_task = asyncio.create_task(self._forward_client_messages(client_ws, upstream_ws, session_id))
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
                    await upstream_ws.send(_build_event_request(102, session_id, {}))
                with suppress(Exception):
                    await upstream_ws.send(_build_event_request(2, None, {}))
                with suppress(Exception):
                    await client_ws.close()

    async def _forward_client_messages(
        self,
        client_ws: WebSocket,
        upstream_ws: websockets.ClientConnection,
        session_id: str,
    ) -> None:
        while True:
            message = await client_ws.receive()
            message_type = message.get("type")

            if message_type == "websocket.disconnect":
                raise WebSocketDisconnect()

            audio_bytes = message.get("bytes")
            if audio_bytes:
                await upstream_ws.send(_build_audio_request(session_id, audio_bytes))
                continue

            text_data = message.get("text")
            if not text_data:
                continue

            data = json.loads(text_data)
            data_type = data.get("type")
            if data_type == "text":
                content = str(data.get("content", "")).strip()
                if content:
                    await upstream_ws.send(_build_event_request(501, session_id, {"content": content}))
            elif data_type == "stop":
                return


realtime_service = RealtimeService()

