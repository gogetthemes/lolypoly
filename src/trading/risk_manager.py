"""Risk management module"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import Trade
from src.utils.logger import get_logger

logger = get_logger("risk_manager")


class RiskManager:
    """Manage trading risks and limits"""
    
    def __init__(self, db: Session, config: Dict[str, Any]):
        self.db = db
        self.max_daily_loss = config.get("max_daily_loss", 1000.0)  # USD
        self.max_trade_size = config.get("max_trade_size", 500.0)  # USD
        self.max_position_size = config.get("max_position_size", 5000.0)  # USD
        self.max_leverage = config.get("max_leverage", 1.0)
        self.max_daily_trades = config.get("max_daily_trades", 100)
        self.enable_circuit_breaker = config.get("enable_circuit_breaker", True)
        self.circuit_breaker_loss = config.get("circuit_breaker_loss", 5000.0)  # USD
    
    def check_trade_allowed(self, trade_data: Dict[str, Any], account_id: str) -> tuple[bool, str]:
        """
        Check if trade is allowed based on risk rules
        Returns: (is_allowed, reason)
        """
        # Check trade size
        trade_amount = trade_data.get("amount", 0)
        if trade_amount > self.max_trade_size:
            reason = f"Trade size {trade_amount} exceeds max {self.max_trade_size}"
            logger.warning(f"Trade rejected: {reason}")
            return False, reason
        
        # Check daily loss limit
        daily_loss = self._get_daily_loss(account_id)
        if daily_loss >= self.max_daily_loss:
            reason = f"Daily loss limit {self.max_daily_loss} reached. Current: {daily_loss}"
            logger.warning(f"Trade rejected: {reason}")
            return False, reason
        
        # Check daily trade count
        daily_trades = self._get_daily_trade_count(account_id)
        if daily_trades >= self.max_daily_trades:
            reason = f"Daily trade limit {self.max_daily_trades} reached"
            logger.warning(f"Trade rejected: {reason}")
            return False, reason
        
        # Check circuit breaker
        if self.enable_circuit_breaker:
            total_loss = self._get_total_loss(account_id)
            if total_loss >= self.circuit_breaker_loss:
                reason = f"Circuit breaker triggered. Total loss: {total_loss} >= {self.circuit_breaker_loss}"
                logger.warning(f"Trade rejected: {reason}")
                return False, reason
        
        # Check position size
        position_value = self._get_position_value(account_id)
        new_position = position_value + trade_amount
        if new_position > self.max_position_size:
            reason = f"Position size {new_position} would exceed max {self.max_position_size}"
            logger.warning(f"Trade rejected: {reason}")
            return False, reason
        
        logger.info(f"Trade allowed for account {account_id}")
        return True, "OK"
    
    def _get_daily_loss(self, account_id: str) -> float:
        """Get total loss for today"""
        today = datetime.utcnow().date()
        trades = self.db.query(Trade).filter(
            Trade.source_account_id == account_id,
            Trade.created_at >= datetime.combine(today, datetime.min.time()),
            Trade.status == "completed",
            Trade.actual_price < Trade.original_price
        ).all()
        
        total_loss = 0.0
        for trade in trades:
            if trade.actual_price and trade.original_price and trade.copied_amount:
                loss = (trade.original_price - trade.actual_price) * trade.copied_amount
                total_loss += loss
        
        return total_loss
    
    def _get_total_loss(self, account_id: str) -> float:
        """Get total loss ever"""
        trades = self.db.query(Trade).filter(
            Trade.source_account_id == account_id,
            Trade.status == "completed",
            Trade.actual_price < Trade.original_price
        ).all()
        
        total_loss = 0.0
        for trade in trades:
            if trade.actual_price and trade.original_price and trade.copied_amount:
                loss = (trade.original_price - trade.actual_price) * trade.copied_amount
                total_loss += loss
        
        return total_loss
    
    def _get_daily_trade_count(self, account_id: str) -> int:
        """Get number of trades today"""
        today = datetime.utcnow().date()
        count = self.db.query(Trade).filter(
            Trade.source_account_id == account_id,
            Trade.created_at >= datetime.combine(today, datetime.min.time())
        ).count()
        
        return count
    
    def _get_position_value(self, account_id: str) -> float:
        """Get current position value"""
        trades = self.db.query(Trade).filter(
            Trade.target_account_id == account_id,
            Trade.status == "completed",
            Trade.closed_at == None
        ).all()
        
        position_value = 0.0
        for trade in trades:
            if trade.actual_price and trade.copied_amount:
                position_value += trade.actual_price * trade.copied_amount
        
        return position_value
    
    def get_account_limits(self, account_id: str) -> Dict[str, Any]:
        """Get current limits for account"""
        daily_loss = self._get_daily_loss(account_id)
        total_loss = self._get_total_loss(account_id)
        daily_trades = self._get_daily_trade_count(account_id)
        position_value = self._get_position_value(account_id)
        
        return {
            "max_daily_loss": self.max_daily_loss,
            "current_daily_loss": daily_loss,
            "daily_loss_remaining": max(0, self.max_daily_loss - daily_loss),
            
            "max_trade_size": self.max_trade_size,
            
            "max_position_size": self.max_position_size,
            "current_position_size": position_value,
            "position_available": max(0, self.max_position_size - position_value),
            
            "max_daily_trades": self.max_daily_trades,
            "current_daily_trades": daily_trades,
            "trades_remaining": max(0, self.max_daily_trades - daily_trades),
            
            "circuit_breaker_enabled": self.enable_circuit_breaker,
            "circuit_breaker_limit": self.circuit_breaker_loss,
            "total_loss": total_loss,
            "circuit_breaker_triggered": total_loss >= self.circuit_breaker_loss if self.enable_circuit_breaker else False
        }
