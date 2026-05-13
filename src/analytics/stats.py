"""Statistics calculation module"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.models import Trade, Account, AccountStats
from src.utils.logger import get_logger

logger = get_logger("stats")


class StatsCalculator:
    """Calculate trading statistics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def update_account_stats(self, account_id: str):
        """Update account statistics"""
        account = self.db.query(Account).filter(Account.id == account_id).first()
        
        if not account:
            logger.warning(f"Account not found: {account_id}")
            return
        
        # Get all trades for account
        trades = self.db.query(Trade).filter(
            (Trade.source_account_id == account_id) | (Trade.target_account_id == account_id)
        ).all()
        
        if not trades:
            logger.info(f"No trades found for account {account_id}")
            return
        
        # Calculate statistics
        total_trades = len(trades)
        successful_trades = len([t for t in trades if t.status == "completed"])
        failed_trades = len([t for t in trades if t.status == "failed"])
        
        win_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate profit (simplified - based on price differences)
        total_profit = 0.0
        for trade in trades:
            if trade.actual_price and trade.original_price:
                price_diff = trade.actual_price - trade.original_price
                profit = price_diff * trade.copied_amount if trade.copied_amount else 0
                total_profit += profit
        
        # Calculate average slippage
        slippages = []
        for trade in trades:
            if trade.actual_price and trade.original_price:
                slippage = ((trade.actual_price - trade.original_price) / trade.original_price) * 100
                slippages.append(slippage)
        
        avg_slippage = (sum(slippages) / len(slippages)) if slippages else 0.0
        
        # Update or create stats record
        stats = account.stats
        if stats:
            stats.total_trades = total_trades
            stats.successful_trades = successful_trades
            stats.failed_trades = failed_trades
            stats.total_profit = total_profit
            stats.win_rate = win_rate
            stats.avg_slippage = avg_slippage
            stats.updated_at = datetime.utcnow()
        else:
            from src.database.models import AccountStats
            stats = AccountStats(
                id=f"stats_{account_id}",
                account_id=account_id,
                total_trades=total_trades,
                successful_trades=successful_trades,
                failed_trades=failed_trades,
                total_profit=total_profit,
                win_rate=win_rate,
                avg_slippage=avg_slippage
            )
            self.db.add(stats)
        
        self.db.commit()
        logger.info(f"Stats updated for account {account_id}")
    
    def get_account_stats(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account statistics"""
        account = self.db.query(Account).filter(Account.id == account_id).first()
        
        if not account or not account.stats:
            return None
        
        stats = account.stats
        return {
            "account_id": account_id,
            "account_name": account.name,
            "total_trades": stats.total_trades,
            "successful_trades": stats.successful_trades,
            "failed_trades": stats.failed_trades,
            "win_rate": f"{stats.win_rate:.2f}%",
            "total_profit": stats.total_profit,
            "avg_slippage": f"{stats.avg_slippage:.4f}%",
            "updated_at": stats.updated_at.isoformat()
        }
    
    def get_all_accounts_stats(self) -> list:
        """Get statistics for all accounts"""
        accounts = self.db.query(Account).all()
        stats_list = []
        
        for account in accounts:
            stats = self.get_account_stats(account.id)
            if stats:
                stats_list.append(stats)
        
        return stats_list
    
    def get_trades_in_period(self, account_id: str, 
                            start_date: datetime, end_date: datetime) -> list:
        """Get trades in specific period"""
        trades = self.db.query(Trade).filter(
            (Trade.source_account_id == account_id) | (Trade.target_account_id == account_id),
            Trade.created_at >= start_date,
            Trade.created_at <= end_date
        ).all()
        
        return trades
    
    def get_daily_stats(self, account_id: str) -> Dict[str, Dict[str, Any]]:
        """Get daily statistics for account"""
        start_date = datetime.utcnow() - timedelta(days=30)
        
        trades = self.db.query(Trade).filter(
            (Trade.source_account_id == account_id) | (Trade.target_account_id == account_id),
            Trade.created_at >= start_date
        ).all()
        
        daily_stats = {}
        
        for trade in trades:
            date_key = trade.created_at.date().isoformat()
            
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "profit": 0.0
                }
            
            daily_stats[date_key]["total"] += 1
            
            if trade.status == "completed":
                daily_stats[date_key]["successful"] += 1
            elif trade.status == "failed":
                daily_stats[date_key]["failed"] += 1
            
            # Add profit
            if trade.actual_price and trade.original_price:
                profit = (trade.actual_price - trade.original_price) * trade.copied_amount
                daily_stats[date_key]["profit"] += profit
        
        return daily_stats
