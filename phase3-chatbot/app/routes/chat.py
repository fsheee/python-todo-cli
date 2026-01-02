"""
Chat endpoint for conversational todo management

Spec Reference: specs/PLAN.md - Backend API Implementation
Tasks: 4.1-4.7
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas import ChatRequest, ChatResponse
from app.middleware.auth import verify_jwt_token, security
from app.agents import process_chat_message
from app.storage import get_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


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
    # Task 4.2: Validate JWT and extract user_id
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

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
            {"role": msg.get("role", "unknown"), "content": msg.get("content", "")}
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
