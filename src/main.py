"""Main bot application"""

import asyncio
import uvicorn
from src.config import settings
from src.database.database import init_db
from src.api.routes import app
from src.utils.logger import get_logger

logger = get_logger("main")


async def startup():
    """Initialize application"""
    logger.info("Starting LolyPoly Trading Bot...")
    init_db()
    logger.info("Database initialized")


async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down LolyPoly Trading Bot...")


def main():
    """Main entry point"""
    logger.info(f"Starting API server on {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Run startup
    asyncio.run(startup())
    
    # Run API server
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info" if not settings.DEBUG else "debug"
    )


if __name__ == "__main__":
    main()
