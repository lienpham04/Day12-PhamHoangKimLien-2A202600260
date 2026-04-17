import time
from fastapi import HTTPException
from .config import settings

class RateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self._cache = {} # In-memory for now, production should use Redis

    def check_rate_limit(self, user_id: str):
        now = time.time()
        user_requests = self._cache.get(user_id, [])
        
        # Filter requests from the last minute
        user_requests = [t for t in user_requests if now - t < 60]
        
        if len(user_requests) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute."
            )
        
        user_requests.append(now)
        self._cache[user_id] = user_requests

rate_limiter = RateLimiter(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

def check_rate_limit_dependency(user_id: str):
    rate_limiter.check_rate_limit(user_id)
