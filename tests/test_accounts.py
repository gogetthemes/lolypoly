"""Tests for account manager"""

import pytest
from src.accounts.manager import AccountManager
from src.database.models import AccountType


def test_create_account(db_session):
    """Test account creation"""
    manager = AccountManager(db_session)
    
    account = manager.create_account(
        name="Test Account",
        api_key="test_key_12345",
        api_secret="test_secret_12345",
        account_type="source"
    )
    
    assert account is not None
    assert account.name == "Test Account"
    assert account.account_type == AccountType.SOURCE
    assert account.enabled is True


def test_get_account(db_session):
    """Test getting account"""
    manager = AccountManager(db_session)
    
    created = manager.create_account(
        name="Test Account",
        api_key="test_key_12345",
        api_secret="test_secret_12345"
    )
    
    retrieved = manager.get_account(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Test Account"


def test_list_accounts(db_session):
    """Test listing accounts"""
    manager = AccountManager(db_session)
    
    manager.create_account("Account 1", "key1", "secret1")
    manager.create_account("Account 2", "key2", "secret2")
    
    accounts = manager.list_accounts()
    
    assert len(accounts) == 2


def test_update_account(db_session):
    """Test updating account"""
    manager = AccountManager(db_session)
    
    account = manager.create_account("Old Name", "key", "secret")
    updated = manager.update_account(account.id, name="New Name")
    
    assert updated.name == "New Name"


def test_delete_account(db_session):
    """Test deleting account"""
    manager = AccountManager(db_session)
    
    account = manager.create_account("Test", "key", "secret")
    
    deleted = manager.delete_account(account.id)
    assert deleted is True
    
    retrieved = manager.get_account(account.id)
    assert retrieved is None


def test_enable_disable_account(db_session):
    """Test enabling/disabling account"""
    manager = AccountManager(db_session)
    
    account = manager.create_account("Test", "key", "secret", enabled=True)
    
    disabled = manager.disable_account(account.id)
    assert disabled is True
    
    retrieved = manager.get_account(account.id)
    assert retrieved.enabled is False
    
    enabled = manager.enable_account(account.id)
    assert enabled is True
    
    retrieved = manager.get_account(account.id)
    assert retrieved.enabled is True
