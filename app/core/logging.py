import logging
import sys

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    # Remove any existing handlers
    logger.remove()
    
    # Add console formatter with simple format matching user's desired output
    logger.add(
        sys.stdout,
        format="{time:HH:mm:ss} | {level: <8} | {message}",
        level=settings.log_level.upper(),
    )
    
    # Add file logger with more detail for debugging (but still clean)
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level=settings.log_level.upper(),
    )


# Setup logging on import
setup_logging()