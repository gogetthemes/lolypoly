"""Tests for trade filters"""

import pytest
from src.strategies.filters import TradeFilter


class TestTradeFilter:
    """Test trade filter logic"""
    
    def test_filter_by_amount_range(self):
        """Test filtering by amount range"""
        filters = {
            "min_amount": 100,
            "max_amount": 1000
        }
        trade_filter = TradeFilter(filters)
        
        # Trade within range
        trade_data = {"amount": 500}
        assert trade_filter.should_copy(trade_data) == True
        
        # Trade below min
        trade_data = {"amount": 50}
        assert trade_filter.should_copy(trade_data) == False
        
        # Trade above max
        trade_data = {"amount": 2000}
        assert trade_filter.should_copy(trade_data) == False
    
    def test_apply_amount_multiplier(self):
        """Test amount multiplier application"""
        filters = {
            "amount_multiplier": 0.5
        }
        trade_filter = TradeFilter(filters)
        
        result = trade_filter.apply_amount_modification(1000)
        assert result == 500
    
    def test_apply_amount_percent(self):
        """Test amount percentage application"""
        filters = {
            "amount_percent": 75
        }
        trade_filter = TradeFilter(filters)
        
        result = trade_filter.apply_amount_modification(1000)
        assert result == 750
    
    def test_get_slippage_tolerance(self):
        """Test getting slippage tolerance"""
        filters = {
            "slippage_percent": 0.5
        }
        trade_filter = TradeFilter(filters)
        
        assert trade_filter.get_slippage_tolerance() == 0.5
    
    def test_get_filter_summary(self):
        """Test filter summary generation"""
        filters = {
            "min_amount": 100,
            "max_amount": 1000,
            "amount_multiplier": 0.5,
            "slippage_percent": 0.5,
            "real_time": True
        }
        trade_filter = TradeFilter(filters)
        
        summary = trade_filter.get_filter_summary()
        assert "Min: 100" in summary
        assert "Max: 1000" in summary
        assert "Size: 50.0%" in summary
        assert "Slippage: 0.5%" in summary
        assert "Real-time only" in summary
