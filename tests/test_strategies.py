"""Tests for strategy manager"""

import pytest
from src.strategies.manager import StrategyManager
from src.accounts.manager import AccountManager


class TestStrategyManager:
    """Test strategy manager"""
    
    @pytest.fixture
    def source_account(self, db_session):
        """Create a source account for testing"""
        manager = AccountManager(db_session)
        return manager.create_account(
            name="Source Account",
            api_key="source_key_1234567890ab",
            api_secret="source_secret",
            account_type="source"
        )
    
    @pytest.fixture
    def target_account(self, db_session):
        """Create a target account for testing"""
        manager = AccountManager(db_session)
        return manager.create_account(
            name="Target Account",
            api_key="target_key_cdefghijklmn",
            api_secret="target_secret",
            account_type="target"
        )
    
    def test_create_strategy(self, db_session, source_account, target_account):
        """Test creating a strategy"""
        manager = StrategyManager(db_session)
        
        strategy = manager.create_strategy(
            name="Test Strategy",
            source_account_id=source_account.id,
            target_accounts=[target_account.id],
            copy_mode="full"
        )
        
        assert strategy.name == "Test Strategy"
        assert strategy.enabled == True
        assert strategy.copy_mode.value == "full"
    
    def test_list_strategies(self, db_session, source_account, target_account):
        """Test listing strategies"""
        manager = StrategyManager(db_session)
        
        manager.create_strategy(
            name="Strategy 1",
            source_account_id=source_account.id,
            target_accounts=[target_account.id]
        )
        
        strategies = manager.list_strategies()
        assert len(strategies) >= 1
    
    def test_update_strategy(self, db_session, source_account, target_account):
        """Test updating a strategy"""
        manager = StrategyManager(db_session)
        
        strategy = manager.create_strategy(
            name="Original Name",
            source_account_id=source_account.id,
            target_accounts=[target_account.id]
        )
        
        updated = manager.update_strategy(strategy.id, name="Updated Name")
        assert updated.name == "Updated Name"
    
    def test_delete_strategy(self, db_session, source_account, target_account):
        """Test deleting a strategy"""
        manager = StrategyManager(db_session)
        
        strategy = manager.create_strategy(
            name="To Delete",
            source_account_id=source_account.id,
            target_accounts=[target_account.id]
        )
        
        deleted = manager.delete_strategy(strategy.id)
        assert deleted == True
        
        retrieved = manager.get_strategy(strategy.id)
        assert retrieved is None
