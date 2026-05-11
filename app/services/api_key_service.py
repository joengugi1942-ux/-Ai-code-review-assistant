import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import APIKey


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class APIKeyService:
    """Service for managing API keys (generate, verify, revoke)."""

    async def generate_key(self, db: AsyncSession, name: str | None = None) -> str:
        """Generate a new API key. Returns the plain text key (shown once)."""
        plain_key = secrets.token_hex(16)
        api_key = APIKey(
            id=str(uuid.uuid4()),
            key_hash=APIKey.generate_key(plain_key),
            name=name,
            is_active=True,
            created_at=_utcnow(),
            last_used_at=None,
        )
        db.add(api_key)
        await db.commit()
        return plain_key

    async def verify_key(self, db: AsyncSession, plain_key: str) -> bool:
        """Verify a plain API key and update last_used_at on success."""
        key_hash = APIKey.generate_key(plain_key)
        stmt = select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
        result = await db.execute(stmt)
        api_key = result.scalar_one_or_none()
        if api_key:
            api_key.last_used_at = _utcnow()
            await db.commit()
            return True
        return False

    async def list_keys(self, db: AsyncSession) -> list[APIKey]:
        stmt = select(APIKey).order_by(APIKey.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def revoke_key(self, db: AsyncSession, key_id: str) -> bool:
        stmt = update(APIKey).where(APIKey.id == key_id).values(is_active=False)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0


api_key_service = APIKeyService()
