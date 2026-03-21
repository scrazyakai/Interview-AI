from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/interview", tags=["interview"])





@router.post("/chat")
async def chat(message: str):
    pass