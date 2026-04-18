"""
Database models for the application.

Defines SQLAlchemy models for API key management.
"""

import hashlib
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Index, String
from sqlalchemy.orm import declarative_base

# Import the shared Base from database module
from app.db.database import Base as SharedBase


class APIKey(SharedBase):
    """Model for storing API keys with hashed values."""

    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, index=True)
    key_hash = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_api_keys_key_hash", "key_hash"),
        Index("ix_api_keys_is_active", "is_active"),
    )

    @classmethod
    def generate_key(cls, plain_key: str) -> str:
        """Generate SHA256 hash of the plain API key."""
        return hashlib.sha256(plain_key.encode()).hexdigest()
