import asyncio
import gzip
import json
import logging
import uuid
from contextlib import suppress
from typing import Any
from uuid import UUID

import websockets
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.config.db_config import AsyncSessionLocal
from app.config.interview_config import build_realtime_ws_config, build_start_session_payload
from app.models import InterviewSession

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
logger = logging.getLogger(__name__)


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
    payload = raw[header_size * 4:]

    result: dict[str, Any] = {}
    start = 0
    payload_msg: bytes | None = None

    if message_type in {SERVER_FULL_RESPONSE, SERVER_ACK}:
        result["message_type"] = "SERVER_ACK" if message_type == SERVER_ACK else "SERVER_FULL_RESPONSE"
        if message_flags & 0b0010:
            result["seq"] = int.from_bytes(payload[:4], "big", signed=False)
            start += 4
        if message_flags & MSG_WITH_EVENT:
            result["event"] = int.from_bytes(payload[start: start + 4], "big", signed=False)
            start += 4

        payload = payload[start:]
        session_id_size = int.from_bytes(payload[:4], "big", signed=True)
        session_id = payload[4: 4 + session_id_size]
        result["session_id"] = session_id.decode("utf-8", errors="ignore")
        payload = payload[4 + session_id_size:]
        payload_size = int.from_bytes(payload[:4], "big", signed=False)
        payload_msg = payload[4: 4 + payload_size]
        result["payload_size"] = payload_size
    elif message_type == SERVER_ERROR_RESPONSE:
        result["message_type"] = "SERVER_ERROR"
        result["code"] = int.from_bytes(payload[:4], "big", signed=False)
        payload_size = int.from_bytes(payload[4:8], "big", signed=False)
        payload_msg = payload[8: 8 + payload_size]
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


"""提取文本"""


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

    # Official ASRResponse shape: {"results": [{"text": "...", "is_interim": true}]}
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
        "content",
        "text",
        "message",
        "transcript",
        "utterance",
        "value",
    )
    for key in preferred_keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    nested_keys = (
        "data",
        "result",
        "payload",
        "transcription",
        "asr",
        "recognition",
        "sentence",
        "delta",
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


async def _forward_upstream_messages(
        upstream_ws: websockets.ClientConnection,
        client_ws: WebSocket,
) -> None:
    saw_user_transcript = False
    while True:
        response = _parse_response(await upstream_ws.recv())
        message_type = response.get("message_type")
        event = response.get("event")
        payload_msg = response.get("payload_msg")

        if message_type == "SERVER_ERROR":
            logger.error("Doubao realtime upstream error: %s", _payload_preview(response))
            await client_ws.send_json(
                {
                    "type": "error",
                    "detail": f"Doubao realtime request failed: {response}",
                }
            )
            return

        if message_type == "SERVER_ACK" and event == 352 and isinstance(payload_msg, (bytes, bytearray)):
            await client_ws.send_bytes(bytes(payload_msg))
            continue

        if event is not None:
            logger.info(
                "Doubao upstream event=%s message_type=%s payload=%s transcript_candidate=%s",
                event,
                message_type,
                _payload_preview(payload_msg),
                _looks_like_user_transcript_payload(payload_msg),
            )

        if event == 550:
            content = _extract_text_from_payload(payload_msg)
            if content:
                await client_ws.send_json(
                    {
                        "type": "assistant_text",
                        "text": content,
                    }
                )
            continue

        if event == 451:
            content = _extract_text_from_payload(payload_msg)
            if content:
                saw_user_transcript = True
                await client_ws.send_json(
                    {
                        "type": "user_text_delta",
                        "text": content,
                    }
                )
            continue

        if event == 458:
            content = _extract_text_from_payload(payload_msg)
            if content:
                saw_user_transcript = True
                await client_ws.send_json(
                    {
                        "type": "user_text",
                        "text": content,
                    }
                )
            continue

        if event == 359:
            await client_ws.send_json({"type": "assistant_done"})
            continue

        if event == 450:
            await client_ws.send_json({"type": "user_speaking"})
            continue

        if event == 459:
            if not saw_user_transcript:
                logger.warning(
                    "Doubao user turn finished without transcript event. payload=%s",
                    _payload_preview(payload_msg),
                )
            await client_ws.send_json({"type": "user_done"})
            saw_user_transcript = False
            continue

        if _looks_like_user_transcript_payload(payload_msg):
            logger.warning(
                "Doubao upstream event=%s carried transcript-like payload but is not mapped yet. payload=%s",
                event,
                _payload_preview(payload_msg),
            )
            continue


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
        # 获取interview_session实体类
        interview = await _get_interview_session(user_id, session_uuid)
        # WebSocket连接使用的session_id
        session_id = str(uuid.uuid4())
        # WS连接详细信息
        ws_config = build_realtime_ws_config()
        # 建立连接池
        start_session_payload = await build_start_session_payload(interview, input_mod="audio")
        # 打开输入音频转写
        start_session_payload["input_audio_transcription"] = {
            "enabled": True
        }
        # 建立上游连接
        async with websockets.connect(
                ws_config["base_url"],
                additional_headers=ws_config["headers"],
                ping_interval=None,
        ) as upstream_ws:
            await upstream_ws.send(_build_event_request(1, None, {"content": start_session_payload}))
            # 解析结果
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
                upstream_task = asyncio.create_task(_forward_upstream_messages(upstream_ws, client_ws))
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
