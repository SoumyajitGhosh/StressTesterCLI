import asyncio
import json

import httpx

async def main():
    url = "http://localhost:8000/review/stream"
    payload = {"snippets": ["x=1", "y=2"], "max_concurrent": 2}

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            print("Connected to stream, waiting for events...")

            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    data = line[len("data:"):].strip()
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        print("Received non-JSON data:", data)
                        continue
                    print("Event:", json.dumps(event, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
