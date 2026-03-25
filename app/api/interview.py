from contextlib import suppress
import traceback
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, WebSocket, WebSocketDisconnect, status, Depends, UploadFile, File
from pymupdf import pymupdf

from app.common.dependencies import get_current_user_id
from app.schemas import InterviewResponse
from app.schemas.interview import InterviewerInitRequest
from app.services.interview_service import interview_service

router = APIRouter(prefix="/api/interview", tags=["interview"])




@router.post("/chat")
async def chat(message: str = Body(..., embed=True),) -> InterviewResponse:
    try:
        cleaned_message = message.strip() # 去掉空格
        if not cleaned_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="message cannot be empty",
            )

        response = await interview_service.chat(cleaned_message) # 对话
        return InterviewResponse(**response)
    except HTTPException:
        raise
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        )
    except Exception as err:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Doubao realtime chat failed: {err}",
        )


@router.websocket("/ws")
async def interview_ws(websocket: WebSocket) -> None:
    try:
        await interview_service.bridge_websocket(websocket) #建立WS连接
    except WebSocketDisconnect:
        return
    except Exception as err:
        traceback.print_exc()
        with suppress(Exception):
            await websocket.accept() #不往外抛出异常
        with suppress(Exception):
            await websocket.send_json(
                {
                    "type": "error",
                    "detail": f"Failed to start realtime interview: {err}",
                }
            )
        with suppress(Exception):
            await websocket.close(code=1011)
@router.post("/create-session")
async def create_session(interview_init: InterviewerInitRequest,user_id: UUID = Depends(get_current_user_id)) -> bool:
    result =  await interview_service.create_session(interview_init,user_id)
    return result
@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    data = await file.read()
    # 判断是否为空
    if not data:
        raise HTTPException(status_code=400,detail="File is empty")
    doc = pymupdf.open(stream=data,filetype="pdf")
    texts = []
    for page in doc:
        page_text = page.get_text().strip()
        if page_text:
            texts.append(page_text)
    return {"resume_text": "\n".join(texts)}