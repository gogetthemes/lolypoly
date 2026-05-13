"""Trade filters for strategy application"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from src.utils.validators import (
    validate_amount, 
    validate_completion_time,
    apply_amount_filter,
    calculate_completion_deadline
)
from src.utils.logger import get_logger

logger = get_logger("filters")


class TradeFilter:
    """Filter for determining if a trade should be copied"""
    
    def __init__(self, filters: Dict[str, Any]):
        self.filters = filters
        self._validate_filters()
    
    def _validate_filters(self):
        """Validate filter configuration"""
        if "completion_time" in self.filters:
            validate_completion_time(self.filters["completion_time"])
    
    def should_copy(self, trade_data: Dict[str, Any]) -> bool:
        """Determine if trade should be copied based on filters"""
        
        # Check real-time filter
        if self.filters.get("real_time", False):
            if not self._check_real_time(trade_data):
                return False
        
        # Check amount range
        amount = trade_data.get("amount", 0)
        min_amount = self.filters.get("min_amount")
        max_amount = self.filters.get("max_amount")
        
        try:
            if not validate_amount(amount, min_amount, max_amount):
                logger.debug(f"Trade amount {amount} outside range [{min_amount}, {max_amount}]")
                return False
        except Exception as e:
            logger.error(f"Amount validation error: {e}")
            return False
        
        # Check completion time filter
        if "completion_time" in self.filters:
            if not self._check_completion_time(trade_data):
                logger.debug(f"Trade completion time filter failed")
                return False
        
        return True
    
    def _check_real_time(self, trade_data: Dict[str, Any]) -> bool:
        """Check if trade is in real-time"""
        # If trade has been open recently, it's real-time
        opened_at = trade_data.get("opened_at")
        if opened_at:
            if isinstance(opened_at, str):
                opened_at = datetime.fromisoformat(opened_at)
            time_diff = datetime.utcnow() - opened_at
            return time_diff.total_seconds() < 60  # Less than 1 minute old
        return False
    
    def _check_completion_time(self, trade_data: Dict[str, Any]) -> bool:
        """Check if trade meets completion time requirement"""
        completion_time_filter = self.filters.get("completion_time")
        if not completion_time_filter:
            return True
        
        deadline = calculate_completion_deadline(completion_time_filter)
        
        # Check if trade will complete within the deadline
        opened_at = trade_data.get("opened_at")
        if opened_at:
            if isinstance(opened_at, str):
                opened_at = datetime.fromisoformat(opened_at)
            return opened_at < deadline
        
        return True
    
    def apply_amount_modification(self, original_amount: float) -> float:
        """Apply amount modification based on filters"""
        multiplier = self.filters.get("amount_multiplier")
        percent = self.filters.get("amount_percent")
        
        return apply_amount_filter(original_amount, multiplier, percent)
    
    def get_slippage_tolerance(self) -> float:
        """Get slippage tolerance in percentage"""
        return self.filters.get("slippage_percent", 0.5)
    
    def get_filter_summary(self) -> str:
        """Get human-readable filter summary"""
        parts = []
        
        if self.filters.get("min_amount"):
            parts.append(f"Min: {self.filters['min_amount']}")
        
        if self.filters.get("max_amount"):
            parts.append(f"Max: {self.filters['max_amount']}")
        
        if self.filters.get("amount_multiplier"):
            percent = self.filters['amount_multiplier'] * 100
            parts.append(f"Size: {percent}%")
        
        if self.filters.get("amount_percent"):
            parts.append(f"Size: {self.filters['amount_percent']}%")
        
        if self.filters.get("slippage_percent"):
            parts.append(f"Slippage: {self.filters['slippage_percent']}%")
        
        if self.filters.get("real_time"):
            parts.append("Real-time only")
        
        if self.filters.get("completion_time"):
            ct = self.filters['completion_time']
            parts.append(f"Complete in: {ct['value']} {ct['type']}")
        
        return " | ".join(parts) if parts else "No filters"
