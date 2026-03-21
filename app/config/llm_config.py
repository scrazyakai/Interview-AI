import os
from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    """
    获取 LLM 实例

    Returns:
        ChatOpenAI: 配置好的 LLM 实例
    """
    return ChatOpenAI(
        api_key=os.getenv("VOLC_API_KEY"),
        base_url=os.getenv("VOLC_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
        model=os.getenv("VOLC_MODEL", "doubao-seed-1-8-251228")
    )


# 可以直接使用的实例
llm = get_llm()
