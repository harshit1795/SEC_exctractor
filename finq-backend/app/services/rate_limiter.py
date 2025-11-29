"""
Rate limiter for Gemini API requests
Prevents exceeding Google's API rate limits
"""
import asyncio
import time
import logging
from collections import deque
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter that ensures requests don't exceed per-minute limits
    Uses a sliding window approach
    """
    
    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed in the time window
            window_seconds: Time window in seconds (default 60 = 1 minute)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_times: deque = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Acquire permission to make a request
        Will wait if necessary to avoid exceeding rate limit
        """
        async with self.lock:
            now = time.time()
            
            # Remove requests outside the time window
            while self.request_times and self.request_times[0] < now - self.window_seconds:
                self.request_times.popleft()
            
            # If we're at the limit, wait until the oldest request expires
            if len(self.request_times) >= self.max_requests:
                oldest_time = self.request_times[0]
                wait_time = (oldest_time + self.window_seconds) - now + 0.1  # Add 0.1s buffer
                if wait_time > 0:
                    logger.info(f"Rate limit reached. Waiting {wait_time:.2f}s before next request")
                    await asyncio.sleep(wait_time)
                    # Clean up again after waiting
                    now = time.time()
                    while self.request_times and self.request_times[0] < now - self.window_seconds:
                        self.request_times.popleft()
            
            # Record this request
            self.request_times.append(time.time())
            logger.debug(f"Request allowed. {len(self.request_times)}/{self.max_requests} requests in window")


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(max_requests: int = 15, window_seconds: int = 60) -> RateLimiter:
    """Get or create global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds)
    return _rate_limiter

