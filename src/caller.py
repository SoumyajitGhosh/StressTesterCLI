import asyncio
from openai import AsyncOpenAI
from .models import CodeReview
from .config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM = """You are a code reviewer. Reply ONLY with a JSON object matching: {"verdict": "pass"|"warn"|"fail", "score": 0-100, "issues": ["list", "of", "strings"], "suggestions": "string"}"""

async def review_code(snippet: str) -> CodeReview:
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": snippet},
        ],
    )
    raw = resp.choices[0].message.content
    return CodeReview.model_validate_json(raw)