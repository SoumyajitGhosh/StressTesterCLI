import asyncio
import time
from src.caller import review_code

if __name__ == "__main__":
    print("Reviewing code snippet...")
    start = time.perf_counter()
    result = asyncio.run(review_code("x=1"))
    end = time.perf_counter()
    latency = end - start
    print(f"Latency: {latency:.2f} seconds")
    print(result)
