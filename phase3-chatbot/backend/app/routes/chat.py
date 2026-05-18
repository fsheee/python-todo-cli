"""
Chat endpoint for conversational todo management

Spec Reference: specs/PLAN.md - Backend API Implementation
Tasks: 4.1-4.7
"""

import logging
import re
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Request, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials

from app.schemas import ChatRequest, ChatResponse, MessageListResponse
from app.middleware.auth import verify_jwt_token, security
from app.agents import process_chat_message
from app.storage import get_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


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
        has_more=(offset + limit) < total,
    )


# ---------------------------------------------------------------------------
# Command parser — runs BEFORE the LLM on every request
# ---------------------------------------------------------------------------


def _parse_command(message: str):
    """
    Detect structured todo commands from a user message using regex.

    Returns (command_name, args_dict) or (None, None) if nothing matches.

    Supported commands
    ------------------
    add <title>                  → ("add",      {"title": str})
    show / list [my] [tasks]     → ("list",     {})
    complete / done <id>         → ("complete", {"todo_id": str})
    delete / remove <id>         → ("delete",   {"todo_id": str})
    """
    text = message.strip()

    # --- ADD task -----------------------------------------------------------
    m = re.match(
        r'^(?:add|create|new|make)\s+(?:(?:a\s+)?(?:task|todo|item)\s+)?(.+)$',
        text,
        re.IGNORECASE,
    )
    if m:
        # Pull title from original (preserve case)
        title = re.sub(
            r'^(?:add|create|new|make)\s+(?:(?:a\s+)?(?:task|todo|item)\s+)?',
            '',
            text,
            flags=re.IGNORECASE,
        ).strip()
        if title:
            return ("add", {"title": title})

    # --- LIST tasks ---------------------------------------------------------
    if re.match(
        r'^(?:show|list|view|display|get|see)(?:\s+(?:my\s+|all\s+)?(?:tasks?|todos?|items?|list))?$',
        text,
        re.IGNORECASE,
    ):
        return ("list", {})
    if re.match(
        r"^what(?:'s| is)(?: on)? my (?:list|tasks?|todos?)\??$",
        text,
        re.IGNORECASE,
    ):
        return ("list", {})
    if text.lower() in {
        "tasks", "todos", "my tasks", "my todos",
        "all tasks", "all todos", "task list", "todo list",
    }:
        return ("list", {})

    # --- COMPLETE task ------------------------------------------------------
    m = re.match(
        r'^(?:complete|done|finish|mark\s+(?:(?:as\s+)?(?:done|complete|completed)\s+)?)\s+'
        r'(?:task\s+|#\s*)?(\S+)',
        text,
        re.IGNORECASE,
    )
    if m:
        return ("complete", {"todo_id": m.group(1).lstrip('#')})

    # ALSO: "mark task 3 as done" style
    m = re.match(
        r'^mark\s+(?:task\s+|#\s*)?(\S+)\s+(?:as\s+)?(?:done|complete|completed)$',
        text,
        re.IGNORECASE,
    )
    if m:
        return ("complete", {"todo_id": m.group(1).lstrip('#')})

    # --- DELETE task --------------------------------------------------------
    m = re.match(
        r'^(?:delete|remove|del|rm)\s+(?:task\s+|#\s*)?(\S+)',
        text,
        re.IGNORECASE,
    )
    if m:
        return ("delete", {"todo_id": m.group(1).lstrip('#')})

    return (None, None)


def _looks_like_task_id(token: str) -> bool:
    token = token.strip()
    if not token:
        return False

    if token.isdigit():
        return True

    # Accept common UUID formats used by Phase 2 backend IDs.
    return bool(
        re.match(
            r'^(?:\d+|[0-9a-fA-F]{32}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$',
            token,
        )
    )


