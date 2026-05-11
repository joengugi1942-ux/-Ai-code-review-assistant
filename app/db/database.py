from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

database_url = str(settings.database_url)

# SQLite requires check_same_thread=False; other drivers ignore this kwarg
_connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

# Always set echo=False to avoid SQLAlchemy stdout logging; control via loggers
engine = create_async_engine(
    database_url,
    echo=False,  # Changed from settings.app_env == "development"
    future=True,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session