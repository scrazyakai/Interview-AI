from fastapi import APIRouter, Depends
from app.config.llm_config import get_llm, llm

router = APIRouter(prefix="/api/interview", tags=["interview"])





@router.post("/chat")
async def chat(message: str):
    res = llm.invoke("你好，你叫什么名字")
    return res