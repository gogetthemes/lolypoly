"""Tests for account manager"""

import pytest
from src.accounts.manager import AccountManager
from src.database.models import Account


class TestAccountManager:
    """Test account manager"""
    
    def test_create_account(self, db_session):
        """Test creating an account"""
        manager = AccountManager(db_session)
        
        account = manager.create_account(
            name="Test Account",
            api_key="test_api_key_1234567890",
            api_secret="test_api_secret",
            account_type="source"
        )
        
        assert account.name == "Test Account"
        assert account.enabled == True
        assert account.account_type.value == "source"
    
    def test_get_account(self, db_session):
        """Test getting an account"""
        manager = AccountManager(db_session)
        
        account = manager.create_account(
            name="Test Account 2",
            api_key="test_api_key_abcdefghij",
            api_secret="test_api_secret_2"
        )
        
        retrieved = manager.get_account(account.id)
        assert retrieved is not None
        assert retrieved.name == "Test Account 2"
    
    def test_list_accounts(self, db_session):
        """Test listing accounts"""
        manager = AccountManager(db_session)
        
        manager.create_account(
            name="Account 1",
            api_key="test_key_111111111111",
            api_secret="secret_1"
        )
        manager.create_account(
            name="Account 2",
            api_key="test_key_222222222222",
            api_secret="secret_2"
        )
        
        accounts = manager.list_accounts()
        assert len(accounts) >= 2
    
    def test_update_account(self, db_session):
        """Test updating an account"""
        manager = AccountManager(db_session)
        
        account = manager.create_account(
            name="Original Name",
            api_key="test_key_333333333333",
            api_secret="secret_3"
        )
        
        updated = manager.update_account(account.id, name="Updated Name")
        assert updated.name == "Updated Name"
    
    def test_delete_account(self, db_session):
        """Test deleting an account"""
        manager = AccountManager(db_session)
        
        account = manager.create_account(
            name="To Delete",
            api_key="test_key_444444444444",
            api_secret="secret_4"
        )
        
        deleted = manager.delete_account(account.id)
        assert deleted == True
        
        retrieved = manager.get_account(account.id)
        assert retrieved is None