async def _execute_command(
    command: str, args: dict, user_id: str, jwt_token: str
) -> dict:
    """
    Execute a parsed command by calling the appropriate MCP tool directly.

    Returns {"content": str, "metadata": dict} — same shape as agent responses.
    """
    from mcp_server.tools.create_todo import create_todo
    from mcp_server.tools.list_todos import list_todos
    from mcp_server.tools.update_todo import update_todo
    from mcp_server.tools.delete_todo import delete_todo

    # ---- ADD ---------------------------------------------------------------
    if command == "add":
        title = args["title"]
        result = await create_todo(user_id=user_id, title=title, jwt_token=jwt_token)
        if result.get("success"):
            todo = result.get("todo", {})
            todo_id = todo.get("id", "")
            id_hint = f" (ID: `{todo_id}`)" if todo_id else ""
            return {
                "content": f"✅ Task added: **{title}**{id_hint}",
                "metadata": {"command": "add", "tool_result": result},
            }
        err = result.get("error", "Unknown error")
        return {
            "content": f"❌ Could not create task: {err}",
            "metadata": {"command": "add", "tool_result": result},
        }

    # ---- LIST --------------------------------------------------------------
    elif command == "list":
        result = await list_todos(user_id=user_id, status="all", jwt_token=jwt_token)
        if result.get("success"):
            todos = result.get("todos", [])
            if not todos:
                return {
                    "content": (
                        "📋 You have no tasks yet. "
                        "Use **add <task name>** to create your first one!"
                    ),
                    "metadata": {"command": "list", "tool_result": result},
                }
            lines = []
            for i, todo in enumerate(todos, start=1):
                icon = "✅" if todo.get("status") == "completed" else "⬜"
                title = todo.get("title", "Untitled")
                todo_id = todo.get("id", "")
                id_hint = f" (ID: `{todo_id}`)" if todo_id else ""
                lines.append(f"{i}. {icon} {title}{id_hint}")
            body = "\n".join(lines)
            return {
                "content": f"📋 **Your tasks ({len(todos)}):**\n\n{body}",
                "metadata": {
                    "command": "list",
                    "tool_result": result,
                    "count": len(todos),
                },
            }
        err = result.get("error", "Unknown error")
        return {
            "content": f"❌ Could not retrieve tasks: {err}",
            "metadata": {"command": "list", "tool_result": result},
        }

    # ---- COMPLETE ----------------------------------------------------------
    elif command == "complete":
        todo_id = args["todo_id"]
        if not _looks_like_task_id(todo_id):
            return {
                "content": (
                    "❌ I couldn't identify that task ID. "
                    "Please use **show my tasks** and try again with the exact task ID."
                ),
                "metadata": {
                    "command": "complete",
                    "tool_result": {
                        "success": False,
                        "error": "Invalid task identifier",
                        "code": "INVALID_TASK_ID",
                    },
                },
            }

        result = await update_todo(
            user_id=user_id,
            todo_id=todo_id,
            status="completed",
            jwt_token=jwt_token,
        )
        if result.get("success"):
            todo = result.get("todo", {})
            title = todo.get("title", todo_id)
            return {
                "content": f"✅ Task **{title}** marked as completed!",
                "metadata": {"command": "complete", "tool_result": result},
            }
        err = result.get("error", "Unknown error")
        hint = (
            " Tip: use **show my tasks** to get the full task ID."
            if todo_id.isdigit()
            else ""
        )
        return {
            "content": f"❌ Could not complete task `{todo_id}`: {err}.{hint}",
            "metadata": {"command": "complete", "tool_result": result},
        }

    # ---- DELETE ------------------------------------------------------------
    elif command == "delete":
        todo_id = args["todo_id"]
        if not _looks_like_task_id(todo_id):
            return {
                "content": (
                    "❌ I couldn't identify that task ID. "
                    "Please use **show my tasks** and try again with the exact task ID."
                ),
                "metadata": {
                    "command": "delete",
                    "tool_result": {
                        "success": False,
                        "error": "Invalid task identifier",
                        "code": "INVALID_TASK_ID",
                    },
                },
            }

        result = await delete_todo(
            user_id=user_id,
            todo_id=todo_id,
            confirm=True,
            jwt_token=jwt_token,
        )
        if result.get("success"):
            return {
                "content": f"🗑️ Task `{todo_id}` deleted.",
                "metadata": {"command": "delete", "tool_result": result},
            }
        err = result.get("error", "Unknown error")
        return {
            "content": f"❌ Could not delete task `{todo_id}`: {err}",
            "metadata": {"command": "delete", "tool_result": result},
        }

    # Should never reach here
    return {"content": "❓ Unknown command.", "metadata": {"command": command}}


