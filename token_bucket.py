import time
import asyncio

class _TokenBucket:
    def __init__(self, qps: float):
        self.qps = max(0.1, qps)
        self.capacity = 1.0
        self.tokens = self.capacity
        self.last = time.monotonic()

    async def acquire(self):
        while True:
            now = time.monotonic()
            elapsed = now - self.last
            self.last = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.qps)
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return
            need = (1.0 - self.tokens) / self.qps
            await asyncio.sleep(max(need, 0.001))
