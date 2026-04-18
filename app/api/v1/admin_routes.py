"""
Admin API endpoints for API key management.

Provides endpoints to:
- POST /keys: Generate a new API key
- GET /keys: List all API keys
- DELETE /keys/{key_id}: Revoke an API key

Requires X-Admin-Key header for authentication.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from loguru import logger
from pydantic import BaseModel

from app.core.config import settings
from app.db.database import get_db
from app.db.models import APIKey
from app.services.api_key_service import api_key_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


async def verify_admin(admin_key: str = Header(..., alias="X-Admin-Key")) -> str:
    """
    Dependency to verify admin access via X-Admin-Key header.

    Compares against ADMIN_API_KEY from .env. Raises 401 if invalid.
    """
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin API key not configured on server",
        )

    if admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key",
        )
    return admin_key


class KeyGenerateRequest(BaseModel):
    name: str | None = None


class KeyResponse(BaseModel):
    key: str


class KeyInfo(BaseModel):
    id: str
    name: str | None
    is_active: bool
    created_at: str
    last_used_at: str | None


class KeyListResponse(BaseModel):
    keys: list[KeyInfo]


@router.post("/keys", response_model=KeyResponse)
async def generate_key(
    payload: KeyGenerateRequest,
    _: str = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
) -> KeyResponse:
    """
    Generate a new API key.

    Requires X-Admin-Key header.
    Returns the plaintext key (shown only once).
    """
    plain_key = await api_key_service.generate_key(db, name=payload.name)
    logger.info(f"API key generated: name={payload.name}")
    return KeyResponse(key=plain_key)


@router.get("/keys", response_model=KeyListResponse)
async def list_keys(
    _: str = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
) -> KeyListResponse:
    """
    List all API keys (without plaintext).

    Requires X-Admin-Key header.
    """
    keys = await api_key_service.list_keys(db)
    key_infos = [
        KeyInfo(
            id=key.id,
            name=key.name,
            is_active=key.is_active,
            created_at=key.created_at.isoformat() if key.created_at else None,
            last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
        )
        for key in keys
    ]
    return KeyListResponse(keys=key_infos)


@router.delete("/keys/{key_id}")
async def revoke_key(
    key_id: str,
    _: str = Depends(verify_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Revoke (deactivate) an API key by ID.

    Requires X-Admin-Key header.
    """
    success = await api_key_service.revoke_key(db, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    return {"detail": "API key revoked"}
