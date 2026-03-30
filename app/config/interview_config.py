import os
import uuid
from pathlib import Path
from typing import Any

from app.models import InterviewSession

DEFAULT_REALTIME_URL = "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"
DEFAULT_RESOURCE_ID = "volc.speech.dialog"
DEFAULT_APP_KEY = "PlgvMymc7f3tQnJ6"
DEFAULT_SPEAKER = "zh_male_yunzhou_jupiter_bigtts"


def build_realtime_ws_config() -> dict[str, Any]:
    app_id = os.getenv("VOLC_REALTIME_APP_ID")
    access_key = os.getenv("VOLC_REALTIME_ACCESS_KEY")
    resource_id = os.getenv("VOLC_REALTIME_RESOURCE_ID", DEFAULT_RESOURCE_ID)
    app_key = os.getenv("VOLC_REALTIME_APP_KEY", DEFAULT_APP_KEY)
    base_url = os.getenv("VOLC_REALTIME_URL", DEFAULT_REALTIME_URL)

    if not app_id or not access_key:
        raise ValueError(
            "Missing Doubao realtime credentials. Set VOLC_REALTIME_APP_ID and VOLC_REALTIME_ACCESS_KEY."
        )

    return {
        "base_url": base_url,
        "headers": {
            "X-Api-App-ID": app_id,
            "X-Api-Access-Key": access_key,
            "X-Api-Resource-Id": resource_id,
            "X-Api-App-Key": app_key,
            "X-Api-Connect-Id": str(uuid.uuid4()),
        },
    }


async def build_start_session_payload(
    interview: InterviewSession | None = None,
    input_mod: str = "text",
) -> dict[str, Any]:
    role_prompt_path = os.getenv("VOLC_REALTIME_SYSTEM_ROLE")
    if not role_prompt_path:
        raise ValueError("Missing VOLC_REALTIME_SYSTEM_ROLE")

    system_role_template = Path(role_prompt_path).read_text(encoding="utf-8").strip()
    interview_data = {
        "job_function": getattr(interview, "job_function", "") or "",
        "job_title": getattr(interview, "job_title", "") or "",
        "job_description": getattr(interview, "job_description", "") or "",
        "experience_level": getattr(interview, "experience_level", "") or "",
        "mode": getattr(interview, "mode", "") or "",
        "resume_text": getattr(interview, "resume_text", "") or "",
    }
    system_role = system_role_template.format(**interview_data)

    return {
        "asr": {
            "audio_config": {
                "channel": 1,
                "format": os.getenv("VOLC_REALTIME_INPUT_FORMAT", "pcm"),
                "sample_rate": int(os.getenv("VOLC_REALTIME_INPUT_SAMPLE_RATE", "16000")),
            },
            "extra": {
                "enable_custom_vad" : True,
                "end_smooth_window_ms": int(os.getenv("VOLC_REALTIME_END_SMOOTH_WINDOW_MS", "1500")),
            },
        },
        "tts": {
            "speaker": os.getenv("VOLC_REALTIME_SPEAKER", DEFAULT_SPEAKER),
            "audio_config": {
                "channel": 1,
                "format": os.getenv("VOLC_REALTIME_OUTPUT_FORMAT", "pcm"),
                "sample_rate": int(os.getenv("VOLC_REALTIME_OUTPUT_SAMPLE_RATE", "24000")),
            },
        },
        "dialog": {
            "bot_name": os.getenv("VOLC_REALTIME_BOT_NAME", "豆生"),
            "system_role": system_role,
            "speaking_style": os.getenv("VOLC_REALTIME_SPEAKING_STYLE", "表达专业、清晰、语速适中。"),
            "extra": {
                "strict_audit": False,
                "recv_timeout": int(os.getenv("VOLC_REALTIME_RECV_TIMEOUT", "30")),
                "input_mod": input_mod,
            },
        },
    }
