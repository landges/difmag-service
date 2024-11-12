from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)
from typing import AsyncGenerator
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import config


# create session factory to generate new database sessions
SessionFactory = sessionmaker(
    bind=create_engine(config.database.dsn),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def create_session() -> Iterator[Session]:
    """Create new database session.

    Yields:
        Database session.
    """

    session = SessionFactory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


DB_POOL_SIZE = 83
WEB_CONCURRENCY = 9
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

async_engine = create_async_engine(
    config.database.dsn.replace('psycopg2', 'asyncpg'),
    echo=False,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=1,
    max_overflow=64,
)

AsyncSessionFactory = async_sessionmaker(
    autocommit=False,
    class_=AsyncSession,
    expire_on_commit=False,
    bind=async_engine,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
