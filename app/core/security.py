"""
Authentication and security utilities.

Provides API key validation via X-API-Key header, supporting both:
- Static API key from configuration
- Database-stored API keys
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from loguru import logger

from app.core.config import settings
from app.db.database import get_db
from app.services.api_key_service import api_key_service
from sqlalchemy.ext.asyncio import AsyncSession

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Validate the API key from the X-API-Key header.

    Checks both:
    1. Static .env API_KEY (backward compatible)
    2. Database-stored API keys (generated via admin endpoint)

    Raises 401 if key is missing or invalid.
    """
    if not api_key:
        logger.warning("[Auth] Request rejected — missing X-API-Key header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    # First, check static config key (backward compatible)
    if settings.api_key and api_key == settings.api_key:
        logger.debug("[Auth] Authenticated via static config key")
        return api_key

    # Second, check database keys
    if await api_key_service.verify_key(db, api_key):
        logger.debug("[Auth] Authenticated via database key")
        return api_key

    logger.warning(f"[Auth] Request rejected — invalid API key (prefix: {api_key[:6]}...)")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )
