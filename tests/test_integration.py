"""Integration tests for Pooymarket API and WebSocket client"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.trading.pooymarket_api import PooymarketAPI
from src.trading.ws_client import WebSocketClient
from src.config import settings
from src.security.encryption import encrypt_credential


@pytest.mark.asyncio
async def test_pooymarket_api_headers_decryption():
    """Test that API client decrypts credentials correctly and crafts headers"""
    enc_key = encrypt_credential("real_api_key_secure")
    enc_secret = encrypt_credential("real_api_secret_secure")
    
    api = PooymarketAPI(enc_key, enc_secret)
    headers = api._get_headers()
    
    assert headers["Authorization"] == "Bearer real_api_key_secure"
    assert headers["X-Pooymarket-Secret"] == "real_api_secret_secure"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_pooymarket_api_testnet_override():
    """Test that setting POOYMARKET_TESTNET switches base URL correctly"""
    with patch.object(settings, 'POOYMARKET_TESTNET', True):
        api = PooymarketAPI("key", "secret")
        # Assuming defaults are standard
        if settings.POOYMARKET_API_BASE_URL == "https://api.pooymarket.com":
            assert api.base_url == "https://testnet.api.pooymarket.com"


@pytest.mark.asyncio
async def test_create_trade_success():
    """Test creating trade endpoint integration flow"""
    api = PooymarketAPI("key", "secret")
    
    mock_resp = AsyncMock()
    mock_resp.status = 201
    mock_resp.json.return_value = {"id": "trade_mock_99", "price": 100.5}
    
    mock_session = MagicMock()
    mock_session.post.return_value.__aenter__.return_value = mock_resp
    api.session = mock_session
    
    result = await api.create_trade("BTC/USD", "BUY", 0.5, 100.0)
    assert result is not None
    assert result["id"] == "trade_mock_99"
    assert result["price"] == 100.5


@pytest.mark.asyncio
async def test_websocket_client_init():
    """Test initializing real WebSocket monitoring client"""
    ws = WebSocketClient("ws_key", "ws_secret")
    assert ws.connected == False
    assert ws.ws is None
