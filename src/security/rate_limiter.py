"""API Security - Rate limiting and request validation"""

from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import asyncio
from src.utils.logger import get_logger

logger = get_logger("rate_limiter")


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> Tuple[bool, int, int]:
        """
        Check if request is allowed
        Returns: (is_allowed, remaining_requests, reset_time_seconds)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check if allowed
        remaining = self.max_requests - len(self.requests[identifier])
        
        if remaining > 0:
            self.requests[identifier].append(now)
            return True, remaining, 0
        else:
            # Calculate reset time
            oldest_request = self.requests[identifier][0]
            reset_time = int((oldest_request - window_start).total_seconds())
            return False, 0, reset_time


class APISecurityManager:
    """Manage API security features"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.rate_limiter = RateLimiter(
            max_requests=self.config.get("rate_limit_requests", 100),
            window_seconds=self.config.get("rate_limit_window", 60)
        )
        self.allowed_ips = self.config.get("allowed_ips", [])  # Empty = all allowed
        self.require_https = self.config.get("require_https", True)
        self.api_key_required = self.config.get("api_key_required", False)
    
    def check_rate_limit(self, identifier: str) -> Tuple[bool, Dict]:
        """
        Check if request passes rate limit
        Returns: (is_allowed, response_dict)
        """
        is_allowed, remaining, reset_time = self.rate_limiter.is_allowed(identifier)
        
        response = {
            "allowed": is_allowed,
            "remaining_requests": remaining,
            "reset_time_seconds": reset_time
        }
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {identifier}. Reset in {reset_time}s")
        
        return is_allowed, response
    
    def check_ip_allowed(self, ip_address: str) -> bool:
        """
        Check if IP is in whitelist
        """
        if not self.allowed_ips:
            return True  # All IPs allowed
        
        if ip_address in self.allowed_ips:
            return True
        
        logger.warning(f"Request from unauthorized IP: {ip_address}")
        return False
    
    def check_https(self, is_https: bool) -> bool:
        """
        Check if request uses HTTPS
        """
        if self.require_https and not is_https:
            logger.warning("Request without HTTPS received")
            return False
        return True
