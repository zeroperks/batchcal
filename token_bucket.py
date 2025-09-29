import time
import asyncio
from typing import Protocol

class RateLimiter(Protocol):
    async def acquire(self) -> None: ...

class TokenBucketLimiter:
    """
    Simple token bucket rate limiter.

    qps: average tokens per second added.
    burst: max tokens accumulated (defaults to 1 token if not set).
    """
    def __init__(self, qps: float, burst: int | None = None):
        self.qps = max(0.1, qps)
        self.capacity = float(burst) if burst is not None else 1.0
        self.tokens = self.capacity
        self.last = time.monotonic()

    async def acquire(self) -> None:
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

# Backward compatibility alias (old name)
_TokenBucket = TokenBucketLimiter
