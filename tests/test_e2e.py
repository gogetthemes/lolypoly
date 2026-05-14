"""E2E flow tests for trading bot lifecycle"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.accounts.manager import AccountManager
from src.strategies.manager import StrategyManager
from src.trading.copier import TradeCopier
from src.trading.risk_manager import RiskManager
from src.security.two_factor_auth import TwoFactorAuthManager


@pytest.mark.asyncio
async def test_full_trade_copy_lifecycle(db_session):
    """Test full e2e flow: setup accounts, strategies, copy trade with risk check"""
    acc_manager = AccountManager(db_session)
    strat_manager = StrategyManager(db_session)
    
    # 1. Create Source and Target accounts
    source_acc = acc_manager.create_account(
        name="E2E Source",
        api_key="src_key_secure_12345",
        api_secret="src_secret",
        account_type="source"
    )
    
    target_acc = acc_manager.create_account(
        name="E2E Target",
        api_key="tgt_key_secure_67890",
        api_secret="tgt_secret",
        account_type="target"
    )
    
    # 2. Create Strategy mapping
    strategy = strat_manager.create_strategy(
        name="E2E Strategy",
        source_account_id=source_acc.id,
        target_accounts=[target_acc.id],
        copy_mode="full",
        filters={"min_amount": 0.01}
    )
    
    # 3. Trigger trade copy flow via TradeCopier
    copier = TradeCopier(db_session)
    
    # Mock PooymarketAPI create_trade execution
    mock_api_instance = AsyncMock()
    mock_api_instance.create_trade.return_value = {"id": "live_exec_101", "price": 50000.0}
    
    source_trade_data = {
        "id": "src_trade_777",
        "symbol": "BTC/USD",
        "type": "BUY",
        "amount": 0.05,
        "price": 49950.0
    }
    
    with patch("src.trading.copier.PooymarketAPI", return_value=mock_api_instance):
        mock_api_instance.__aenter__.return_value = mock_api_instance
        trade_record = await copier.copy_trade(strategy, source_trade_data)
        
    assert trade_record is not None
    assert trade_record.status == "completed"
    assert trade_record.copied_amount == 0.05
    assert trade_record.actual_price == 50000.0


def test_2fa_verification_lifecycle(db_session):
    """Test 2FA generation and confirmation flow"""
    acc_manager = AccountManager(db_session)
    twofa_manager = TwoFactorAuthManager(db_session, {"enable_email_2fa": False})
    
    account = acc_manager.create_account("2FA User", "key_1234567890", "secret")
    
    # Generate code
    success, msg = twofa_manager.generate_code(account.id, "trade_execution", "user@example.com")
    assert success is True
    
    # Retrieve the raw code directly from DB for test verification
    from src.security.two_factor_auth import TwoFactorAuth
    auth_record = db_session.query(TwoFactorAuth).filter_by(account_id=account.id).first()
    assert auth_record is not None
    
    # Verify valid code
    v_success, v_msg = twofa_manager.verify_code(account.id, "trade_execution", auth_record.code)
    assert v_success is True
    assert auth_record.verified == 1
