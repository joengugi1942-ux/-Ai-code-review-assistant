"""
API key service for managing API keys.

Provides methods to generate, verify, list, and revoke API keys.
"""

import secrets
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import APIKey


class APIKeyService:
    """Service for managing API keys (generate, verify, revoke)."""

    async def generate_key(self, db: AsyncSession, name: str | None = None) -> str:
        """
        Generate a new API key.

        Returns the plain text key (shown once). The key is stored hashed in the DB.
        """
        # Generate a random 32-character hex key
        plain_key = secrets.token_hex(16)  # 32 hex chars

        key_hash = APIKey.generate_key(plain_key)
        key_id = str(uuid.uuid4())

        api_key = APIKey(
            id=key_id,
            key_hash=key_hash,
            name=name,
            is_active=True,
            created_at=datetime.utcnow(),
            last_used_at=None,
        )
        db.add(api_key)
        await db.commit()

        return plain_key

    async def verify_key(self, db: AsyncSession, plain_key: str) -> bool:
        """
        Verify if a plain API key is valid (exists and is active).
        Updates last_used_at on successful verification.
        """
        key_hash = APIKey.generate_key(plain_key)

        stmt = select(APIKey).where(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True,
        )
        result = await db.execute(stmt)
        api_key = result.scalar_one_or_none()

        if api_key:
            # Update last_used_at
            api_key.last_used_at = datetime.utcnow()
            await db.commit()
            return True

        return False

    async def list_keys(self, db: AsyncSession) -> list[APIKey]:
        """List all API keys (without plaintext)."""
        stmt = select(APIKey).order_by(APIKey.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def revoke_key(self, db: AsyncSession, key_id: str) -> bool:
        """Revoke (deactivate) an API key by ID."""
        stmt = (
            update(APIKey)
            .where(APIKey.id == key_id)
            .values(is_active=False)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0


# Singleton instance
api_key_service = APIKeyService()
