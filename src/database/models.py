"""Database models"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List
from sqlalchemy import Column, String, Float, DateTime, Boolean, JSON, ForeignKey, ARRAY, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AccountType(str, Enum):
    """Account type enum"""
    SOURCE = "source"
    TARGET = "target"
    BOTH = "both"


class CopyMode(str, Enum):
    """Copy mode enum"""
    FULL = "full"
    SELECTIVE = "selective"


class Account(Base):
    """Trading account model"""
    __tablename__ = "accounts"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=False)
    api_secret = Column(String(255), nullable=False)
    account_type = Column(SQLEnum(AccountType), default=AccountType.SOURCE)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    strategies = relationship("Strategy", back_populates="source_account")
    trades = relationship("Trade", back_populates="source_account")
    stats = relationship("AccountStats", uselist=False, back_populates="account")


class Strategy(Base):
    """Trading strategy model"""
    __tablename__ = "strategies"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    source_account_id = Column(String(50), ForeignKey("accounts.id"))
    target_accounts = Column(ARRAY(String), nullable=False)
    copy_mode = Column(SQLEnum(CopyMode), default=CopyMode.FULL)
    filters = Column(JSON, default={})
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    source_account = relationship("Account", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")


class Trade(Base):
    """Trade record model"""
    __tablename__ = "trades"
    
    id = Column(String(50), primary_key=True)
    strategy_id = Column(String(50), ForeignKey("strategies.id"), nullable=True)
    source_account_id = Column(String(50), ForeignKey("accounts.id"), nullable=False)
    target_account_id = Column(String(50), nullable=True)
    symbol = Column(String(20), nullable=False)
    trade_type = Column(String(20), nullable=False)
    original_amount = Column(Float, nullable=False)
    copied_amount = Column(Float, nullable=True)
    original_price = Column(Float, nullable=False)
    actual_price = Column(Float, nullable=True)
    status = Column(String(20), default="pending")
    source_opened_at = Column(DateTime, nullable=False)
    copied_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    strategy = relationship("Strategy", back_populates="trades")
    source_account = relationship("Account", back_populates="trades")


class AccountStats(Base):
    """Account statistics model"""
    __tablename__ = "account_stats"
    
    id = Column(String(50), primary_key=True)
    account_id = Column(String(50), ForeignKey("accounts.id"), unique=True)
    total_trades = Column(Float, default=0)
    successful_trades = Column(Float, default=0)
    failed_trades = Column(Float, default=0)
    total_profit = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    avg_slippage = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("Account", back_populates="stats")
