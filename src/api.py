from fastapi import FastAPI
from pydantic import BaseModel
from .caller import review_batch
from .models import CodeReview

app = FastAPI(title="LLM Stress-Tester")

class BatchRequest(BaseModel):
    snippets: list[str]
    max_concurrent: int = 5

class BatchResult(BaseModel):
    results: list[CodeReview | dict]  # dict for errors
    total_time_s: float

@app.get("/health")
async def health():
    return {"status": "ok", "model": "gpt-4o-mini"}

@app.post("/review/batch", response_model=BatchResult)
async def batch_review(req: BatchRequest):
    import time
    t = time.perf_counter()
    results = await review_batch(req.snippets, req.max_concurrent)
    elapsed = time.perf_counter() - t
    serialized = [
        r.model_dump() if isinstance(r, CodeReview)
        else {"error": str(r)}
        for r in results
    ]
    return BatchResult(results=serialized, total_time_s=round(elapsed, 2))