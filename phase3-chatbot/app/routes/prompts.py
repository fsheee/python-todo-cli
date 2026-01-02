"""
Prompt history management endpoints.

Provides access to user's prompt history with search, filtering, and export capabilities.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
from tempfile import NamedTemporaryFile

from app.middleware.auth import verify_jwt_token, security
from app.storage import FileBasedChatStorage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["prompts"])

# Initialize file storage
file_storage = FileBasedChatStorage(base_path="data/chat-history")


# Request/Response Models
class PromptResponse(BaseModel):
    prompt_id: str
    user_id: int
    session_id: Optional[str]
    prompt: str
    timestamp: str
    date: str
    metadata: dict


class PromptStatisticsResponse(BaseModel):
    total_prompts: int
    first_prompt: Optional[str]
    last_prompt: Optional[str]
    prompts_by_date: dict
    prompts_by_session: dict
    average_prompt_length: float
    most_active_date: Optional[str]


class DeletePromptHistoryRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    session_id: Optional[str] = None
    confirm: bool = False


class DeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: Optional[int] = None


# Endpoints

@router.get("/history", response_model=List[PromptResponse])
async def get_prompt_history(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    session_id: Optional[str] = Query(None, description="Filter by session ID")
):
    """
    Get user's prompt history with optional filters.

    Args:
        limit: Maximum number of prompts to return (1-1000)
        offset: Number of prompts to skip (for pagination)
        start_date: Filter prompts from this date onwards
        end_date: Filter prompts up to this date
        session_id: Filter prompts from specific session

    Returns:
        List of prompt objects in reverse chronological order
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        prompts = file_storage.get_prompt_history(
            user_id=user_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            session_id=session_id
        )

        logger.info(
            f"Retrieved {len(prompts)} prompts for user {user_id} "
            f"(limit={limit}, offset={offset})"
        )
        return prompts

    except Exception as e:
        logger.error(f"Error retrieving prompt history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prompt history"
        )


@router.get("/search", response_model=List[PromptResponse])
async def search_prompts(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=500)
):
    """
    Search user's prompt history by text.

    Args:
        query: Search query (case-insensitive)
        limit: Maximum number of results (1-500)

    Returns:
        List of matching prompt objects
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        matching_prompts = file_storage.search_prompts(
            user_id=user_id,
            query=query,
            limit=limit
        )

        logger.info(
            f"Search query '{query}' returned {len(matching_prompts)} results "
            f"for user {user_id}"
        )
        return matching_prompts

    except Exception as e:
        logger.error(f"Error searching prompts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search prompts"
        )


@router.get("/statistics", response_model=PromptStatisticsResponse)
async def get_prompt_statistics(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get statistics about user's prompt history.

    Returns:
        Statistics including total prompts, date ranges, distribution, etc.
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        statistics = file_storage.get_prompt_statistics(user_id=user_id)

        logger.info(f"Retrieved prompt statistics for user {user_id}")
        return statistics

    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


@router.post("/delete", response_model=DeleteResponse)
async def delete_prompt_history(
    request: DeletePromptHistoryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete prompt history with optional filters.

    WARNING: This action is permanent and cannot be undone.
    Requires explicit confirmation (confirm=true).

    Args:
        start_date: Delete prompts from this date onwards
        end_date: Delete prompts up to this date
        session_id: Delete prompts from specific session
        confirm: Must be True to proceed

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
            detail="Must confirm deletion with confirm=true"
        )

    try:
        deleted_count = file_storage.delete_prompt_history(
            user_id=user_id,
            start_date=request.start_date,
            end_date=request.end_date,
            session_id=request.session_id,
            confirm=True
        )

        if deleted_count == -1:
            message = "All prompt history deleted successfully"
            deleted_count = None
        else:
            message = f"{deleted_count} prompts deleted successfully"

        logger.warning(
            f"User {user_id} deleted prompt history "
            f"(filters: start={request.start_date}, end={request.end_date}, "
            f"session={request.session_id})"
        )

        return DeleteResponse(
            success=True,
            message=message,
            deleted_count=deleted_count
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting prompt history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prompt history"
        )


@router.get("/export")
async def export_prompt_history(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    format: str = Query("json", regex="^(json|jsonl|csv|txt)$")
):
    """
    Export user's prompt history to a file.

    Args:
        format: Export format ('json', 'jsonl', 'csv', or 'txt')

    Returns:
        File download with prompt history
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        # Create temporary file for export
        with NamedTemporaryFile(
            mode="w",
            suffix=f".{format}",
            delete=False,
            encoding="utf-8"
        ) as temp_file:
            temp_path = temp_file.name

        # Export to temporary file
        success = file_storage.export_prompt_history(
            user_id=user_id,
            output_path=temp_path,
            format=format
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export prompt history"
            )

        logger.info(f"Exported prompt history for user {user_id} in {format} format")

        # Return file
        return FileResponse(
            path=temp_path,
            filename=f"prompt-history-{user_id}.{format}",
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting prompt history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export prompt history"
        )


@router.get("/recent", response_model=List[str])
async def get_recent_prompts(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get recent prompts (text only, for quick access/suggestions).

    Args:
        limit: Maximum number of recent prompts (1-50)

    Returns:
        List of recent prompt texts
    """
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    try:
        prompts = file_storage.get_prompt_history(
            user_id=user_id,
            limit=limit
        )

        # Extract just the prompt text
        recent_prompts = [p["prompt"] for p in prompts]

        logger.info(f"Retrieved {len(recent_prompts)} recent prompts for user {user_id}")
        return recent_prompts

    except Exception as e:
        logger.error(f"Error retrieving recent prompts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent prompts"
        )
