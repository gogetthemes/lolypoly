"""API routes"""

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from src.api.schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
    StrategyCreate, StrategyUpdate, StrategyResponse,
    TradeResponse, AccountStatsResponse, StatusResponse
)
from src.accounts.manager import AccountManager
from src.strategies.manager import StrategyManager
from src.trading.copier import TradeCopier
from src.analytics.stats import StatsCalculator
from src.database.database import get_db
from src.config import settings
from src import __version__
from src.utils.logger import get_logger

logger = get_logger("api")

app = FastAPI(
    title="LolyPoly Trading Bot API",
    description="API for managing trading accounts, strategies and analytics",
    version=__version__
)


# Dependencies
def get_account_manager(db: Session = Depends(get_db)) -> AccountManager:
    return AccountManager(db)


def get_strategy_manager(db: Session = Depends(get_db)) -> StrategyManager:
    return StrategyManager(db)


def get_trade_copier(db: Session = Depends(get_db)) -> TradeCopier:
    return TradeCopier(db)


def get_stats_calculator(db: Session = Depends(get_db)) -> StatsCalculator:
    return StatsCalculator(db)


# Account Endpoints
@app.get("/api/accounts", response_model=List[AccountResponse])
async def list_accounts(
    account_manager: AccountManager = Depends(get_account_manager),
    enabled_only: bool = Query(False)
):
    """List all accounts"""
    accounts = account_manager.list_accounts(enabled_only=enabled_only)
    return accounts


@app.post("/api/accounts", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    account_manager: AccountManager = Depends(get_account_manager)
):
    """Create new account"""
    try:
        created_account = account_manager.create_account(
            name=account.name,
            api_key=account.api_key,
            api_secret=account.api_secret,
            account_type=account.account_type,
            enabled=account.enabled
        )
        return created_account
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    account_manager: AccountManager = Depends(get_account_manager)
):
    """Get account by ID"""
    account = account_manager.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.put("/api/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    account_update: AccountUpdate,
    account_manager: AccountManager = Depends(get_account_manager)
):
    """Update account"""
    updated_account = account_manager.update_account(
        account_id,
        **account_update.dict(exclude_unset=True)
    )
    if not updated_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated_account


@app.delete("/api/accounts/{account_id}")
async def delete_account(
    account_id: str,
    account_manager: AccountManager = Depends(get_account_manager)
):
    """Delete account"""
    if not account_manager.delete_account(account_id):
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted"}


# Strategy Endpoints
@app.get("/api/strategies", response_model=List[StrategyResponse])
async def list_strategies(
    strategy_manager: StrategyManager = Depends(get_strategy_manager),
    enabled_only: bool = Query(False)
):
    """List all strategies"""
    strategies = strategy_manager.list_strategies(enabled_only=enabled_only)
    return strategies


@app.post("/api/strategies", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """Create new strategy"""
    try:
        created_strategy = strategy_manager.create_strategy(
            name=strategy.name,
            source_account_id=strategy.source_account_id,
            target_accounts=strategy.target_accounts,
            copy_mode=strategy.copy_mode,
            filters=strategy.filters,
            enabled=strategy.enabled
        )
        return created_strategy
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """Get strategy by ID"""
    strategy = strategy_manager.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@app.put("/api/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: str,
    strategy_update: StrategyUpdate,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """Update strategy"""
    updated_strategy = strategy_manager.update_strategy(
        strategy_id,
        **strategy_update.dict(exclude_unset=True)
    )
    if not updated_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return updated_strategy


@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """Delete strategy"""
    if not strategy_manager.delete_strategy(strategy_id):
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy deleted"}


# Statistics Endpoints
@app.get("/api/trades/stats", response_model=List[AccountStatsResponse])
async def get_all_stats(
    stats_calculator: StatsCalculator = Depends(get_stats_calculator)
):
    """Get statistics for all accounts"""
    stats_list = stats_calculator.get_all_accounts_stats()
    return stats_list


@app.get("/api/trades/stats/{account_id}", response_model=AccountStatsResponse)
async def get_account_stats(
    account_id: str,
    stats_calculator: StatsCalculator = Depends(get_stats_calculator)
):
    """Get statistics for account"""
    stats = stats_calculator.get_account_stats(account_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Account not found")
    return stats


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get bot status"""
    return {
        "status": "running",
        "running": True,
        "timestamp": datetime.utcnow(),
        "version": __version__
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
