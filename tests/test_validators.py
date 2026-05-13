"""Tests for validators"""

import pytest
from src.utils.validators import (
    validate_api_key,
    validate_amount,
    validate_completion_time,
    apply_amount_filter,
    calculate_completion_deadline
)
from datetime import datetime, timedelta


class TestValidators:
    """Test validation utilities"""
    
    def test_validate_api_key(self):
        """Test API key validation"""
        # Valid key
        assert validate_api_key("valid_key_1234567890") == True
        
        # Invalid keys
        with pytest.raises(ValueError):
            validate_api_key("short")
        
        with pytest.raises(ValueError):
            validate_api_key("")
    
    def test_validate_amount(self):
        """Test amount validation"""
        # Valid amount
        assert validate_amount(100.0) == True
        
        # Invalid amount
        assert validate_amount(0) == False
        assert validate_amount(-100) == False
        
        # With range
        assert validate_amount(100, min_amount=50, max_amount=200) == True
        assert validate_amount(30, min_amount=50, max_amount=200) == False
        assert validate_amount(300, min_amount=50, max_amount=200) == False
    
    def test_validate_completion_time(self):
        """Test completion time validation"""
        # Valid
        assert validate_completion_time({"type": "hours", "value": 24}) == True
        assert validate_completion_time({"type": "days", "value": 7}) == True
        
        # Invalid
        with pytest.raises(ValueError):
            validate_completion_time({"type": "invalid", "value": 24})
        
        with pytest.raises(ValueError):
            validate_completion_time({"type": "hours", "value": -1})
    
    def test_apply_amount_filter(self):
        """Test amount filter application"""
        # With multiplier
        assert apply_amount_filter(1000, multiplier=0.5) == 500
        
        # With percent
        assert apply_amount_filter(1000, percent=50) == 500
        
        # Without filter
        assert apply_amount_filter(1000) == 1000
    
    def test_calculate_completion_deadline(self):
        """Test deadline calculation"""
        before = datetime.utcnow()
        
        # Hours
        deadline = calculate_completion_deadline({"type": "hours", "value": 1})
        after = datetime.utcnow()
        
        assert before < deadline < after + timedelta(hours=2)
        
        # Days
        deadline = calculate_completion_deadline({"type": "days", "value": 1})
        assert before < deadline < after + timedelta(days=2)
