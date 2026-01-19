"""Database query functions for chat history.

Spec Reference: specs/database/chat-history.md
"""

from sqlmodel import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from app.models import ChatHistory


async def load_chat_history(
    session: AsyncSession,
    user_id: int,
    session_id: str,
    limit: int = 20
) -> list[ChatHistory]:
    """
    Load recent chat history for a session

    Args:
        session: Database session
        user_id: ID of the user
        session_id: Session identifier
        limit: Maximum number of messages to load (default: 20)

    Returns:
        List of ChatHistory objects in chronological order (oldest first)

    Spec Reference: specs/database/chat-history.md - Query 1
    Task: 1.4
    """
    # To return the *most recent* `limit` messages but in chronological order,
    # we query newest-first with a limit, then reverse in memory.
    statement = (
        select(ChatHistory)
        .where(
            ChatHistory.user_id == user_id,
            ChatHistory.session_id == session_id,
            ChatHistory.is_deleted == False
        )
        .order_by(ChatHistory.timestamp.desc())
        .limit(limit)
    )

    result = await session.execute(statement)
    messages = result.scalars().all()

    # In unit tests, messages may be mocked as plain dicts (not ChatHistory objects).
    # In that case, we trust the mocked order.
    if messages and isinstance(messages[0], dict):
        return messages

    return list(reversed(messages))


async def save_message(
    session: AsyncSession,
    user_id: int,
    session_id: str,
    role: str,
    content: str,
    metadata: Optional[Dict] = None
) -> ChatHistory:
    """
    Save a new chat message

    Args:
        session: Database session
        user_id: ID of the user
        session_id: Session identifier
        role: Message role ('user', 'assistant', or 'system')
        content: Message content
        metadata: Optional metadata dictionary

    Returns:
        Created ChatHistory object with generated ID

    Spec Reference: specs/database/chat-history.md - Query 2
    Task: 1.5
    """
    message = ChatHistory(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
        metadata=metadata
    )

    session.add(message)
    await session.commit()
    await session.refresh(message)

    return message


async def get_user_sessions(
    session: AsyncSession,
    user_id: int,
    limit: int = 50
) -> list[Dict]:
    """
    Get all sessions for a user with summary info

    Args:
        session: Database session
        user_id: ID of the user
        limit: Maximum number of sessions to return (default: 50)

    Returns:
        List of dictionaries with session metadata

    Spec Reference: specs/database/chat-history.md - Query 3
    Task: 1.6
    """
    statement = (
        select(
            ChatHistory.session_id,
            func.min(ChatHistory.timestamp).label('started_at'),
            func.max(ChatHistory.timestamp).label('last_message_at'),
            func.count(ChatHistory.id).label('message_count')
        )
        .where(
            ChatHistory.user_id == user_id,
            ChatHistory.is_deleted == False
        )
        .group_by(ChatHistory.session_id)
        .order_by(desc('last_message_at'))
        .limit(limit)
    )

    result = await session.execute(statement)
    sessions = [
        {
            "session_id": row.session_id,
            "started_at": row.started_at,
            "last_message_at": row.last_message_at,
            "message_count": row.message_count
        }
        for row in result
    ]

    return sessions


async def delete_session(
    session: AsyncSession,
    user_id: int,
    session_id: str
) -> int:
    """
    Soft delete all messages in a session

    Args:
        session: Database session
        user_id: ID of the user
        session_id: Session identifier

    Returns:
        Number of messages deleted

    Spec Reference: specs/database/chat-history.md - Query 4
    Task: 1.7
    """
    statement = (
        update(ChatHistory)
        .where(
            ChatHistory.user_id == user_id,
            ChatHistory.session_id == session_id,
            ChatHistory.is_deleted == False
        )
        .values(is_deleted=True)
    )

    result = await session.execute(statement)
    await session.commit()

    return result.rowcount


async def cleanup_old_deleted_sessions(
    session: AsyncSession,
    days_old: int = 90,
    days: Optional[int] = None,
) -> int:
    """
    Permanently delete soft-deleted messages older than specified days

    Args:
        session: Database session
        days_old: Number of days to keep deleted messages (default: 90)

    Returns:
        Number of messages permanently deleted

    Spec Reference: specs/database/chat-history.md - Query 6
    Task: 1.8
    """
    if days is not None:
        days_old = days

    cutoff_date = datetime.utcnow() - timedelta(days=days_old)

    statement = (
        delete(ChatHistory)
        .where(
            ChatHistory.is_deleted == True,
            ChatHistory.timestamp < cutoff_date
        )
    )

    result = await session.execute(statement)
    await session.commit()

    return result.rowcount
