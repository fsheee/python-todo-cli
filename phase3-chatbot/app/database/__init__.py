"""
Database configuration and connection management.

This module provides database setup without relying on Alembic migrations
for Python 3.13 compatibility.
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Patch for Python 3.13 SQLAlchemy typing issue
import sys
if sys.version_info >= (3, 13):
    # Disable strict typing checks that break in Python 3.13
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Monkey patch to bypass TypingOnly check
    try:
        from sqlalchemy.util import langhelpers
        original_init_subclass = langhelpers.MemoizedSlots.__init_subclass__

        def patched_init_subclass(cls, **kwargs):
            try:
                original_init_subclass(**kwargs)
            except AssertionError:
                # Ignore TypingOnly assertion errors in Python 3.13
                pass

        langhelpers.MemoizedSlots.__init_subclass__ = classmethod(patched_init_subclass)
    except Exception as e:
        logging.warning(f"Could not apply SQLAlchemy patch: {e}")

load_dotenv()
logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Base class for models
Base = declarative_base()

logger.info(f"Database configured: {DATABASE_URL[:50]}...")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database - create all tables.

    This is an alternative to Alembic migrations for Python 3.13.
    """
    try:
        async with engine.begin() as conn:
            # Import all models to register them
            from app.models.chat_history import ChatHistory

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


async def drop_db():
    """
    Drop all database tables.

    WARNING: This will delete all data!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("🗑️ All database tables dropped")
