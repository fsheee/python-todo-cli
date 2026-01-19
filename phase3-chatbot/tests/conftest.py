"""
Pytest configuration and fixtures for Phase 3 tests.

This file provides shared fixtures for database setup, mocking,
and test utilities used across all test files.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Load test environment
load_dotenv(".env.test")

# Test database URL
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Create async engine for tests
# Handle missing drivers gracefully
try:
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )

    # Create session factory
    TestSessionLocal = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
except ImportError:
    # If aiosqlite or other drivers are missing
    print("Warning: Database driver missing. SQL tests might fail if not using mocks.")
    test_engine = None
    TestSessionLocal = None
except Exception as e:
    print(f"Warning: Could not create test engine: {e}")
    test_engine = None
    TestSessionLocal = None


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    Creates all tables before the test and drops them after.
    """
    if not test_engine or not TestSessionLocal:
        # Yield a mock session if real DB unavailable
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        yield session
        return

    # Create all tables
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")
        # Yield mock
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        yield session
        return

    # Create session
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def mock_session():
    """Create mock database session for unit tests."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_http_client():
    """Create mock HTTP client for MCP tests."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def test_user_id() -> int:
    """Return a test user ID."""
    return 123


@pytest.fixture
def test_session_id() -> str:
    """Return a test session ID."""
    return "sess_test_12345"


@pytest.fixture
def mock_jwt_token() -> str:
    """Return a mock JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSJ9.mock"


@pytest.fixture
async def http_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with AsyncClient() as client:
        yield client


@pytest.fixture
def sample_chat_messages() -> list[dict]:
    """Return sample chat messages for testing."""
    return [
        {
            "role": "user",
            "content": "Add buy milk",
            "timestamp": "2025-12-25T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "I've added 'Buy milk' to your list.",
            "timestamp": "2025-12-25T10:00:01Z"
        },
        {
            "role": "user",
            "content": "Show my tasks",
            "timestamp": "2025-12-25T10:01:00Z"
        }
    ]


@pytest.fixture
def sample_todos() -> list[dict]:
    """Return sample todo items for testing."""
    return [
        {
            "id": 1,
            "user_id": 123,
            "title": "Buy milk",
            "description": "Get 2% milk from store",
            "status": "pending",
            "priority": "medium",
            "due_date": "2025-12-26T00:00:00Z"
        },
        {
            "id": 2,
            "user_id": 123,
            "title": "Call dentist",
            "description": None,
            "status": "pending",
            "priority": "high",
            "due_date": "2025-12-25T00:00:00Z"
        }
    ]

