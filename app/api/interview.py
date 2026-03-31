from contextlib import suppress
import traceback
from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, status, \
    Query
from pymupdf import pymupdf

from app.common.dependencies import get_current_user_id, parse_user_id_from_token
from app.realtime.realtime_service import realtime_service
from app.schemas import InterviewResponse, InterviewSessionCreateResponse
from app.schemas.interview import InterviewerInitRequest
from app.schemas.interview_session import SessionHistoryListResponse
from app.services.interview_service import interview_service

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/chat")
async def chat(message: str = Body(..., embed=True)) -> InterviewResponse:
    try:
        cleaned_message = message.strip()
        if not cleaned_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="message cannot be empty",
            )

        response = await interview_service.chat(cleaned_message)
        return InterviewResponse(**response)
    except HTTPException:
        raise
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        ) from err
    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Doubao realtime chat failed: {err}",
        ) from err


@router.websocket("/ws")
async def interview_ws(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token", "").strip()
    session_uuid_raw = websocket.query_params.get("session_uuid", "").strip()

    if not token or not session_uuid_raw:
        await websocket.close(code=1008)
        return

    try:
        user_id = parse_user_id_from_token(token)
        session_uuid = UUID(session_uuid_raw)
        await websocket.accept()
        await realtime_service.bridge_websocket(websocket, user_id, session_uuid)
    except WebSocketDisconnect:
        return
    except HTTPException as err:
        traceback.print_exc()
        with suppress(Exception):
            await websocket.send_json(
                {
                    "type": "error",
                    "detail": err.detail,
                }
            )
        with suppress(Exception):
            await websocket.close(code=1008)
    except Exception as err:
        traceback.print_exc()
        with suppress(Exception):
            await websocket.send_json(
                {
                    "type": "error",
                    "detail": f"Failed to start realtime interview: {err}",
                }
            )
        with suppress(Exception):
            await websocket.close(code=1011)


@router.post("/create-session", response_model=InterviewSessionCreateResponse)
async def create_session(
    interview_init: InterviewerInitRequest,
    user_id: UUID = Depends(get_current_user_id),
) -> InterviewSessionCreateResponse:
    result = await interview_service.create_session(interview_init, user_id)
    return InterviewSessionCreateResponse(**result)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="File is empty")

    doc = pymupdf.open(stream=data, filetype="pdf")
    texts = []
    for page in doc:
        page_text = page.get_text().strip()
        if page_text:
            texts.append(page_text)
    return {"resume_text": "\n".join(texts)}
"""分页查会话消息"""
@router.get("/session/{session_id}", response_model=SessionHistoryListResponse)
async def get_session_history_pages(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> SessionHistoryListResponse:
    offset = (page - 1) * page_size
    return await interview_service.get_session_history(
        user_id=user_id,
        offset=offset,
        session_id=session_id,
        limit=page_size,
    )
