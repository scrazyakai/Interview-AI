from contextlib import suppress
import traceback

from fastapi import APIRouter, Body, HTTPException, WebSocket, WebSocketDisconnect, status

from app.schemas import InterviewResponse
from app.services.interview_service import interview_service

router = APIRouter(prefix="/api/interview", tags=["interview"])




@router.post("/chat")
async def chat(message: str = Body(..., embed=True),) -> InterviewResponse:
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
        await interview_service.bridge_websocket(websocket)
    except WebSocketDisconnect:
        return
    except Exception as err:
        traceback.print_exc()
        with suppress(Exception):
            await websocket.accept()
        with suppress(Exception):
            await websocket.send_json(
                {
                    "type": "error",
                    "detail": f"Failed to start realtime interview: {err}",
                }
            )
        with suppress(Exception):
            await websocket.close(code=1011)
