import json

import pytest
from httpx import AsyncClient

from src.stresstestercli.api import app

@pytest.mark.anycio
async def test_stream_review_endpoint_sends_sse_events():
    payload = {"snippets": ["x=1", "y=2"], "max_concurrent": 1}

    async with AsyncClient(app=app, base_url="http://test") as client:
        async with client.stream("POST", "/review/stream", json=payload) as response:
            assert response.status_code == 200

            events = []
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    event_data = line[len("data:"):].strip()
                    event = json.loads(event_data)
                    events.append(event)

            assert len(events) == 2
            for event in events:
                assert "index" in event
                assert "result" in event
                assert event["result"]["verdict"] in {"pass", "warn", "fail"}
                assert isinstance(event["result"]["score"], int)
                assert "issues" in event["result"]
                assert "suggestions" in event["result"]
