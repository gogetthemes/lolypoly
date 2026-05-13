"""Pydantic schemas for API"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Account Schemas
class AccountCreate(BaseModel):
    name: str
    api_key: str
    api_secret: str
    account_type: str = "source"
    enabled: bool = True


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None
    enabled: Optional[bool] = None


class AccountResponse(BaseModel):
    id: str
    name: str
    account_type: str
    enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Strategy Schemas
class StrategyCreate(BaseModel):
    name: str
    source_account_id: str
    target_accounts: List[str]
    copy_mode: str = "full"
    filters: Dict[str, Any] = {}
    enabled: bool = True


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    copy_mode: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class StrategyResponse(BaseModel):
    id: str
    name: str
    source_account_id: str
    target_accounts: List[str]
    copy_mode: str
    filters: Dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Trade Schemas
class TradeResponse(BaseModel):
    id: str
    strategy_id: Optional[str]
    source_account_id: str
    target_account_id: Optional[str]
    symbol: str
    trade_type: str
    original_amount: float
    copied_amount: Optional[float]
    original_price: float
    actual_price: Optional[float]
    status: str
    source_opened_at: datetime
    copied_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Stats Schemas
class AccountStatsResponse(BaseModel):
    account_id: str
    account_name: str
    total_trades: int
    successful_trades: int
    failed_trades: int
    win_rate: str
    total_profit: float
    avg_slippage: str
    updated_at: str


class TradeStatsRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Status Schemas
class StatusResponse(BaseModel):
    status: str
    running: bool
    timestamp: datetime
    version: str
