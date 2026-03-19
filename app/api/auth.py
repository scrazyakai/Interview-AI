from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await auth_service.login(form_data)