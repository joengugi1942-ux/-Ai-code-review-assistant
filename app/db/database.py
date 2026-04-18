"""
Database configuration and session management.

Sets up SQLAlchemy async engine, session factory, and dependency for FastAPI.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Parse database URL
database_url = str(settings.database_url)

# Create async engine with appropriate driver
engine = create_async_engine(
    database_url,
    echo=settings.app_env == "development",
    future=True,
    # For MySQL, SQLAlchemy needs the aiomysql dialect
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """FastAPI dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        yield session
