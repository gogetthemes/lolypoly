"""Strategy manager for managing trading strategies"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from src.database.models import Strategy, CopyMode
from src.strategies.filters import TradeFilter
from src.utils.logger import get_logger

logger = get_logger("strategies")


class StrategyManager:
    """Manages trading strategies"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_strategy(self, name: str, source_account_id: str, 
                       target_accounts: List[str], copy_mode: str = "full",
                       filters: Optional[Dict[str, Any]] = None,
                       enabled: bool = True) -> Strategy:
        """Create new trading strategy"""
        logger.info(f"Creating strategy: {name}")
        
        strategy_id = f"strat_{uuid.uuid4().hex[:8]}"
        
        if filters is None:
            filters = {}
        
        strategy = Strategy(
            id=strategy_id,
            name=name,
            source_account_id=source_account_id,
            target_accounts=target_accounts,
            copy_mode=CopyMode(copy_mode),
            filters=filters,
            enabled=enabled
        )
        
        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)
        
        logger.info(f"Strategy created: {strategy_id}")
        return strategy
    
    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Get strategy by ID"""
        return self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    def list_strategies(self, enabled_only: bool = False) -> List[Strategy]:
        """List all strategies"""
        query = self.db.query(Strategy)
        
        if enabled_only:
            query = query.filter(Strategy.enabled == True)
        
        return query.all()
    
    def list_strategies_by_source(self, source_account_id: str, 
                                 enabled_only: bool = False) -> List[Strategy]:
        """List strategies for specific source account"""
        query = self.db.query(Strategy).filter(
            Strategy.source_account_id == source_account_id
        )
        
        if enabled_only:
            query = query.filter(Strategy.enabled == True)
        
        return query.all()
    
    def update_strategy(self, strategy_id: str, **kwargs) -> Optional[Strategy]:
        """Update strategy"""
        strategy = self.get_strategy(strategy_id)
        
        if not strategy:
            logger.warning(f"Strategy not found: {strategy_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(strategy, key) and key not in ['id', 'created_at']:
                setattr(strategy, key, value)
        
        self.db.commit()
        self.db.refresh(strategy)
        
        logger.info(f"Strategy updated: {strategy_id}")
        return strategy
    
    def update_filters(self, strategy_id: str, filters: Dict[str, Any]) -> Optional[Strategy]:
        """Update strategy filters"""
        return self.update_strategy(strategy_id, filters=filters)
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete strategy"""
        strategy = self.get_strategy(strategy_id)
        
        if not strategy:
            logger.warning(f"Strategy not found: {strategy_id}")
            return False
        
        self.db.delete(strategy)
        self.db.commit()
        
        logger.info(f"Strategy deleted: {strategy_id}")
        return True
    
    def enable_strategy(self, strategy_id: str) -> bool:
        """Enable strategy"""
        return bool(self.update_strategy(strategy_id, enabled=True))
    
    def disable_strategy(self, strategy_id: str) -> bool:
        """Disable strategy"""
        return bool(self.update_strategy(strategy_id, enabled=False))
    
    def get_trade_filter(self, strategy_id: str) -> Optional[TradeFilter]:
        """Get trade filter for strategy"""
        strategy = self.get_strategy(strategy_id)
        
        if not strategy:
            return None
        
        try:
            return TradeFilter(strategy.filters)
        except Exception as e:
            logger.error(f"Error creating filter for strategy {strategy_id}: {e}")
            return None
