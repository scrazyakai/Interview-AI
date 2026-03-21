from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import auth
from app.api import user


app = FastAPI()

# 注册路由
app.include_router(auth.router)
app.include_router(user.router)

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True  # 携带token
)