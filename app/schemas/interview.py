from pydantic import BaseModel, Field


class InterviewRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message sent to the realtime interviewer")


class InterviewResponse(BaseModel):
    reply: str
    session_id: str
    audio_base64: str | None = None
    audio_format: str | None = None
    audio_sample_rate: int | None = None
