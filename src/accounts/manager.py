"""Account manager for managing trading accounts"""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.models import Account, AccountType, AccountStats
from src.utils.logger import get_logger
from src.utils.validators import validate_api_key

logger = get_logger("accounts")


class AccountManager:
    """Manages trading accounts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_account(self, name: str, api_key: str, api_secret: str,
                      account_type: str = "source", enabled: bool = True) -> Account:
        """Create new trading account"""
        logger.info(f"Creating account: {name}")
        
        validate_api_key(api_key)
        
        account_id = f"acc_{uuid.uuid4().hex[:8]}"
        
        account = Account(
            id=account_id,
            name=name,
            api_key=api_key,
            api_secret=api_secret,
            account_type=AccountType(account_type),
            enabled=enabled
        )
        
        # Create account stats
        stats = AccountStats(
            id=f"stats_{account_id}",
            account_id=account_id
        )
        
        self.db.add(account)
        self.db.add(stats)
        self.db.commit()
        self.db.refresh(account)
        
        logger.info(f"Account created: {account_id}")
        return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID"""
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def list_accounts(self, enabled_only: bool = False) -> List[Account]:
        """List all accounts"""
        query = self.db.query(Account)
        
        if enabled_only:
            query = query.filter(Account.enabled == True)
        
        return query.all()
    
    def list_source_accounts(self) -> List[Account]:
        """List all source (tracked) accounts"""
        return self.db.query(Account).filter(
            Account.account_type.in_([AccountType.SOURCE, AccountType.BOTH]),
            Account.enabled == True
        ).all()
    
    def list_target_accounts(self) -> List[Account]:
        """List all target (copy) accounts"""
        return self.db.query(Account).filter(
            Account.account_type.in_([AccountType.TARGET, AccountType.BOTH]),
            Account.enabled == True
        ).all()
    
    def update_account(self, account_id: str, **kwargs) -> Optional[Account]:
        """Update account"""
        account = self.get_account(account_id)
        
        if not account:
            logger.warning(f"Account not found: {account_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(account, key) and key not in ['id', 'created_at']:
                setattr(account, key, value)
        
        self.db.commit()
        self.db.refresh(account)
        
        logger.info(f"Account updated: {account_id}")
        return account
    
    def delete_account(self, account_id: str) -> bool:
        """Delete account"""
        account = self.get_account(account_id)
        
        if not account:
            logger.warning(f"Account not found: {account_id}")
            return False
        
        self.db.delete(account)
        self.db.commit()
        
        logger.info(f"Account deleted: {account_id}")
        return True
    
    def enable_account(self, account_id: str) -> bool:
        """Enable account"""
        return bool(self.update_account(account_id, enabled=True))
    
    def disable_account(self, account_id: str) -> bool:
        """Disable account"""
        return bool(self.update_account(account_id, enabled=False))
