from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.log import AccessLogMiddleware, configure_logging

load_dotenv()
configure_logging()

from app.api import auth, interview
from app.api import user
from app.core.exception import register_exception_handlers


app = FastAPI()
register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(interview.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_middleware(AccessLogMiddleware)
