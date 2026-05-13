"""Trade copier - main logic for copying trades"""

import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.models import Trade, Strategy, Account
from src.accounts.manager import AccountManager
from src.strategies.manager import StrategyManager
from src.trading.pooymarket_api import PooymarketAPI
from src.utils.logger import get_logger

logger = get_logger("copier")


class TradeCopier:
    """Main trade copier logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.account_manager = AccountManager(db)
        self.strategy_manager = StrategyManager(db)
        self.active_api_clients: Dict[str, PooymarketAPI] = {}
    
    async def copy_trade(self, strategy: Strategy, source_trade_data: Dict[str, Any]) -> Optional[Trade]:
        """Copy a trade based on strategy"""
        
        # Get trade filter
        trade_filter = self.strategy_manager.get_trade_filter(strategy.id)
        if not trade_filter:
            logger.error(f"Could not get filter for strategy {strategy.id}")
            return None
        
        # Check if trade should be copied
        if not trade_filter.should_copy(source_trade_data):
            logger.debug(f"Trade filtered out by strategy {strategy.id}")
            return None
        
        logger.info(f"Copying trade from strategy {strategy.id}: {source_trade_data}")
        
        # Calculate copied amount
        original_amount = source_trade_data.get("amount", 0)
        copied_amount = trade_filter.apply_amount_modification(original_amount)
        
        logger.info(f"Original amount: {original_amount}, Copied amount: {copied_amount}")
        
        # Get target account
        if not strategy.target_accounts:
            logger.warning(f"No target accounts for strategy {strategy.id}")
            return None
        
        target_account_id = strategy.target_accounts[0]
        target_account = self.account_manager.get_account(target_account_id)
        
        if not target_account:
            logger.error(f"Target account not found: {target_account_id}")
            return None
        
        # Create trade record
        trade_id = f"trade_{uuid.uuid4().hex[:8]}"
        trade = Trade(
            id=trade_id,
            strategy_id=strategy.id,
            source_account_id=strategy.source_account_id,
            target_account_id=target_account_id,
            symbol=source_trade_data.get("symbol", ""),
            trade_type=source_trade_data.get("type", "BUY"),
            original_amount=original_amount,
            copied_amount=copied_amount,
            original_price=source_trade_data.get("price", 0),
            status="pending",
            source_opened_at=datetime.utcnow(),
            metadata={
                "filter_summary": trade_filter.get_filter_summary(),
                "source_trade_id": source_trade_data.get("id")
            }
        )
        
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        
        logger.info(f"Trade record created: {trade_id}")
        
        # Execute trade on target account
        success = await self._execute_trade(target_account, copied_amount, source_trade_data, trade)
        
        if success:
            trade.status = "completed"
            trade.copied_at = datetime.utcnow()
            logger.info(f"Trade {trade_id} completed successfully")
        else:
            trade.status = "failed"
            logger.error(f"Trade {trade_id} failed to execute")
        
        self.db.commit()
        return trade
    
    async def _execute_trade(self, account: Account, amount: float,
                            source_trade_data: Dict[str, Any], 
                            trade_record: Trade) -> bool:
        """Execute trade on target account"""
        
        try:
            async with PooymarketAPI(account.api_key, account.api_secret) as api:
                result = await api.create_trade(
                    symbol=source_trade_data.get("symbol"),
                    trade_type=source_trade_data.get("type"),
                    amount=amount,
                    price=source_trade_data.get("price"),
                    stop_loss=source_trade_data.get("stop_loss"),
                    take_profit=source_trade_data.get("take_profit")
                )
                
                if result:
                    trade_record.actual_price = result.get("price")
                    trade_record.metadata["executed_trade_id"] = result.get("id")
                    self.db.commit()
                    return True
                else:
                    return False
        
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    async def close_trade(self, trade_id: str) -> bool:
        """Close a trade"""
        trade = self.db.query(Trade).filter(Trade.id == trade_id).first()
        
        if not trade:
            logger.warning(f"Trade not found: {trade_id}")
            return False
        
        if trade.status == "closed":
            logger.warning(f"Trade already closed: {trade_id}")
            return True
        
        target_account = self.account_manager.get_account(trade.target_account_id)
        if not target_account:
            logger.error(f"Target account not found: {trade.target_account_id}")
            return False
        
        try:
            async with PooymarketAPI(target_account.api_key, target_account.api_secret) as api:
                executed_trade_id = trade.metadata.get("executed_trade_id")
                if executed_trade_id:
                    success = await api.close_trade(executed_trade_id)
                    
                    if success:
                        trade.status = "closed"
                        trade.closed_at = datetime.utcnow()
                        self.db.commit()
                        logger.info(f"Trade closed: {trade_id}")
                        return True
        
        except Exception as e:
            logger.error(f"Error closing trade: {e}")
        
        return False
    
    def get_account_stats(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for account"""
        account = self.account_manager.get_account(account_id)
        
        if not account or not account.stats:
            return None
        
        stats = account.stats
        return {
            "account_id": account_id,
            "account_name": account.name,
            "total_trades": stats.total_trades,
            "successful_trades": stats.successful_trades,
            "failed_trades": stats.failed_trades,
            "total_profit": stats.total_profit,
            "win_rate": stats.win_rate,
            "avg_slippage": stats.avg_slippage,
            "updated_at": stats.updated_at.isoformat()
        }
