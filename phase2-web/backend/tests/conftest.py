"""Pytest fixtures for Todo API tests."""

import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import User, Task
from auth import AuthenticatedUser, get_current_user, get_verified_user


# Test database - use SQLite in memory
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Test user ID
TEST_USER_ID = UUID("550e8400-e29b-41d4-a716-446655440000")
TEST_USER_EMAIL = "test@example.com"


def get_test_session():
    """Override database session for tests."""
    with Session(test_engine) as session:
        yield session


def get_mock_current_user():
    """Mock authenticated user for tests."""
    return AuthenticatedUser(
        id=TEST_USER_ID,
        email=TEST_USER_EMAIL,
        name="Test User"
    )


async def get_mock_verified_user(user_id: UUID):
    """Mock verified user - checks user_id matches test user."""
    if user_id != TEST_USER_ID:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )
    return AuthenticatedUser(
        id=TEST_USER_ID,
        email=TEST_USER_EMAIL,
        name="Test User"
    )


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables."""
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def session(test_db):
    """Provide a test database session."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def test_user(session):
    """Create a test user."""
    user = User(
        id=TEST_USER_ID,
        email=TEST_USER_EMAIL,
        name="Test User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers():
    """Provide mock authorization headers (not actually used with mocked auth)."""
    return {"Authorization": "Bearer mock-token"}


@pytest.fixture(scope="function")
def client(test_db, test_user):
    """Provide a test client with mocked dependencies."""
    from db import get_session

    # Override database session
    app.dependency_overrides[get_session] = get_test_session

    # Override auth dependencies to use mock user
    app.dependency_overrides[get_verified_user] = get_mock_verified_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_no_auth(test_db, test_user):
    """Provide a test client WITHOUT mocked auth (for testing 401 responses)."""
    from db import get_session

    # Only override database session, not auth
    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_task(session, test_user):
    """Create a sample task for testing."""
    task = Task(
        user_id=test_user.id,
        title="Sample Task",
        description="Sample description",
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
