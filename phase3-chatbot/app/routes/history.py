"""
History management endpoints for chat sessions.

Spec Reference: specs/storage/file-based-mono-structure.md
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.middleware.auth import verify_jwt_token, security
from app.storage import FileBasedChatStorage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["history"])

# Initialize file storage
file_storage = FileBasedChatStorage(base_path="data/chat-history")


# Request/Response Models
class DeleteSessionRequest(BaseModel):
    session_id: str
    permanent: bool = False


class DeleteMultipleSessionsRequest(BaseModel):
    session_ids: List[str]
    permanent: bool = False


class DeleteAllSessionsRequest(BaseModel):
    permanent: bool = False
    confirm: bool = False


class DeleteMessagesRequest(BaseModel):
    session_id: str
    message_sequences: List[int]


class RestoreSessionRequest(BaseModel):
    session_id: str


class SessionResponse(BaseModel):
    session_id: str
    user_id: int
    created_at: str
    updated_at: str
    message_count: int
    status: str


class DeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: Optional[int] = None


# Endpoints

@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = False
):
    """
    Get all chat sessions for the authenticated user.

    Args:
        limit: Maximum number of sessions to return (1-100)
        include_deleted: Include soft-deleted sessions

    Returns:
        List of session metadata objects
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        if include_deleted:
            sessions = file_storage.get_deleted_sessions(user_id, limit)
        else:
            sessions = file_storage.get_user_sessions(user_id, limit)

        logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
        return sessions

    except Exception as e:
        logger.error(f"Error retrieving sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )


@router.post("/delete-session", response_model=DeleteResponse)
async def delete_session(
    request: DeleteSessionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete a single chat session.

    Args:
        session_id: Session identifier
        permanent: If True, permanently delete; if False, soft delete (default)

    Returns:
        Deletion status
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        if request.permanent:
            success = file_storage.delete_session_permanent(user_id, request.session_id)
            action = "permanently deleted"
        else:
            success = file_storage.delete_session(user_id, request.session_id)
            action = "deleted"

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {request.session_id} not found"
            )

        logger.info(
            f"User {user_id} {action} session {request.session_id}"
        )

        return DeleteResponse(
            success=True,
            message=f"Session {action} successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


@router.post("/delete-multiple-sessions", response_model=DeleteResponse)
async def delete_multiple_sessions(
    request: DeleteMultipleSessionsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete multiple chat sessions at once.

    Args:
        session_ids: List of session identifiers
        permanent: If True, permanently delete; if False, soft delete

    Returns:
        Deletion status with count
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    if not request.session_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No session IDs provided"
        )

    try:
        results = file_storage.delete_multiple_sessions(
            user_id,
            request.session_ids,
            request.permanent
        )

        deleted_count = sum(1 for success in results.values() if success)
        action = "permanently deleted" if request.permanent else "deleted"

        logger.info(
            f"User {user_id} {action} {deleted_count}/{len(request.session_ids)} sessions"
        )

        return DeleteResponse(
            success=True,
            message=f"{deleted_count} sessions {action} successfully",
            deleted_count=deleted_count
        )

    except Exception as e:
        logger.error(f"Error deleting multiple sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sessions"
        )


@router.post("/delete-all-sessions", response_model=DeleteResponse)
async def delete_all_sessions(
    request: DeleteAllSessionsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete ALL chat sessions for the authenticated user.

    WARNING: This action affects all user sessions.
    Requires explicit confirmation (confirm=true).

    Args:
        permanent: If True, permanently delete; if False, soft delete
        confirm: Must be True to proceed (safety check)

    Returns:
        Deletion status with count
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm deletion of all sessions with confirm=true"
        )

    try:
        deleted_count = file_storage.delete_all_user_sessions(
            user_id,
            request.permanent,
            confirm=True
        )

        action = "permanently deleted" if request.permanent else "deleted"

        logger.warning(
            f"User {user_id} {action} ALL {deleted_count} sessions"
        )

        return DeleteResponse(
            success=True,
            message=f"All {deleted_count} sessions {action} successfully",
            deleted_count=deleted_count
        )

    except Exception as e:
        logger.error(f"Error deleting all sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete all sessions"
        )


@router.post("/delete-messages", response_model=DeleteResponse)
async def delete_messages(
    request: DeleteMessagesRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete specific messages from a session.

    Args:
        session_id: Session identifier
        message_sequences: List of message sequence numbers to delete

    Returns:
        Deletion status with count
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    if not request.message_sequences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No message sequences provided"
        )

    try:
        deleted_count = file_storage.delete_messages_in_session(
            user_id,
            request.session_id,
            request.message_sequences
        )

        logger.info(
            f"User {user_id} deleted {deleted_count} messages from session {request.session_id}"
        )

        return DeleteResponse(
            success=True,
            message=f"{deleted_count} messages deleted successfully",
            deleted_count=deleted_count
        )

    except Exception as e:
        logger.error(f"Error deleting messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete messages"
        )


@router.post("/restore-session", response_model=DeleteResponse)
async def restore_session(
    request: RestoreSessionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Restore a soft-deleted session.

    Args:
        session_id: Session identifier

    Returns:
        Restoration status
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        success = file_storage.restore_session(user_id, request.session_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {request.session_id} not found or not deleted"
            )

        logger.info(
            f"User {user_id} restored session {request.session_id}"
        )

        return DeleteResponse(
            success=True,
            message="Session restored successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore session"
        )


@router.get("/deleted-sessions", response_model=List[SessionResponse])
async def get_deleted_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get all soft-deleted sessions for the authenticated user.

    Args:
        limit: Maximum number of sessions to return (1-100)

    Returns:
        List of deleted session metadata objects
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        sessions = file_storage.get_deleted_sessions(user_id, limit)

        logger.info(f"Retrieved {len(sessions)} deleted sessions for user {user_id}")
        return sessions

    except Exception as e:
        logger.error(f"Error retrieving deleted sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve deleted sessions"
        )
