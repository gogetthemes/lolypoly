"""Stress tests checking RateLimiter and concurrency stability"""

import pytest
import asyncio
from src.security.rate_limiter import APISecurityManager


@pytest.mark.asyncio
async def test_rate_limiter_stress():
    """Simulate rapid bursts of API requests to check rate limiting precision"""
    manager = APISecurityManager({
        "rate_limit_requests": 50,
        "rate_limit_window": 10
    })
    
    ip = "192.168.1.100"
    
    # Send 50 allowed requests rapidly
    for _ in range(50):
        allowed, resp = manager.check_rate_limit(ip)
        assert allowed is True
        
    # 51st request should be blocked instantly
    allowed, resp = manager.check_rate_limit(ip)
    assert allowed is False
    assert resp["remaining_requests"] == 0
    assert resp["reset_time_seconds"] > 0
