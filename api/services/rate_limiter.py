#!/usr/bin/env python3
"""
Rate Limiter Service
Handles API rate limiting and usage tracking
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
import threading
import os

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Types of rate limits"""
    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"

@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    limit_type: RateLimitType
    max_requests: int
    window_seconds: int
    endpoint_pattern: str = "*"
    user_role: Optional[str] = None

@dataclass
class RateLimitStatus:
    """Current rate limit status for a key"""
    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None
    limit: int = 0
    window_seconds: int = 0

class RateLimiter:
    """Rate limiter with sliding window implementation"""
    
    def __init__(self):
        # Storage for request timestamps per key
        self._request_logs: Dict[str, deque] = defaultdict(lambda: deque())
        self._lock = threading.RLock()
        
        # Default rate limit rules
        self._rules: List[RateLimitRule] = [
            # Global limits
            RateLimitRule(RateLimitType.PER_SECOND, 10, 1),
            RateLimitRule(RateLimitType.PER_MINUTE, 100, 60),
            RateLimitRule(RateLimitType.PER_HOUR, 1000, 3600),
            RateLimitRule(RateLimitType.PER_DAY, 10000, 86400),
            
            # Endpoint-specific limits
            RateLimitRule(RateLimitType.PER_MINUTE, 20, 60, "/api/v1/talents/search"),
            RateLimitRule(RateLimitType.PER_HOUR, 100, 3600, "/api/v1/outreach/campaign"),
            RateLimitRule(RateLimitType.PER_MINUTE, 5, 60, "/api/v1/outreach/contact"),
        ]
        
        # Load custom rules from environment
        self._load_custom_rules()
        
        # Cleanup old entries periodically
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes
        
        logger.info(f"Rate limiter initialized with {len(self._rules)} rules")
    
    def check_rate_limit(
        self,
        key: str,
        endpoint: str = "*",
        user_role: str = "user"
    ) -> RateLimitStatus:
        """Check if request is within rate limits"""
        with self._lock:
            current_time = time.time()
            
            # Cleanup old entries if needed
            if current_time - self._last_cleanup > self._cleanup_interval:
                self._cleanup_old_entries(current_time)
                self._last_cleanup = current_time
            
            # Find applicable rules
            applicable_rules = self._get_applicable_rules(endpoint, user_role)
            
            # Check each rule
            for rule in applicable_rules:
                status = self._check_rule(key, rule, current_time)
                if not status.allowed:
                    return status
            
            # All rules passed, record the request
            self._record_request(key, current_time)
            
            # Return success status with most restrictive remaining count
            min_remaining = float('inf')
            next_reset = None
            
            for rule in applicable_rules:
                remaining = self._get_remaining_requests(key, rule, current_time)
                if remaining < min_remaining:
                    min_remaining = remaining
                    next_reset = datetime.fromtimestamp(
                        current_time + rule.window_seconds
                    )
            
            return RateLimitStatus(
                allowed=True,
                remaining=int(min_remaining) if min_remaining != float('inf') else 1000,
                reset_time=next_reset or datetime.now() + timedelta(hours=1)
            )
    
    def _check_rule(
        self,
        key: str,
        rule: RateLimitRule,
        current_time: float
    ) -> RateLimitStatus:
        """Check a specific rate limit rule"""
        window_start = current_time - rule.window_seconds
        
        # Count requests in the current window
        request_log = self._request_logs[key]
        requests_in_window = sum(
            1 for timestamp in request_log 
            if timestamp > window_start
        )
        
        remaining = max(0, rule.max_requests - requests_in_window)
        reset_time = datetime.fromtimestamp(current_time + rule.window_seconds)
        
        if requests_in_window >= rule.max_requests:
            # Rate limit exceeded
            retry_after = int(rule.window_seconds)
            return RateLimitStatus(
                allowed=False,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
                limit=rule.max_requests,
                window_seconds=rule.window_seconds
            )
        
        return RateLimitStatus(
            allowed=True,
            remaining=remaining,
            reset_time=reset_time,
            limit=rule.max_requests,
            window_seconds=rule.window_seconds
        )
    
    def _get_remaining_requests(
        self,
        key: str,
        rule: RateLimitRule,
        current_time: float
    ) -> int:
        """Get remaining requests for a rule"""
        window_start = current_time - rule.window_seconds
        request_log = self._request_logs[key]
        
        requests_in_window = sum(
            1 for timestamp in request_log 
            if timestamp > window_start
        )
        
        return max(0, rule.max_requests - requests_in_window)
    
    def _record_request(self, key: str, timestamp: float):
        """Record a request timestamp"""
        self._request_logs[key].append(timestamp)
        
        # Keep only recent entries (last 24 hours)
        cutoff = timestamp - 86400
        while self._request_logs[key] and self._request_logs[key][0] < cutoff:
            self._request_logs[key].popleft()
    
    def _get_applicable_rules(
        self,
        endpoint: str,
        user_role: str
    ) -> List[RateLimitRule]:
        """Get rules applicable to the endpoint and user role"""
        applicable_rules = []
        
        for rule in self._rules:
            # Check endpoint pattern
            if rule.endpoint_pattern == "*" or endpoint.startswith(rule.endpoint_pattern):
                # Check user role
                if rule.user_role is None or rule.user_role == user_role:
                    applicable_rules.append(rule)
        
        return applicable_rules
    
    def _cleanup_old_entries(self, current_time: float):
        """Clean up old request log entries"""
        cutoff = current_time - 86400  # Keep last 24 hours
        
        for key in list(self._request_logs.keys()):
            request_log = self._request_logs[key]
            
            # Remove old entries
            while request_log and request_log[0] < cutoff:
                request_log.popleft()
            
            # Remove empty logs
            if not request_log:
                del self._request_logs[key]
    
    def _load_custom_rules(self):
        """Load custom rate limit rules from environment"""
        try:
            # Example: RATE_LIMIT_RULES=endpoint:/api/v1/search,type:per_minute,limit:50
            custom_rules_env = os.getenv('RATE_LIMIT_RULES')
            if custom_rules_env:
                # Parse custom rules (simplified implementation)
                logger.info("Custom rate limit rules found in environment")
        except Exception as e:
            logger.error(f"Failed to load custom rate limit rules: {e}")
    
    def add_rule(self, rule: RateLimitRule):
        """Add a custom rate limit rule"""
        with self._lock:
            self._rules.append(rule)
            logger.info(f"Added rate limit rule: {rule.endpoint_pattern} - {rule.max_requests}/{rule.window_seconds}s")
    
    def remove_rule(self, endpoint_pattern: str, limit_type: RateLimitType):
        """Remove a rate limit rule"""
        with self._lock:
            self._rules = [
                rule for rule in self._rules 
                if not (rule.endpoint_pattern == endpoint_pattern and rule.limit_type == limit_type)
            ]
            logger.info(f"Removed rate limit rule: {endpoint_pattern} - {limit_type.value}")
    
    def get_usage_stats(self, key: str) -> Dict[str, any]:
        """Get usage statistics for a key"""
        with self._lock:
            current_time = time.time()
            request_log = self._request_logs.get(key, deque())
            
            if not request_log:
                return {
                    "total_requests": 0,
                    "requests_last_hour": 0,
                    "requests_last_day": 0,
                    "first_request": None,
                    "last_request": None
                }
            
            # Calculate stats
            hour_ago = current_time - 3600
            day_ago = current_time - 86400
            
            requests_last_hour = sum(
                1 for timestamp in request_log 
                if timestamp > hour_ago
            )
            
            requests_last_day = sum(
                1 for timestamp in request_log 
                if timestamp > day_ago
            )
            
            return {
                "total_requests": len(request_log),
                "requests_last_hour": requests_last_hour,
                "requests_last_day": requests_last_day,
                "first_request": datetime.fromtimestamp(request_log[0]).isoformat(),
                "last_request": datetime.fromtimestamp(request_log[-1]).isoformat()
            }
    
    def get_current_limits(self, key: str, endpoint: str = "*", user_role: str = "user") -> List[Dict[str, any]]:
        """Get current rate limit status for all applicable rules"""
        with self._lock:
            current_time = time.time()
            applicable_rules = self._get_applicable_rules(endpoint, user_role)
            
            limits = []
            for rule in applicable_rules:
                remaining = self._get_remaining_requests(key, rule, current_time)
                reset_time = datetime.fromtimestamp(current_time + rule.window_seconds)
                
                limits.append({
                    "type": rule.limit_type.value,
                    "limit": rule.max_requests,
                    "remaining": remaining,
                    "reset_time": reset_time.isoformat(),
                    "window_seconds": rule.window_seconds,
                    "endpoint_pattern": rule.endpoint_pattern
                })
            
            return limits
    
    def reset_limits(self, key: str):
        """Reset rate limits for a key (admin function)"""
        with self._lock:
            if key in self._request_logs:
                del self._request_logs[key]
                logger.info(f"Rate limits reset for key: {key}")
    
    def get_global_stats(self) -> Dict[str, any]:
        """Get global rate limiter statistics"""
        with self._lock:
            current_time = time.time()
            
            total_keys = len(self._request_logs)
            total_requests = sum(len(log) for log in self._request_logs.values())
            
            # Recent activity
            hour_ago = current_time - 3600
            active_keys_last_hour = sum(
                1 for log in self._request_logs.values()
                if any(timestamp > hour_ago for timestamp in log)
            )
            
            requests_last_hour = sum(
                sum(1 for timestamp in log if timestamp > hour_ago)
                for log in self._request_logs.values()
            )
            
            return {
                "total_keys": total_keys,
                "total_requests": total_requests,
                "active_keys_last_hour": active_keys_last_hour,
                "requests_last_hour": requests_last_hour,
                "total_rules": len(self._rules),
                "memory_usage": {
                    "request_logs_count": len(self._request_logs),
                    "avg_log_size": total_requests / max(total_keys, 1)
                }
            }
    
    def export_rules(self) -> List[Dict[str, any]]:
        """Export current rate limit rules"""
        return [
            {
                "limit_type": rule.limit_type.value,
                "max_requests": rule.max_requests,
                "window_seconds": rule.window_seconds,
                "endpoint_pattern": rule.endpoint_pattern,
                "user_role": rule.user_role
            }
            for rule in self._rules
        ]
    
    def import_rules(self, rules_data: List[Dict[str, any]]):
        """Import rate limit rules"""
        with self._lock:
            new_rules = []
            for rule_data in rules_data:
                try:
                    rule = RateLimitRule(
                        limit_type=RateLimitType(rule_data['limit_type']),
                        max_requests=rule_data['max_requests'],
                        window_seconds=rule_data['window_seconds'],
                        endpoint_pattern=rule_data.get('endpoint_pattern', '*'),
                        user_role=rule_data.get('user_role')
                    )
                    new_rules.append(rule)
                except Exception as e:
                    logger.error(f"Failed to import rule {rule_data}: {e}")
            
            self._rules = new_rules
            logger.info(f"Imported {len(new_rules)} rate limit rules")