import os
from langchain_openai import ChatOpenAI

from app.core.config.config import settings


def get_llm() -> ChatOpenAI:
    """
    获取 LLM 实例

    Returns:
        ChatOpenAI: 配置好的 LLM 实例
    """
    return ChatOpenAI(
        api_key=settings.VOLC_API_KEY, #API_KEY
        base_url=settings.VOLC_BASE_URL,
        model=settings.VOLC_MODEL
    )


# 可以直接使用的实例
llm = get_llm()
