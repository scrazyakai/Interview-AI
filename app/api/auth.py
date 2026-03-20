from fastapi import APIRouter, HTTPException
from starlette import status
from pydantic import BaseModel,Field

from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 创建用户
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32,pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(..., min_length=3, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=3, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

# 创建 AuthService 实例
auth_service = AuthService()

@router.post("/register", response_model=TokenResponse)
async def register_user(register_request: RegisterRequest):

    try:
        user = await auth_service.register_user(register_request.username, register_request.password)
        token = await auth_service.create_access_token(user)
        return TokenResponse(username=user.username, access_token=token)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/login", response_model=TokenResponse)
async def login_user(login_request: LoginRequest):
    try:
        user = await auth_service.authenticate(login_request.username, login_request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = await auth_service.create_access_token(user)
        return TokenResponse(username=user.username, access_token=token)
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
