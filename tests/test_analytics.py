"""Tests for statistics calculator"""

import pytest
from datetime import datetime
from src.analytics.stats import StatsCalculator
from src.accounts.manager import AccountManager
from src.database.models import Trade


class TestStatsCalculator:
    """Test statistics calculator"""
    
    def test_update_account_stats(self, db_session):
        """Test updating account statistics"""
        # Create account
        acc_manager = AccountManager(db_session)
        account = acc_manager.create_account(
            name="Test Account",
            api_key="test_key_stats_1234567890",
            api_secret="test_secret"
        )
        
        # Add some trades
        for i in range(5):
            trade = Trade(
                id=f"trade_{i}",
                source_account_id=account.id,
                symbol="BTC/USDT",
                trade_type="BUY",
                original_amount=100.0,
                copied_amount=100.0,
                original_price=50000.0,
                actual_price=50000.0,
                status="completed" if i % 2 == 0 else "failed",
                source_opened_at=datetime.utcnow()
            )
            db_session.add(trade)
        
        db_session.commit()
        
        # Calculate stats
        stats_calc = StatsCalculator(db_session)
        stats_calc.update_account_stats(account.id)
        
        # Verify stats
        stats = stats_calc.get_account_stats(account.id)
        assert stats is not None
        assert stats["total_trades"] == 5
        assert stats["successful_trades"] == 3
        assert stats["failed_trades"] == 2
    
    def test_get_account_stats(self, db_session):
        """Test getting account statistics"""
        acc_manager = AccountManager(db_session)
        account = acc_manager.create_account(
            name="Stats Test",
            api_key="stats_key_1234567890abcd",
            api_secret="stats_secret"
        )
        
        stats_calc = StatsCalculator(db_session)
        stats = stats_calc.get_account_stats(account.id)
        
        # Should return empty stats for new account
        assert stats is not None
        assert stats["total_trades"] == 0
