"""
Rate Limiting Middleware

Implements sliding window rate limiting for the chat API.
30 requests per minute per user as per spec.

Spec Reference: specs/PLAN.md - Task 4.9: Rate limiting (30 requests/min per user)
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = __import__('logging').getLogger(__name__)


class RateLimiter:
    """
    Sliding window rate limiter using time-based tracking.

    Tracks request timestamps per user and enforces a maximum
    number of requests within a time window.
    """

    def __init__(self, requests_per_minute: int = 30):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        # user_id -> list of timestamps
        self.windows = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if request is allowed for user.

        Args:
            user_id: The user identifier

        Returns:
            True if request is within rate limit, False otherwise
        """
        now = time.time()
        minute_ago = now - 60

        # Clean old entries (older than 60 seconds)
        self.windows[user_id] = [
            ts for ts in self.windows[user_id] if ts > minute_ago
        ]

        # Check if under limit
        if len(self.windows[user_id]) >= self.requests_per_minute:
            return False

        # Record this request
        self.windows[user_id].append(now)
        return True

    def get_retry_after(self, user_id: int) -> int:
        """
        Get seconds until next request is allowed.

        Args:
            user_id: The user identifier

        Returns:
            Seconds to wait before retry
        """
        if user_id not in self.windows or not self.windows[user_id]:
            return 0

        now = time.time()
        minute_ago = now - 60

        # Filter to entries in the last minute
        recent = [ts for ts in self.windows[user_id] if ts > minute_ago]

        if len(recent) < self.requests_per_minute:
            return 0

        # Get the oldest request in the current window
        oldest = min(recent)
        retry_after = int(60 - (now - oldest))

        return max(0, retry_after)

    def get_remaining(self, user_id: int) -> int:
        """
        Get remaining requests for the current window.

        Args:
            user_id: The user identifier

        Returns:
            Number of remaining requests
        """
        now = time.time()
        minute_ago = now - 60

        # Clean old entries
        self.windows[user_id] = [
            ts for ts in self.windows[user_id] if ts > minute_ago
        ]

        used = len(self.windows[user_id])
        return max(0, self.requests_per_minute - used)

    def reset(self, user_id: int) -> None:
        """
        Reset rate limit for a user.

        Args:
            user_id: The user identifier
        """
        self.windows[user_id] = []


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=30)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting chat API endpoints.

    Exempts health checks and documentation endpoints.
    """

    # Endpoints that don't require rate limiting
    EXEMPT_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        """
        Process request through rate limiting.

        Args:
            request: The incoming request
            call_next: The next middleware/handler

        Returns:
            Response from the application
        """
        path = request.url.path

        # Skip rate limiting for exempt paths
        if path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Get user_id from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        # If no user_id (unauthenticated), apply global limit
        if user_id is None:
            # Use IP as identifier for unauthenticated requests
            client_ip = request.client.host if request.client else "unknown"
            user_id = f"ip:{client_ip}"

        # Check rate limit
        if not rate_limiter.is_allowed(user_id):
            retry_after = rate_limiter.get_retry_after(user_id)
            remaining = 0
        else:
            retry_after = 0
            remaining = rate_limiter.get_remaining(user_id)

        # Add rate limit headers
        response = await call_next(request)

        # Only add headers if we have a user_id
        if user_id:
            response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset-In"] = str(retry_after)

        # Return 429 if rate limited
        if retry_after > 0:
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "message": f"Too many requests. Please try again in {retry_after} seconds."
                },
                headers=response.headers
            )
            response.headers["Retry-After"] = str(retry_after)
            response.headers["X-RateLimit-Remaining"] = "0"

            logger.warning(
                f"Rate limit exceeded for user {user_id}, "
                f"retry after {retry_after} seconds"
            )

        return response


def add_rate_limit_middleware(app):
    """
    Add rate limit middleware to FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(RateLimitMiddleware)
    logger.info("Rate limiting middleware added (30 requests/minute)")


# Utility functions for testing and management
def check_rate_limit(user_id: int) -> dict:
    """
    Check current rate limit status for a user.

    Args:
        user_id: The user identifier

    Returns:
        Dict with limit, remaining, and reset information
    """
    return {
        "limit": rate_limiter.requests_per_minute,
        "remaining": rate_limiter.get_remaining(user_id),
        "retry_after": rate_limiter.get_retry_after(user_id),
        "is_allowed": rate_limiter.is_allowed(user_id)
    }


def reset_rate_limit(user_id: int) -> None:
    """
    Reset rate limit counter for a user.

    Args:
        user_id: The user identifier
    """
    rate_limiter.reset(user_id)
    logger.info(f"Rate limit reset for user {user_id}")
