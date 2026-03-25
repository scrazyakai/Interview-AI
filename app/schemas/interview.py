from pydantic import BaseModel, Field


class InterviewRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message sent to the realtime interviewer")


class InterviewerInitRequest(BaseModel):
    job_title: str = Field(..., min_length=1, description="Job title used to initialize the interviewer")
    job_description: str = Field(..., min_length=1, description="Description used to initialize the interviewer")
    experience_level: str = Field(..., min_length=1, description="Experience level used to initialize the interviewer")
    resume_text: str = Field(..., description="Resume text used to initialize the interviewer")
    mode: str = Field(..., min_length=1, description="Interview mode used to initialize the interviewer")


class InterviewSessionCreateResponse(BaseModel):
    success: bool
    session_uuid: str


class InterviewResponse(BaseModel):
    reply: str
    session_id: str
    audio_base64: str | None = None
    audio_format: str | None = None
    audio_sample_rate: int | None = None
