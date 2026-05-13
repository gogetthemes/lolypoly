"""Pooymarket API client"""

import aiohttp
import json
from typing import Optional, Dict, Any
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("pooymarket_api")


class PooymarketAPI:
    """Pooymarket API client"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = settings.POOYMARKET_API_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information"""
        try:
            url = f"{self.base_url}/account"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Error getting account info: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Exception in get_account_info: {e}")
            return None
    
    async def get_open_trades(self) -> Optional[Dict[str, Any]]:
        """Get open trades"""
        try:
            url = f"{self.base_url}/trades/open"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Error getting open trades: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Exception in get_open_trades: {e}")
            return None
    
    async def get_trade_history(self, limit: int = 100, offset: int = 0) -> Optional[Dict[str, Any]]:
        """Get trade history"""
        try:
            url = f"{self.base_url}/trades/history?limit={limit}&offset={offset}"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Error getting trade history: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Exception in get_trade_history: {e}")
            return None
    
    async def create_trade(self, symbol: str, trade_type: str, amount: float,
                          price: float, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new trade"""
        try:
            url = f"{self.base_url}/trades/create"
            payload = {
                "symbol": symbol,
                "type": trade_type,
                "amount": amount,
                "price": price,
                **kwargs
            }
            async with self.session.post(url, json=payload, headers=self._get_headers()) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    logger.error(f"Error creating trade: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Exception in create_trade: {e}")
            return None
    
    async def close_trade(self, trade_id: str) -> bool:
        """Close a trade"""
        try:
            url = f"{self.base_url}/trades/{trade_id}/close"
            async with self.session.post(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    logger.info(f"Trade closed: {trade_id}")
                    return True
                else:
                    logger.error(f"Error closing trade: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Exception in close_trade: {e}")
            return False
    
    async def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get market data for symbol"""
        try:
            url = f"{self.base_url}/market/{symbol}"
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Error getting market data for {symbol}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Exception in get_market_data: {e}")
            return None
