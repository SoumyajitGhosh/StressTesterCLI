import asyncio
from openai import AsyncOpenAI, RateLimitError
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


async def review_batch(
    snippets: list[str],
    max_concurrent: int = 5,
) -> list[CodeReview | Exception]:
    
    sem = asyncio.Semaphore(max_concurrent)
    
    async def guarded(snippet):
        async with sem:
            max_retries = 3
            backoff = 1.0
            for attempt in range(max_retries + 1):
                try:
                    return await review_code(snippet)
                except RateLimitError as e:
                    if attempt == max_retries:
                        return e
                    await asyncio.sleep(backoff)
                    backoff *= 2
                except Exception as e:
                    return e  # surface errors, don't crash
            return RuntimeError("Unexpected retry loop exit")
            
    tasks = [guarded(s) for s in snippets]
    return await asyncio.gather(*tasks)
