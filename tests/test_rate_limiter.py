import time
import pytest
from token_bucket import TokenBucketLimiter

@pytest.mark.asyncio
async def test_token_bucket_limiter_basic():
    limiter = TokenBucketLimiter(qps=5.0, burst=2)  # allow short burst
    start = time.monotonic()
    # First two should be immediate (burst)
    await limiter.acquire()
    await limiter.acquire()
    # Third should incur delay (~ >= 0.18s for 5 qps -> 0.2s per token minus refills during waits)
    await limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed >= 0.15
