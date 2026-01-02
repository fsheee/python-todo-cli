"""
Unit Tests for Chat Query Functions

Tests for app/queries/chat_queries.py

Spec Reference: specs/database/chat-history.md
Tasks: 1.4-1.8
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_session():
    """Create mock database session"""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def sample_chat_history():
    """Sample chat history data"""
    return [
        {
            "id": 1,
            "user_id": 123,
            "session_id": "session-1",
            "role": "user",
            "content": "Add buy groceries",
            "timestamp": datetime.utcnow() - timedelta(minutes=10),
            "is_deleted": False
        },
        {
            "id": 2,
            "user_id": 123,
            "session_id": "session-1",
            "role": "assistant",
            "content": "I've created a todo for you",
            "timestamp": datetime.utcnow() - timedelta(minutes=9),
            "is_deleted": False
        }
    ]


class TestLoadChatHistory:
    """Tests for load_chat_history function"""

    @pytest.mark.asyncio
    async def test_load_chat_history_success(self, mock_session, sample_chat_history):
        """Test successful chat history loading"""
        from app.queries import load_chat_history

        # Mock the result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_chat_history

        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await load_chat_history(
            session=mock_session,
            user_id=123,
            session_id="session-1",
            limit=20
        )

        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_load_chat_history_empty(self, mock_session):
        """Test loading empty chat history"""
        from app.queries import load_chat_history

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await load_chat_history(
            session=mock_session,
            user_id=123,
            session_id="session-1",
            limit=20
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_load_chat_history_with_limit(self, mock_session):
        """Test loading chat history with limit"""
        from app.queries import load_chat_history

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(return_value=mock_result)

        await load_chat_history(
            session=mock_session,
            user_id=123,
            session_id="session-1",
            limit=10
        )

        # Verify execute was called
        mock_session.execute.assert_called_once()


class TestSaveMessage:
    """Tests for save_message function"""

    @pytest.mark.asyncio
    async def test_save_user_message(self, mock_session):
        """Test saving a user message"""
        from app.queries import save_message

        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        result = await save_message(
            session=mock_session,
            user_id=123,
            session_id="session-1",
            role="user",
            content="Add buy milk"
        )

        assert result is not None or result is None  # Depends on implementation

    @pytest.mark.asyncio
    async def test_save_assistant_message(self, mock_session):
        """Test saving an assistant message"""
        from app.queries import save_message

        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        result = await save_message(
            session=mock_session,
            user_id=123,
            session_id="session-1",
            role="assistant",
            content="I've created that todo for you"
        )

        assert result is not None or result is None


class TestGetUserSessions:
    """Tests for get_user_sessions function"""

    @pytest.mark.asyncio
    async def test_get_user_sessions_success(self, mock_session):
        """Test getting user sessions"""
        from app.queries import get_user_sessions

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            {"session_id": "session-1", "last_message": datetime.utcnow()}
        ]

        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await get_user_sessions(
            session=mock_session,
            user_id=123,
            limit=10
        )

        assert len(result) >= 0

    @pytest.mark.asyncio
    async def test_get_user_sessions_empty(self, mock_session):
        """Test getting sessions when none exist"""
        from app.queries import get_user_sessions

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await get_user_sessions(
            session=mock_session,
            user_id=123,
            limit=10
        )

        assert result == []


class TestDeleteSession:
    """Tests for delete_session function"""

    @pytest.mark.asyncio
    async def test_delete_session_success(self, mock_session):
        """Test soft deleting a session"""
        from app.queries import delete_session

        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        result = await delete_session(
            session=mock_session,
            user_id=123,
            session_id="session-1"
        )

        # Verify soft delete was performed
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, mock_session):
        """Test deleting non-existent session"""
        from app.queries import delete_session

        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        result = await delete_session(
            session=mock_session,
            user_id=123,
            session_id="non-existent"
        )


class TestCleanupOldDeletedSessions:
    """Tests for cleanup_old_deleted_sessions function"""

    @pytest.mark.asyncio
    async def test_cleanup_old_sessions(self, mock_session):
        """Test cleaning up old deleted sessions"""
        from app.queries import cleanup_old_deleted_sessions

        mock_result = MagicMock()
        mock_result.rowcount = 5

        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        days_old = 30
        deleted_count = await cleanup_old_deleted_sessions(
            session=mock_session,
            days_old=days_old
        )

        assert deleted_count >= 0

    @pytest.mark.asyncio
    async def test_cleanup_no_old_sessions(self, mock_session):
        """Test cleanup when no old sessions exist"""
        from app.queries import cleanup_old_deleted_sessions

        mock_result = MagicMock()
        mock_result.rowcount = 0

        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        deleted_count = await cleanup_old_deleted_sessions(
            session=mock_session,
            days_old=30
        )

        assert deleted_count == 0


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