# ---------------------------------------------------------------------------
# Main /api/chat endpoint
# ---------------------------------------------------------------------------


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Process user chat message and return AI assistant response.

    Flow:
    1. Validate JWT → extract user_id
    2. Load recent chat history from storage
    3. Persist incoming user message
    4. [NEW] Try deterministic command parsing (add / show / complete / delete)
       - If matched → call MCP tool directly, skip LLM
    5. If no command matched → delegate to AI agent (LLM with function calling)
    6. Persist assistant reply
    7. Return ChatResponse JSON
    """
    # 1. Authenticate
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    storage = get_storage()

    # Auto-generate session_id when absent
    if not chat_request.session_id:
        import uuid, time
        chat_request.session_id = f"sess_{int(time.time())}_{str(uuid.uuid4())[:8]}"

    logger.info(
        f"Chat request - user_id: {user_id}, "
        f"session: {chat_request.session_id}, "
        f"msg_len: {len(chat_request.message)}"
    )

    try:
        # 2. Load history
        history = storage.load_chat_history(
            user_id=user_id,
            session_id=chat_request.session_id,
            limit=20,
        )
        formatted_history = [
            {
                "role": msg.get("role", "unknown"),
                "content": msg.get("content", ""),
                "metadata": msg.get("metadata", {}),
            }
            for msg in history
        ]

        # 3. Persist user message
        storage.save_message(
            user_id=user_id,
            session_id=chat_request.session_id,
            role="user",
            content=chat_request.message,
            metadata={
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        jwt_token = credentials.credentials

        # 4. Deterministic command parsing — fires BEFORE the LLM
        command, cmd_args = _parse_command(chat_request.message)

        if command is not None:
            logger.info(
                f"Command '{command}' matched args={cmd_args} for user {user_id}"
            )
            agent_response = await _execute_command(
                command, cmd_args, user_id, jwt_token
            )
        else:
            # 5. Freeform input → AI agent
            logger.info(
                f"No command matched for '{chat_request.message[:60]}', "
                f"delegating to AI agent (user={user_id})"
            )
            agent_response = await process_chat_message(
                user_id=user_id,
                session_id=chat_request.session_id,
                message=chat_request.message,
                history=formatted_history,
                jwt_token=jwt_token,
            )

        # 6. Persist assistant reply
        storage.save_message(
            user_id=user_id,
            session_id=chat_request.session_id,
            role="assistant",
            content=agent_response["content"],
            metadata=agent_response.get("metadata", {}),
        )

        logger.info(
            f"Chat response - user_id: {user_id}, "
            f"session: {chat_request.session_id}, "
            f"resp_len: {len(agent_response['content'])}"
        )

        # 7. Return
        return ChatResponse(
            response=agent_response["content"],
            session_id=chat_request.session_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error processing chat - user_id: {user_id}, "
            f"session: {chat_request.session_id}, "
            f"error: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message. Please try again.",
        )


# ---------------------------------------------------------------------------
# Supporting endpoints (unchanged in behaviour)
# ---------------------------------------------------------------------------


@router.post("/test")
async def test_chat(
    chat_request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Simple test endpoint that always works (no AI, no DB)."""
    return {
        "response": f"Echo: {chat_request.message}",
        "session_id": "test_session",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/sessions", response_model=list)
async def get_user_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get all conversation sessions for the authenticated user."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    storage = get_storage()
    sessions = storage.get_user_sessions(user_id)
    return sessions


@router.post("/session", response_model=dict)
async def create_or_resume_session(
    request: Request,
    session_id: str = Query(None, description="Session ID to resume, or None to create new"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Create a new session or resume existing one."""
    try:
        user_id = await verify_jwt_token(credentials)
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise

    storage = get_storage()

    if not session_id:
        import uuid
        session_id = (
            f"sess_{int(datetime.now(timezone.utc).timestamp())}_{str(uuid.uuid4())[:8]}"
        )

    storage.ensure_session_exists(user_id, session_id)

    logger.info(
        f"Session {'created' if not storage.session_exists(user_id, session_id) else 'resumed'}"
        f" - user_id: {user_id}, session: {session_id}"
    )

    return {
        "session_id": session_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
