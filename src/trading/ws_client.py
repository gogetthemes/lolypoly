"""WebSocket client for real-time trade monitoring"""

import asyncio
import websockets
import json
from typing import Callable, Optional, Dict, Any
from datetime import datetime
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger("ws_client")


class WebSocketClient:
    """WebSocket client for Pooymarket"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_url = settings.POOYMARKET_WS_URL
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = settings.WS_RECONNECT_ATTEMPTS
        self.reconnect_delay = settings.WS_RECONNECT_DELAY
        self.handlers: Dict[str, Callable] = {}
    
    def on_trade_update(self, handler: Callable):
        """Register handler for trade updates"""
        self.handlers['trade_update'] = handler
        return self
    
    def on_account_update(self, handler: Callable):
        """Register handler for account updates"""
        self.handlers['account_update'] = handler
        return self
    
    def on_connection(self, handler: Callable):
        """Register handler for connection"""
        self.handlers['connected'] = handler
        return self
    
    def on_disconnection(self, handler: Callable):
        """Register handler for disconnection"""
        self.handlers['disconnected'] = handler
        return self
    
    async def connect(self):
        """Connect to WebSocket"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                logger.info(f"Connecting to WebSocket ({self.reconnect_attempts + 1}/{self.max_reconnect_attempts})...")
                
                self.ws = await websockets.connect(self.ws_url)
                
                # Authenticate
                auth_message = {
                    "type": "auth",
                    "api_key": self.api_key,
                    "api_secret": self.api_secret
                }
                await self.ws.send(json.dumps(auth_message))
                
                # Wait for auth response
                response = await asyncio.wait_for(
                    self.ws.recv(), 
                    timeout=settings.WS_TIMEOUT
                )
                
                auth_response = json.loads(response)
                
                if auth_response.get("status") == "authenticated":
                    self.connected = True
                    self.reconnect_attempts = 0
                    logger.info("WebSocket connected and authenticated")
                    
                    if 'connected' in self.handlers:
                        await self._call_handler('connected')
                    
                    # Start listening
                    await self._listen()
                else:
                    logger.error("Authentication failed")
                    self.reconnect_attempts += 1
            
            except asyncio.TimeoutError:
                logger.warning("WebSocket connection timeout")
                self.reconnect_attempts += 1
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                self.reconnect_attempts += 1
            
            if self.reconnect_attempts < self.max_reconnect_attempts:
                await asyncio.sleep(self.reconnect_delay)
        
        logger.error("Max reconnect attempts reached")
    
    async def _listen(self):
        """Listen for messages"""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.connected = False
            
            if 'disconnected' in self.handlers:
                await self._call_handler('disconnected')
            
            # Try to reconnect
            if self.reconnect_attempts < self.max_reconnect_attempts:
                await asyncio.sleep(self.reconnect_delay)
                await self.connect()
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            self.connected = False
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming message"""
        message_type = data.get("type")
        
        if message_type == "trade_update":
            if 'trade_update' in self.handlers:
                await self._call_handler('trade_update', data)
        
        elif message_type == "account_update":
            if 'account_update' in self.handlers:
                await self._call_handler('account_update', data)
        
        else:
            logger.debug(f"Unknown message type: {message_type}")
    
    async def _call_handler(self, handler_name: str, data: Optional[Dict] = None):
        """Call handler safely"""
        try:
            handler = self.handlers[handler_name]
            if asyncio.iscoroutinefunction(handler):
                await handler(data) if data else await handler()
            else:
                handler(data) if data else handler()
        except Exception as e:
            logger.error(f"Error in {handler_name} handler: {e}")
    
    async def subscribe_to_symbol(self, symbol: str):
        """Subscribe to symbol updates"""
        if not self.connected or not self.ws:
            logger.warning("Not connected to WebSocket")
            return
        
        try:
            message = {
                "type": "subscribe",
                "symbol": symbol
            }
            await self.ws.send(json.dumps(message))
            logger.info(f"Subscribed to {symbol}")
        except Exception as e:
            logger.error(f"Error subscribing to {symbol}: {e}")
    
    async def unsubscribe_from_symbol(self, symbol: str):
        """Unsubscribe from symbol updates"""
        if not self.connected or not self.ws:
            logger.warning("Not connected to WebSocket")
            return
        
        try:
            message = {
                "type": "unsubscribe",
                "symbol": symbol
            }
            await self.ws.send(json.dumps(message))
            logger.info(f"Unsubscribed from {symbol}")
        except Exception as e:
            logger.error(f"Error unsubscribing from {symbol}: {e}")
    
    async def disconnect(self):
        """Disconnect WebSocket"""
        if self.ws:
            await self.ws.close()
        self.connected = False
        logger.info("WebSocket disconnected")
