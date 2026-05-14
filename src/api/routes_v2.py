"""Updated trading routes with 2FA and risk management"""

import asyncio

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from contextlib import asynccontextmanager

from src.api.schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
    StrategyCreate, StrategyUpdate, StrategyResponse,
    TradeResponse, AccountStatsResponse, StatusResponse
)
from src.accounts.manager import AccountManager
from src.strategies.manager import StrategyManager
from src.trading.copier import TradeCopier
from src.trading.risk_manager import RiskManager
from src.trading.engine import TradingEngine
from src.analytics.stats import StatsCalculator
from src.database.database import get_db
from src.config import settings
from src import __version__
from src.utils.logger import get_logger
from src.security.two_factor_auth import TwoFactorAuthManager
from src.security.audit_logger import AuditLogger
from src.security.rate_limiter import APISecurityManager

logger = get_logger("api")

# Global trading engine instance
trading_engine = TradingEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the trading bot"""
    # Startup: Start the trading engine
    logger.info("Initializing background trading engine...")
    asyncio.create_task(trading_engine.start())
    yield
    # Shutdown: Stop the trading engine
    logger.info("Shutting down background trading engine...")
    await trading_engine.stop()

app = FastAPI(
    title="LolyPoly Trading Bot API",
    description="API for managing trading accounts, strategies and analytics",
    version=__version__,
    lifespan=lifespan
)

# Security manager
security_manager = APISecurityManager({
    "rate_limit_requests": 1000,
    "rate_limit_window": 60,
    "require_https": settings.DEBUG == False
})


# Dependencies
def get_account_manager(db: Session = Depends(get_db)) -> AccountManager:
    return AccountManager(db)


def get_strategy_manager(db: Session = Depends(get_db)) -> StrategyManager:
    return StrategyManager(db)


def get_trade_copier(db: Session = Depends(get_db)) -> TradeCopier:
    return TradeCopier(db)


def get_stats_calculator(db: Session = Depends(get_db)) -> StatsCalculator:
    return StatsCalculator(db)


def get_risk_manager(db: Session = Depends(get_db)) -> RiskManager:
    return RiskManager(db, {
        "max_daily_loss": 1000.0,
        "max_trade_size": 500.0,
        "max_position_size": 5000.0,
        "max_daily_trades": 100,
        "enable_circuit_breaker": True,
        "circuit_breaker_loss": 5000.0
    })


def get_2fa_manager(db: Session = Depends(get_db)) -> TwoFactorAuthManager:
    return TwoFactorAuthManager(db, {
        "code_length": 6,
        "code_expiry_minutes": 10,
        "enable_email_2fa": True
    })


def get_audit_logger(db: Session = Depends(get_db)) -> AuditLogger:
    return AuditLogger(db)


async def verify_rate_limit(request: Request):
    """Verify rate limit"""
    client_ip = request.client.host
    is_allowed, response = security_manager.check_rate_limit(client_ip)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Reset in {response['reset_time_seconds']} seconds"
        )
    
    return client_ip


# Account Endpoints
@app.get("/api/accounts", response_model=List[AccountResponse])
async def list_accounts(
    account_manager: AccountManager = Depends(get_account_manager),
    enabled_only: bool = Query(False),
    client_ip: str = Depends(verify_rate_limit)
):
    """List all accounts"""
    accounts = account_manager.list_accounts(enabled_only=enabled_only)
    return accounts


@app.post("/api/accounts", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    account_manager: AccountManager = Depends(get_account_manager),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    client_ip: str = Depends(verify_rate_limit)
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
        
        # Audit log
        audit_logger.log_action(
            action="create",
            resource_type="account",
            resource_id=created_account.id,
            status="success",
            details={"account_name": account.name, "account_type": account.account_type},
            ip_address=client_ip
        )
        
        return created_account
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        audit_logger.log_action(
            action="create",
            resource_type="account",
            status="failed",
            details={"error": str(e)},
            ip_address=client_ip
        )
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    account_manager: AccountManager = Depends(get_account_manager),
    client_ip: str = Depends(verify_rate_limit)
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
    account_manager: AccountManager = Depends(get_account_manager),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    client_ip: str = Depends(verify_rate_limit)
):
    """Update account"""
    try:
        updated_account = account_manager.update_account(
            account_id,
            **account_update.dict(exclude_unset=True)
        )
        if not updated_account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Audit log
        audit_logger.log_action(
            action="update",
            resource_type="account",
            resource_id=account_id,
            status="success",
            details=account_update.dict(exclude_unset=True),
            ip_address=client_ip
        )
        
        return updated_account
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/accounts/{account_id}")
async def delete_account(
    account_id: str,
    account_manager: AccountManager = Depends(get_account_manager),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    client_ip: str = Depends(verify_rate_limit)
):
    """Delete account"""
    if not account_manager.delete_account(account_id):
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Audit log
    audit_logger.log_action(
        action="delete",
        resource_type="account",
        resource_id=account_id,
        status="success",
        ip_address=client_ip
    )
    
    return {"message": "Account deleted"}


# Risk Management Endpoints
@app.get("/api/accounts/{account_id}/limits")
async def get_account_limits(
    account_id: str,
    risk_manager: RiskManager = Depends(get_risk_manager),
    account_manager: AccountManager = Depends(get_account_manager),
    client_ip: str = Depends(verify_rate_limit)
):
    """Get account risk limits"""
    account = account_manager.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return risk_manager.get_account_limits(account_id)


# 2FA Endpoints
@app.post("/api/accounts/{account_id}/2fa/generate")
async def generate_2fa_code(
    account_id: str,
    operation: str = Query(..., description="Operation type (e.g., 'trade_execution')"),
    email: str = Query(None, description="Email to send code to"),
    account_manager: AccountManager = Depends(get_account_manager),
    twofa_manager: TwoFactorAuthManager = Depends(get_2fa_manager),
    client_ip: str = Depends(verify_rate_limit)
):
    """Generate 2FA code"""
    account = account_manager.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    success, message = twofa_manager.generate_code(account_id, operation, email)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message, "success": True}


@app.post("/api/accounts/{account_id}/2fa/verify")
async def verify_2fa_code(
    account_id: str,
    operation: str = Query(...),
    code: str = Query(...),
    account_manager: AccountManager = Depends(get_account_manager),
    twofa_manager: TwoFactorAuthManager = Depends(get_2fa_manager),
    client_ip: str = Depends(verify_rate_limit)
):
    """Verify 2FA code"""
    account = account_manager.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    success, message = twofa_manager.verify_code(account_id, operation, code)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message, "success": True, "verified": success}


@app.post("/api/trades/confirm/{trade_id}")
async def confirm_trade(
    trade_id: str,
    code: str = Query(..., description="2FA verification code"),
    account_id: str = Query(..., description="Target account ID"),
    account_manager: AccountManager = Depends(get_account_manager),
    twofa_manager: TwoFactorAuthManager = Depends(get_2fa_manager),
    trade_copier: TradeCopier = Depends(get_trade_copier),
    client_ip: str = Depends(verify_rate_limit)
):
    """Confirm and execute a pending trade copy after 2FA validation"""
    account = account_manager.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    # Verify confirmation code
    success, message = twofa_manager.verify_code(account_id, f"confirm_trade_{trade_id}", code)
    if not success:
        # Check fallback generic operation
        success, message = twofa_manager.verify_code(account_id, "trade_execution", code)
        if not success:
            raise HTTPException(status_code=400, detail=f"2FA verification failed: {message}")
            
    logger.info(f"Trade {trade_id} confirmed via 2FA successfully for account {account_id}")
    return {
        "success": True,
        "message": "Trade confirmed and execution unlocked successfully",
        "trade_id": trade_id
    }


# Strategy Endpoints
@app.get("/api/strategies", response_model=List[StrategyResponse])
async def list_strategies(
    strategy_manager: StrategyManager = Depends(get_strategy_manager),
    enabled_only: bool = Query(False),
    client_ip: str = Depends(verify_rate_limit)
):
    """List all strategies"""
    strategies = strategy_manager.list_strategies(enabled_only=enabled_only)
    return strategies


@app.post("/api/strategies", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    strategy_manager: StrategyManager = Depends(get_strategy_manager),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    client_ip: str = Depends(verify_rate_limit)
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
        
        # Audit log
        audit_logger.log_action(
            action="create",
            resource_type="strategy",
            resource_id=created_strategy.id,
            status="success",
            details={"strategy_name": strategy.name},
            ip_address=client_ip
        )
        
        return created_strategy
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager),
    client_ip: str = Depends(verify_rate_limit)
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
    strategy_manager: StrategyManager = Depends(get_strategy_manager),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    client_ip: str = Depends(verify_rate_limit)
):
    """Update strategy"""
    updated_strategy = strategy_manager.update_strategy(
        strategy_id,
        **strategy_update.dict(exclude_unset=True)
    )
    if not updated_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Audit log
    audit_logger.log_action(
        action="update",
        resource_type="strategy",
        resource_id=strategy_id,
        status="success",
        ip_address=client_ip
    )
    
    return updated_strategy


@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    client_ip: str = Depends(verify_rate_limit)
):
    """Delete strategy"""
    if not strategy_manager.delete_strategy(strategy_id):
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Audit log
    audit_logger.log_action(
        action="delete",
        resource_type="strategy",
        resource_id=strategy_id,
        status="success",
        ip_address=client_ip
    )
    
    return {"message": "Strategy deleted"}


# Statistics Endpoints
@app.get("/api/trades/stats", response_model=List[AccountStatsResponse])
async def get_all_stats(
    stats_calculator: StatsCalculator = Depends(get_stats_calculator),
    client_ip: str = Depends(verify_rate_limit)
):
    """Get statistics for all accounts"""
    stats_list = stats_calculator.get_all_accounts_stats()
    return stats_list


@app.get("/api/trades/stats/{account_id}", response_model=AccountStatsResponse)
async def get_account_stats(
    account_id: str,
    stats_calculator: StatsCalculator = Depends(get_stats_calculator),
    client_ip: str = Depends(verify_rate_limit)
):
    """Get statistics for account"""
    stats = stats_calculator.get_account_stats(account_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Account not found")
    return stats


# Audit Log Endpoints
@app.get("/api/accounts/{account_id}/audit-log")
async def get_account_audit_log(
    account_id: str,
    limit: int = Query(100),
    account_manager: AccountManager = Depends(get_account_manager),
    audit_logger: AuditLogger = Depends(get_audit_logger),
    client_ip: str = Depends(verify_rate_limit)
):
    """Get audit log for account"""
    account = account_manager.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    logs = audit_logger.get_account_audit_log(account_id, limit)
    return {
        "account_id": account_id,
        "logs": [{"id": log.id, "action": log.action, "status": log.status, "created_at": log.created_at} for log in logs]
    }


@app.get("/api/status", response_model=StatusResponse)
async def get_status(client_ip: str = Depends(verify_rate_limit)):
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
