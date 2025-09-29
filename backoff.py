import random

def _compute_backoff(attempt: int, base: float = 0.5, cap: float = 8.0) -> float:
    exp = min(cap, base * (2 ** (attempt - 1)))
    jitter = random.uniform(0, exp / 2)
    return exp + jitter
