"""
Integration tests for database operations.

Tests the chat_history table and all query functions
with a real database connection.

Spec Reference: specs/database/chat-history.md
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_history import ChatHistory
from app.queries.chat_queries import (
    load_chat_history,
    save_message,
    get_user_sessions,
    delete_session,
    cleanup_old_deleted_sessions
)


class TestChatHistoryModel:
    """Test ChatHistory SQLModel validation and creation."""

    @pytest.mark.asyncio
    async def test_create_chat_history_with_all_fields(self, db_session: AsyncSession, test_user_id: int):
        """TC-1.3.1: Create instance with all fields - succeeds"""
        message = ChatHistory(
            user_id=test_user_id,
            session_id="sess_test",
            role="user",
            content="Hello, world!",
            metadata={"client_ip": "127.0.0.1"},
            timestamp=datetime.utcnow(),
            is_deleted=False
        )

        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        assert message.id is not None
        assert message.user_id == test_user_id
        assert message.role == "user"
        assert message.content == "Hello, world!"

    @pytest.mark.asyncio
    async def test_create_chat_history_minimal_fields(self, db_session: AsyncSession, test_user_id: int):
        """TC-1.3.2: Create instance with minimal fields - succeeds"""
        message = ChatHistory(
            user_id=test_user_id,
            session_id="sess_min",
            role="assistant",
            content="Response"
        )

        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        assert message.id is not None
        assert message.is_deleted is False  # Default value
        assert message.timestamp is not None  # Auto-generated


class TestLoadChatHistory:
    """Test load_chat_history query function."""

    @pytest.mark.asyncio
    async def test_load_recent_messages(self, db_session: AsyncSession, test_user_id: int, test_session_id: str):
        """TC-1.4.1: Load 5 messages from session with 10 - returns 5 most recent"""
        # Create 10 messages
        for i in range(10):
            msg = ChatHistory(
                user_id=test_user_id,
                session_id=test_session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                timestamp=datetime.utcnow() + timedelta(seconds=i)
            )
            db_session.add(msg)
        await db_session.commit()

        # Load last 5
        messages = await load_chat_history(db_session, test_user_id, test_session_id, limit=5)

        assert len(messages) == 5
        # Should be in chronological order (oldest first)
        assert messages[0].content == "Message 5"
        assert messages[-1].content == "Message 9"

    @pytest.mark.asyncio
    async def test_load_from_empty_session(self, db_session: AsyncSession, test_user_id: int):
        """TC-1.4.2: Load from empty session - returns empty list"""
        messages = await load_chat_history(db_session, test_user_id, "sess_empty")

        assert messages == []

    @pytest.mark.asyncio
    async def test_user_isolation(self, db_session: AsyncSession, test_session_id: str):
        """TC-1.4.4: User A cannot load User B's messages - returns empty"""
        # Create messages for user 123
        msg = ChatHistory(
            user_id=123,
            session_id=test_session_id,
            role="user",
            content="User 123 message"
        )
        db_session.add(msg)
        await db_session.commit()

        # Try to load as user 456
        messages = await load_chat_history(db_session, 456, test_session_id)

        assert messages == []

    @pytest.mark.asyncio
    async def test_soft_deleted_messages_excluded(self, db_session: AsyncSession, test_user_id: int, test_session_id: str):
        """TC-1.4.5: Soft-deleted messages excluded from results"""
        # Create normal message
        msg1 = ChatHistory(
            user_id=test_user_id,
            session_id=test_session_id,
            role="user",
            content="Active message",
            is_deleted=False
        )
        # Create deleted message
        msg2 = ChatHistory(
            user_id=test_user_id,
            session_id=test_session_id,
            role="user",
            content="Deleted message",
            is_deleted=True
        )
        db_session.add(msg1)
        db_session.add(msg2)
        await db_session.commit()

        messages = await load_chat_history(db_session, test_user_id, test_session_id)

        assert len(messages) == 1
        assert messages[0].content == "Active message"


class TestSaveMessage:
    """Test save_message mutation function."""

    @pytest.mark.asyncio
    async def test_save_user_message(self, db_session: AsyncSession, test_user_id: int, test_session_id: str):
        """TC-1.5.1: Save user message - succeeds, returns ID"""
        message = await save_message(
            db_session,
            test_user_id,
            test_session_id,
            "user",
            "Test message"
        )

        assert message.id is not None
        assert message.user_id == test_user_id
        assert message.role == "user"
        assert message.content == "Test message"

    @pytest.mark.asyncio
    async def test_save_with_metadata(self, db_session: AsyncSession, test_user_id: int, test_session_id: str):
        """TC-1.5.2: Save assistant message with metadata - succeeds"""
        metadata = {"tool_calls": ["create_todo"], "tokens": 150}

        message = await save_message(
            db_session,
            test_user_id,
            test_session_id,
            "assistant",
            "Response text",
            metadata=metadata
        )

        assert message.msg_metadata == metadata

    @pytest.mark.asyncio
    async def test_timestamp_auto_generated(self, db_session: AsyncSession, test_user_id: int, test_session_id: str):
        """TC-1.5.4: Timestamp auto-generated - within 1 second of now"""
        before = datetime.utcnow()
        message = await save_message(db_session, test_user_id, test_session_id, "user", "Test")
        after = datetime.utcnow()

        assert before <= message.timestamp <= after


