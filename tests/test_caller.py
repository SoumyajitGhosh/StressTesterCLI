import asyncio

import pytest
from src.caller import review_batch

class DummyError(Exception):
    pass

async def failing_review_code(snippet: str):
    raise DummyError("forced failure")

@pytest.mark.asyncio
async def test_review_batch_returns_exception_on_failure(monkeypatch):
    monkeypatch.setattr('src.caller.review_code', failing_review_code)

    snippets = ["x = 1", "y = 2"]
    results = await review_batch(snippets, max_concurrent=2)

    assert len(results) == len(snippets)
    for result in results:
        assert isinstance(result, Exception)
        assert isinstance(result, DummyError)
        assert str(result) == "forced failure"
