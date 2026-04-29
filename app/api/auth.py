from fastapi import APIRouter

from app.core.exception import ApiResponse, BizException, ErrorCode
from app.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])
auth_service = AuthService()


@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register_user(register_request: RegisterRequest) -> ApiResponse[TokenResponse]:
    user = await auth_service.register_user(
        register_request.username,
        register_request.password,
    )
    token = auth_service.create_access_token(user)
    return ApiResponse.success(data=TokenResponse(username=user.username, access_token=token))


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login_user(login_request: LoginRequest) -> ApiResponse[TokenResponse]:
    user = await auth_service.authenticate(
        login_request.username,
        login_request.password,
    )
    if not user:
        raise BizException(
            code=ErrorCode.INVALID_USERNAME_OR_PASSWORD,
            message="用户名或密码错误",
            description="User login failed because the username or password did not match.",
        )

    token = auth_service.create_access_token(user)
    return ApiResponse.success(data=TokenResponse(username=user.username, access_token=token))
