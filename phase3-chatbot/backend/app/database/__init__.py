"""
Database configuration and connection management.

This module provides database setup using SQLModel (Async).
"""

import os
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from dotenv import load_dotenv

# Patch for Python 3.13 SQLAlchemy typing issue
if sys.version_info >= (3, 13):
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    # Monkey patch to bypass TypingOnly check if needed for older libraries
    try:
        from sqlalchemy.util import langhelpers
        original_init_subclass = langhelpers.MemoizedSlots.__init_subclass__

        def patched_init_subclass(cls, **kwargs):
            try:
                original_init_subclass(**kwargs)
            except AssertionError:
                pass

        langhelpers.MemoizedSlots.__init_subclass__ = classmethod(patched_init_subclass)
    except Exception:
        pass

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
    pool_pre_ping=True
)

# Create session factory MANUALLY (replacing async_sessionmaker)
# This ensures compatibility and proper async configuration
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

logger.info(f"Database configured with SQLModel (Async)")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Optional: commit on success if your logic relies on it
            # await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Async context manager for database sessions.

    Usage:
        async with get_db_session() as session:
            await session.execute(...)

    This is an alternative to the FastAPI dependency `get_db`.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database - create all tables.
    """
    try:
        # Verify connection first
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info("✅ Database connection verified")

        async with engine.begin() as conn:
            # Import all models to register them with SQLModel
            from app.models.chat_history import ChatHistory
            from app.models.user import User
            from app.models.task import Task

            # Create all tables
            await conn.run_sync(SQLModel.metadata.create_all)
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
        await conn.run_sync(SQLModel.metadata.drop_all)
        logger.info("🗑️ All database tables dropped")
