"""
Chat endpoint for conversational todo management

Spec Reference: specs/PLAN.md - Backend API Implementation
Tasks: 4.1-4.7
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Request, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas import ChatRequest, ChatResponse, MessageListResponse
from app.middleware.auth import verify_jwt_token, security
from app.agents import process_chat_message
from app.storage import get_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/history/{session_id}", response_model=MessageListResponse)
async def get_chat_history(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = 50,
    offset: int = 0,
):
    """Load chat history for a session (ChatKit compatibility)."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    storage = get_storage()

    messages = storage.get_session_messages(user_id, session_id, limit=limit, offset=offset)
    total = storage.get_message_count(user_id, session_id)

    return MessageListResponse(
        messages=messages,
        total=total,
        session_id=session_id,
        user_id=user_id,
        has_more=(offset + limit) < total
    )


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Process user chat message and return AI assistant response

    This endpoint:
    1. Validates JWT token and extracts user_id
    2. Loads recent chat history from file storage
    3. Saves user message to file storage
    4. Processes message through AI agent (with MCP tools)
    5. Saves assistant response to file storage
    6. Returns response to user

    Spec Reference: specs/PLAN.md - Chat Flow
    """
    # Task 4.2: Validate JWT token and extract user_id
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    # Get file-based storage
    storage = get_storage()

    # Task 4.8: Log incoming request
    logger.info(
        f"Chat request - user_id: {user_id}, "
        f"session: {chat_request.session_id}, "
        f"msg_len: {len(chat_request.message)}"
    )

    try:
        # Task 4.3: Load chat history from file storage
        history = storage.load_chat_history(
            user_id=user_id,
            session_id=chat_request.session_id,
            limit=20
        )
        formatted_history = [
            {
                "role": msg.get("role", "unknown"),
                "content": msg.get("content", ""),
                "metadata": msg.get("metadata", {})
            }
            for msg in history
        ]

        # Task 4.4: Save user message to file storage
        storage.save_message(
            user_id=user_id,
            session_id=chat_request.session_id,
            role="user",
            content=chat_request.message,
            metadata={
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )

        # Task 4.5: Process message through agent
        # Pass the JWT token to the agent so it can authenticate with Phase 2 backend
        jwt_token = credentials.credentials
        agent_response = await process_chat_message(
            user_id=user_id,
            session_id=chat_request.session_id,
            message=chat_request.message,
            history=formatted_history,
            jwt_token=jwt_token
        )

        # Task 4.6: Save assistant response to file storage
        storage.save_message(
            user_id=user_id,
            session_id=chat_request.session_id,
            role="assistant",
            content=agent_response["content"],
            metadata=agent_response.get("metadata", {})
        )

        # Task 4.8: Log successful response
        logger.info(
            f"Chat response - user_id: {user_id}, "
            f"session: {chat_request.session_id}, "
            f"resp_len: {len(agent_response['content'])}"
        )

        # Return response
        return ChatResponse(
            response=agent_response["content"],
            session_id=chat_request.session_id,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Task 4.7: Error handling
        logger.error(
            f"Error processing chat - user_id: {user_id}, "
            f"session: {chat_request.session_id}, "
            f"error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message. Please try again."
        )


@router.get("/sessions", response_model=list)
async def get_user_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all conversation sessions for the authenticated user."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    storage = get_storage()
    # Get all session IDs for this user
    sessions = storage.get_user_sessions(user_id)

    return sessions


@router.post("/session", response_model=dict)
async def create_or_resume_session(
    request: Request,
    session_id: str = Query(None, description="Session ID to resume, or None to create new"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new session or resume existing one."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    storage = get_storage()

    # If no session_id provided, create a new one
    if not session_id:
        import uuid
        session_id = f"sess_{int(datetime.now(timezone.utc).timestamp())}_{str(uuid.uuid4())[:8]}"

    # Ensure session exists (create if needed)
    storage.ensure_session_exists(user_id, session_id)

    # Log session creation/resumption
    logger.info(f"Session {'created' if not storage.session_exists(user_id, session_id) else 'resumed'} - user_id: {user_id}, session: {session_id}")

    return {
        "session_id": session_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
