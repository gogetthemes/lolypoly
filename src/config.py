"""Configuration settings"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/lolypoly"
    )
    
    # Pooymarket API Configuration
    POOYMARKET_API_BASE_URL: str = os.getenv(
        "POOYMARKET_API_BASE_URL",
        "https://api.pooymarket.com"
    )
    POOYMARKET_WS_URL: str = os.getenv(
        "POOYMARKET_WS_URL",
        "wss://ws.pooymarket.com"
    )
    
    # WebSocket Configuration
    WS_TIMEOUT: int = int(os.getenv("WS_TIMEOUT", "10"))
    WS_RECONNECT_ATTEMPTS: int = int(os.getenv("WS_RECONNECT_ATTEMPTS", "5"))
    WS_RECONNECT_DELAY: int = int(os.getenv("WS_RECONNECT_DELAY", "5"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/bot.log")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
