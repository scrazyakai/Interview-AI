from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.params import Depends
import app.models  # 确保所有模型注册到 SQLAlchemy metadata
from app.api import resume
from starlette.middleware.cors import CORSMiddleware

from app.common.dependencies import get_current_user_id
from app.core.log import AccessLogMiddleware, configure_logging

load_dotenv()
configure_logging()

from app.api import auth, interview
from app.api.interview import ws_router as interview_ws_router
from app.api import user
from app.api import admin
from app.core.exception import register_exception_handlers


app = FastAPI()
register_exception_handlers(app)

app.include_router(auth.router)

app.include_router(resume.router, dependencies=[Depends(get_current_user_id)])
app.include_router(user.router, dependencies=[Depends(get_current_user_id)])
app.include_router(interview.router, dependencies=[Depends(get_current_user_id)])
app.include_router(interview_ws_router)  # WebSocket 不走 HTTPBearer，自行校验 token
# admin 路由内部通过 get_current_admin 自行校验权限，不在此处添加全局依赖
app.include_router(admin.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(AccessLogMiddleware)
