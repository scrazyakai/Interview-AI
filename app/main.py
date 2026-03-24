from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

from app.api import auth, interview
from app.api import user


app = FastAPI()

# 注册路由
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(interview.router)

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True  # 携带token
)
