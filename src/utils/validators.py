"""Validation utilities"""

from typing import Optional
from datetime import datetime, timedelta


def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key or len(api_key) < 10:
        raise ValueError("Invalid API key")
    return True


def validate_amount(amount: float, min_amount: Optional[float] = None,
                   max_amount: Optional[float] = None) -> bool:
    """Validate trade amount"""
    if amount <= 0:
        return False
    
    if min_amount is not None and amount < min_amount:
        return False
    
    if max_amount is not None and amount > max_amount:
        return False
    
    return True


def validate_completion_time(completion_time: dict) -> bool:
    """Validate completion time configuration"""
    if not completion_time or "type" not in completion_time or "value" not in completion_time:
        raise ValueError("Invalid completion time configuration")
    
    time_type = completion_time["type"]
    if time_type not in ["hours", "days"]:
        raise ValueError(f"Invalid time type: {time_type}")
    
    if completion_time["value"] <= 0:
        raise ValueError("Completion time value must be positive")
    
    return True


def apply_amount_filter(original_amount: float, multiplier: Optional[float] = None,
                       percent: Optional[float] = None) -> float:
    """Apply amount modification"""
    if multiplier is not None:
        return original_amount * multiplier
    elif percent is not None:
        return original_amount * (percent / 100)
    else:
        return original_amount


def calculate_completion_deadline(completion_time: dict) -> datetime:
    """Calculate deadline based on completion time"""
    time_type = completion_time["type"]
    value = completion_time["value"]
    
    now = datetime.utcnow()
    
    if time_type == "hours":
        return now + timedelta(hours=value)
    elif time_type == "days":
        return now + timedelta(days=value)
    else:
        return now
