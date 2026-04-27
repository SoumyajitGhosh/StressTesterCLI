import asyncio
import json
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .caller import review_batch, review_code
from .models import CodeReview

router = APIRouter()


class BatchRequest(BaseModel):
    snippets: list[str]
    max_concurrent: int = 5


class BatchResult(BaseModel):
    results: list[CodeReview | dict]
    total_time_s: float


@router.get("/health")
async def health():
    return {"status": "ok", "model": "gpt-4o-mini"}


@router.post("/review/batch", response_model=BatchResult)
async def batch_review(req: BatchRequest):
    t = time.perf_counter()
    results = await review_batch(req.snippets, req.max_concurrent)
    elapsed = time.perf_counter() - t

    serialized = [
        r.model_dump() if isinstance(r, CodeReview) else {"error": str(r)}
        for r in results
    ]

    return BatchResult(results=serialized, total_time_s=round(elapsed, 2))


@router.post("/review/stream")
async def stream_review(req: BatchRequest):
    async def event_generator():
        sem = asyncio.Semaphore(req.max_concurrent)
        queue = asyncio.Queue()

        async def worker(i, snippet):
            async with sem:
                try:
                    result = await review_code(snippet)
                except Exception as exc:
                    result = exc
                await queue.put((i, result))

        tasks = [asyncio.create_task(worker(i, s)) for i, s in enumerate(req.snippets)]

        for _ in req.snippets:
            i, result = await queue.get()
            payload = {
                "index": i,
                "result": (
                    result.model_dump()
                    if isinstance(result, CodeReview)
                    else {"error": str(result)}
                ),
            }
            yield f"data: {json.dumps(payload)}\n\n"

        await asyncio.gather(*tasks)

    return StreamingResponse(event_generator(), media_type="text/event-stream")