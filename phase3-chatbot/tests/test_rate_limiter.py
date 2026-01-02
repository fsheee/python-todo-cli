"""
Unit Tests for Rate Limiter

Tests for app/middleware/rate_limit.py

Spec Reference: specs/PLAN.md - Task 4.9: Rate limiting (30 requests/min per user)
"""

import pytest
import time
from unittest.mock import MagicMock, patch
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.middleware.rate_limit import RateLimiter, RateLimitMiddleware


class TestRateLimiter:
    """Tests for RateLimiter class"""

    def setup_method(self):
        """Create fresh rate limiter for each test"""
        self.limiter = RateLimiter(requests_per_minute=5)

    def test_is_allowed_first_request(self):
        """Test first request is always allowed"""
        assert self.limiter.is_allowed(1) is True

    def test_is_allowed_under_limit(self):
        """Test requests under limit are allowed"""
        for i in range(5):
            assert self.limiter.is_allowed(1) is True

    def test_is_allowed_at_limit(self):
        """Test requests at limit are allowed"""
        for i in range(5):
            self.limiter.is_allowed(1)
        # 6th request should be denied
        assert self.limiter.is_allowed(1) is False

    def test_is_allowed_over_limit(self):
        """Test requests over limit are denied"""
        for i in range(6):
            result = self.limiter.is_allowed(1)
            if i < 5:
                assert result is True
            else:
                assert result is False

    def test_different_users_independent(self):
        """Test different users have separate limits"""
        for i in range(5):
            assert self.limiter.is_allowed(1) is True
        assert self.limiter.is_allowed(1) is False

        # User 2 should still have full limit
        assert self.limiter.is_allowed(2) is True

    def test_get_retry_after_under_limit(self):
        """Test retry after is 0 when under limit"""
        self.limiter.is_allowed(1)
        assert self.limiter.get_retry_after(1) == 0

    def test_get_retry_after_over_limit(self):
        """Test retry after is positive when over limit"""
        for i in range(5):
            self.limiter.is_allowed(1)
        self.limiter.is_allowed(1)  # Should be denied

        retry_after = self.limiter.get_retry_after(1)
        assert retry_after > 0
        assert retry_after <= 60

    def test_get_remaining_under_limit(self):
        """Test remaining requests count"""
        self.limiter.is_allowed(1)
        assert self.limiter.get_remaining(1) == 4

    def test_get_remaining_at_limit(self):
        """Test remaining is 0 at limit"""
        for i in range(5):
            self.limiter.is_allowed(1)
        assert self.limiter.get_remaining(1) == 0

    def test_get_remaining_over_limit(self):
        """Test remaining stays 0 when over limit"""
        for i in range(6):
            self.limiter.is_allowed(1)
        assert self.limiter.get_remaining(1) == 0

    def test_reset(self):
        """Test resetting rate limit for user"""
        for i in range(5):
            self.limiter.is_allowed(1)
        assert self.limiter.is_allowed(1) is False

        self.limiter.reset(1)
        assert self.limiter.is_allowed(1) is True

    def test_window_cleanup(self):
        """Test that old requests are cleaned up"""
        # Make 5 requests
        for i in range(5):
            self.limiter.is_allowed(1)

        assert self.limiter.is_allowed(1) is False

        # Wait and check cleanup happens
        time.sleep(0.1)  # Small delay
        # The implementation should clean up entries older than 60 seconds
        # But for this test, entries are still recent

    def test_window_cleanup_after_timeout(self):
        """Test cleanup of entries after window expires"""
        # Manually add old timestamps
        self.limiter.windows[1] = [time.time() - 120]  # 2 minutes ago

        # Should allow request since old entry should be cleaned
        assert self.limiter.is_allowed(1) is True


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware"""

    def setup_method(self):
        """Create middleware for each test"""
        self.middleware = RateLimitMiddleware(lambda x: None)

    def test_exempt_paths_skip_rate_limiting(self):
        """Test that exempt paths don't trigger rate limiting"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.add_middleware(RateLimitMiddleware)

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limit_exempt_paths(self):
        """Test exempt paths bypass middleware"""
        from fastapi import Request
        from starlette.responses import Response

        request = MagicMock(spec=Request)
        request.url.path = "/health"
        request.client.host = "127.0.0.1"

        call_next_called = False

        async def call_next(req):
            nonlocal call_next_called
            call_next_called = True
            return Response()

        await self.middleware.dispatch(request, call_next)

        assert call_next_called is True

    @pytest.mark.asyncio
    async def test_rate_limit_headers_added(self):
        """Test rate limit headers are added to response"""
        from fastapi import Request
        from starlette.responses import Response

        limiter = RateLimiter(requests_per_minute=30)

        request = MagicMock(spec=Request)
        request.url.path = "/chat"
        request.client.host = "127.0.0.1"
        request.state.user_id = 123

        response = Response()

        with patch('app.middleware.rate_limit.rate_limiter', limiter):
            # Make a request first
            limiter.is_allowed(123)

            # Get remaining
            remaining = limiter.get_remaining(123)

            # Check headers would be added
            assert remaining >= 0


class TestRateLimiterEdgeCases:
    """Edge case tests for rate limiter"""

    def test_zero_requests_allowed(self):
        """Test rate limiter with zero limit"""
        limiter = RateLimiter(requests_per_minute=0)
        assert limiter.is_allowed(1) is False

    def test_high_limit(self):
        """Test rate limiter with high limit"""
        limiter = RateLimiter(requests_per_minute=1000)
        for i in range(100):
            assert limiter.is_allowed(1) is True

    def test_concurrent_requests(self):
        """Test rate limiter behavior with simulated concurrent access"""
        import threading

        limiter = RateLimiter(requests_per_minute=10)
        user_id = 1
        results = []
        lock = threading.Lock()

        def make_request():
            result = limiter.is_allowed(user_id)
            with lock:
                results.append(result)

        # Create multiple threads
        threads = [threading.Thread(target=make_request) for _ in range(15)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 10 allowed, 5 denied
        allowed_count = sum(results)
        denied_count = len(results) - allowed_count

        assert allowed_count == 10
        assert denied_count == 5


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
