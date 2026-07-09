from typing import AsyncGenerator, Optional

from openai import OpenAI

from app.config import settings


client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)


def chat_stream(prompt: str, history: Optional[list[dict]] = None) -> AsyncGenerator[str, None]:
    """调用大模型API，返回SSE流式输出的生成器"""
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个智能文档助手。请基于提供的文档内容回答用户问题。"
                "如果文档中没有相关信息，请如实告知。"
            ),
        }
    ]

    if history:
        for msg in history[-6:]:
            messages.append({"role": "user", "content": msg.get("user", "")})
            messages.append({"role": "assistant", "content": msg.get("ai", "")})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        stream=True,
        timeout=120,
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def chat_sync(prompt: str) -> str:
    """同步调用，用于简单问答"""
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        timeout=60,
    )
    return response.choices[0].message.content or ""