class TestGetUserSessions:
    """Test get_user_sessions query function."""

    @pytest.mark.asyncio
    async def test_get_sessions_summary(self, db_session: AsyncSession, test_user_id: int):
        """TC-1.6.1: User with 3 sessions - returns 3 summaries"""
        # Create messages in 3 different sessions
        sessions = ["sess_1", "sess_2", "sess_3"]
        for sess in sessions:
            for i in range(3):
                msg = ChatHistory(
                    user_id=test_user_id,
                    session_id=sess,
                    role="user",
                    content=f"Message {i}"
                )
                db_session.add(msg)
        await db_session.commit()

        result = await get_user_sessions(db_session, test_user_id)

        assert len(result) == 3
        # Check that each has required fields
        for session in result:
            assert "session_id" in session
            assert "started_at" in session
            assert "last_message_at" in session
            assert "message_count" in session


class TestDeleteSession:
    """Test delete_session soft delete function."""

    @pytest.mark.asyncio
    async def test_soft_delete_session(self, db_session: AsyncSession, test_user_id: int, test_session_id: str):
        """TC-1.7.1: Delete session with 10 messages - returns 10"""
        # Create 10 messages
        for i in range(10):
            msg = ChatHistory(
                user_id=test_user_id,
                session_id=test_session_id,
                role="user",
                content=f"Message {i}"
            )
            db_session.add(msg)
        await db_session.commit()

        # Delete session
        count = await delete_session(db_session, test_user_id, test_session_id)

        assert count == 10

    @pytest.mark.asyncio
    async def test_deleted_messages_not_loaded(self, db_session: AsyncSession, test_user_id: int, test_session_id: str):
        """TC-1.7.2: Messages no longer appear in load_chat_history"""
        # Create and then delete session
        msg = ChatHistory(user_id=test_user_id, session_id=test_session_id, role="user", content="Test")
        db_session.add(msg)
        await db_session.commit()

        await delete_session(db_session, test_user_id, test_session_id)

        # Try to load
        messages = await load_chat_history(db_session, test_user_id, test_session_id)

        assert messages == []

    @pytest.mark.asyncio
    async def test_delete_nonexistent_session(self, db_session: AsyncSession, test_user_id: int):
        """TC-1.7.3: Delete non-existent session - returns 0"""
        count = await delete_session(db_session, test_user_id, "sess_nonexistent")

        assert count == 0


class TestCleanupOldSessions:
    """Test cleanup_old_deleted_sessions maintenance function."""

    @pytest.mark.asyncio
    async def test_cleanup_old_deleted_messages(self, db_session: AsyncSession, test_user_id: int):
        """TC-1.8.1: Delete messages older than 90 days - succeeds"""
        # Create old deleted message
        old_msg = ChatHistory(
            user_id=test_user_id,
            session_id="sess_old",
            role="user",
            content="Old message",
            is_deleted=True,
            timestamp=datetime.utcnow() - timedelta(days=100)
        )
        # Create recent deleted message
        recent_msg = ChatHistory(
            user_id=test_user_id,
            session_id="sess_recent",
            role="user",
            content="Recent message",
            is_deleted=True,
            timestamp=datetime.utcnow() - timedelta(days=10)
        )
        db_session.add(old_msg)
        db_session.add(recent_msg)
        await db_session.commit()

        # Cleanup messages older than 90 days
        count = await cleanup_old_deleted_sessions(db_session, days=90)

        assert count == 1  # Only old message deleted

    @pytest.mark.asyncio
    async def test_active_messages_preserved(self, db_session: AsyncSession, test_user_id: int):
        """TC-1.8.3: Non-deleted old messages preserved"""
        # Create old active message
        old_active = ChatHistory(
            user_id=test_user_id,
            session_id="sess_old_active",
            role="user",
            content="Old but active",
            is_deleted=False,
            timestamp=datetime.utcnow() - timedelta(days=100)
        )
        db_session.add(old_active)
        await db_session.commit()

        # Cleanup
        await cleanup_old_deleted_sessions(db_session, days=90)

        # Message should still exist
        messages = await load_chat_history(db_session, test_user_id, "sess_old_active")
        assert len(messages) == 1
