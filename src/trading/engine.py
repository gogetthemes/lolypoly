"""Trading engine to orchestrate automatic trade copying"""

import asyncio
from typing import Dict, List
from sqlalchemy.orm import Session
from src.database.database import SessionLocal
from src.database.models import Account, AccountType
from src.trading.ws_client import WebSocketClient
from src.trading.copier import TradeCopier
from src.strategies.manager import StrategyManager
from src.utils.logger import get_logger

logger = get_logger("engine")


class TradingEngine:
    """Orchestrates automatic trade copying across all active accounts"""
    
    def __init__(self):
        self.clients: Dict[str, WebSocketClient] = {}
        self.running = False
        self._tasks: List[asyncio.Task] = []
    
    async def start(self):
        """Start monitoring all enabled source accounts"""
        if self.running:
            logger.warning("Trading engine is already running")
            return
            
        self.running = True
        logger.info("Starting Trading Engine...")
        
        # We need a new DB session to fetch accounts
        db = SessionLocal()
        try:
            # Find all enabled accounts that can be sources
            source_accounts = db.query(Account).filter(
                Account.enabled == True,
                Account.account_type.in_([AccountType.SOURCE, AccountType.BOTH])
            ).all()
            
            logger.info(f"Found {len(source_accounts)} active source accounts to monitor")
            
            for account in source_accounts:
                await self._start_monitoring(account.id, account.api_key, account.api_secret)
                
        finally:
            db.close()
            
    async def stop(self):
        """Stop all monitoring tasks"""
        self.running = False
        logger.info("Stopping Trading Engine...")
        
        for account_id, client in self.clients.items():
            # Assuming ws_client has a disconnect or we just let tasks cancel
            logger.info(f"Disconnecting client for account {account_id}")
            # The connect() loop in ws_client.py usually handles reconnects, 
            # we need a way to break it. 
            # For now, we will cancel the tasks.
            
        for task in self._tasks:
            task.cancel()
            
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            
        self.clients.clear()
        self._tasks.clear()
        logger.info("Trading Engine stopped")

    async def _start_monitoring(self, account_id: str, api_key: str, api_secret: str):
        """Start a WebSocket client for a specific account"""
        if account_id in self.clients:
            return
            
        client = WebSocketClient(api_key, api_secret)
        
        # Register the automatic copy handler
        client.on_trade_update(lambda data: self._handle_trade_event(account_id, data))
        
        self.clients[account_id] = client
        
        # Run the connection in a background task
        task = asyncio.create_task(client.connect())
        self._tasks.append(task)
        logger.info(f"Started monitoring task for account {account_id}")

    def _handle_trade_event(self, source_account_id: str, trade_data: Dict):
        """Callback triggered when a new trade is detected on a source account"""
        logger.info(f"New trade event detected on account {source_account_id}: {trade_data.get('symbol')}")
        
        # Create a background task to handle the copy logic (non-blocking for WS)
        asyncio.create_task(self._process_copy(source_account_id, trade_data))

    async def _process_copy(self, source_account_id: str, trade_data: Dict):
        """Find strategies and execute copies"""
        db = SessionLocal()
        try:
            strategy_manager = StrategyManager(db)
            copier = TradeCopier(db)
            
            # Find all active strategies for this source
            strategies = strategy_manager.list_strategies(enabled_only=True)
            active_strategies = [s for s in strategies if s.source_account_id == source_account_id]
            
            if not active_strategies:
                logger.debug(f"No active strategies found for account {source_account_id}")
                return
                
            for strategy in active_strategies:
                try:
                    logger.info(f"Processing strategy '{strategy.name}' for event on {source_account_id}")
                    await copier.copy_trade(strategy, trade_data)
                except Exception as e:
                    logger.error(f"Error copying trade for strategy {strategy.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in _process_copy for account {source_account_id}: {e}")
        finally:
            db.close()
