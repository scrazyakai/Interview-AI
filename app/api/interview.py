from contextlib import suppress
import traceback
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, Query, UploadFile, WebSocket, WebSocketDisconnect
from pymupdf import pymupdf

from app.common.dependencies import get_current_user_id, parse_user_id_from_token
from app.core.exception import ApiResponse, BizException, ErrorCode
from app.realtime.realtime_service import realtime_service
from app.schemas import InterviewResponse, InterviewSessionCreateResponse
from app.schemas.interview import InterviewerInitRequest
from app.schemas.interview_session import SessionHistoryListResponse
from app.services.interview_service import interview_service

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/chat", response_model=ApiResponse[InterviewResponse])
async def chat(message: str = Body(..., embed=True)) -> ApiResponse[InterviewResponse]:
    cleaned_message = message.strip()
    if not cleaned_message:
        raise BizException(
            code=ErrorCode.EMPTY_MESSAGE,
            message="message cannot be empty",
            description="The chat endpoint received a blank message after trimming whitespace.",
        )

    response = await interview_service.chat(cleaned_message)
    return ApiResponse.success(data=InterviewResponse(**response))


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
    except Exception as err:
        traceback.print_exc()
        detail = getattr(err, "message", f"Failed to start realtime interview: {err}")
        with suppress(Exception):
            await websocket.send_json(
                {
                    "type": "error",
                    "detail": detail,
                }
            )
        with suppress(Exception):
            await websocket.close(code=1011)


@router.post("/create-session", response_model=ApiResponse[InterviewSessionCreateResponse])
async def create_session(
    interview_init: InterviewerInitRequest,
    user_id: UUID = Depends(get_current_user_id),
) -> ApiResponse[InterviewSessionCreateResponse]:
    result = await interview_service.create_session(interview_init, user_id)
    return ApiResponse.success(data=InterviewSessionCreateResponse(**result))


@router.post("/upload", response_model=ApiResponse[dict[str, str]])
async def upload_resume(
    file: UploadFile = File(...),
    _: UUID = Depends(get_current_user_id),
) -> ApiResponse[dict[str, str]]:
    data = await file.read()
    if not data:
        raise BizException(
            code=ErrorCode.EMPTY_FILE,
            message="File is empty",
            description="The resume upload endpoint received an empty file payload.",
        )

    doc = pymupdf.open(stream=data, filetype="pdf")
    texts = []
    for page in doc:
        page_text = page.get_text().strip()
        if page_text:
            texts.append(page_text)
    return ApiResponse.success(data={"resume_text": "\n".join(texts)})


@router.get("/session/{session_id}", response_model=ApiResponse[SessionHistoryListResponse])
async def get_session_history_pages(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> ApiResponse[SessionHistoryListResponse]:
    offset = (page - 1) * page_size
    result = await interview_service.get_session_history(
        user_id=user_id,
        offset=offset,
        session_id=session_id,
        limit=page_size,
    )
    return ApiResponse.success(data=result)
