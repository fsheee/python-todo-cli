# Prompt History - Phase 3 Chatbot

> Auto-logged user instructions for audit, context reuse, and collaboration.

---

## Session: 2026-01-02

### PHR-001: Initial Phase 3 Debugging Session
**Timestamp:** 2026-01-02T01:00:00Z
**Type:** Debugging

User reported Phase 2 and Phase 3 were working 2 days ago but showed errors last night.

**Investigation:** Checked git history and identified model rename from `Task` to `Todo` in Phase 2 backend causing NameError.

**Output:** Identified root cause in Phase 2 backend (fixed in Phase 2 PHR-008)

---

### PHR-002: Configure OpenRouter Integration
**Timestamp:** 2026-01-02T01:45:00Z
**Type:** Configuration

User wanted to use OpenRouter API instead of OpenAI for cost savings (free Mistral model).

**Context:** Phase 3 .env had placeholder OpenAI key `sk-your-api-key-here`

**Output:** Configured `app/agents/todo_agent.py` to support both OpenAI and OpenRouter:
- Added OPEN_ROUTER_API_KEY environment variable support
- Added BASE_URL configuration for OpenRouter endpoint
- Added model_name configuration (default: `mistralai/devstral-2512:free`)
- OpenRouter client uses same AsyncOpenAI interface (OpenAI-compatible)
- Automatic fallback to OpenAI if OpenRouter key not provided

**Configuration Added:**
```python
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")

if OPEN_ROUTER_API_KEY:
    openai_client = AsyncOpenAI(
        api_key=OPEN_ROUTER_API_KEY,
        base_url=BASE_URL
    )
    logger.info("Using OpenRouter API for AI requests")
else:
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("Using OpenAI API for AI requests")

AGENT_MODEL = os.getenv("model_name", "mistralai/devstral-2512:free")
```

**Related Files:**
- `phase3-chatbot/app/agents/todo_agent.py` (lines 28-48)
- `phase3-chatbot/.env`

**References:**
- OpenRouter provides OpenAI-compatible API
- Mistral Devstral 2512 model available for free

---

### PHR-003: Fix MCP Authentication Chain
**Timestamp:** 2026-01-02T02:00:00Z
**Type:** Bug Fix

Fixed 401 Unauthorized errors when MCP tools called Phase 2 backend.

**Context:** MCP tools were using internal service token instead of user JWT token, causing Phase 2 backend to reject requests.

**Root Cause:** JWT token not passed through the chain:
1. Frontend sends JWT in Authorization header
2. Phase 3 chat.py receives JWT but didn't pass to agent
3. Agent didn't pass JWT to MCP tools
4. MCP tools used service token instead of user JWT
5. Phase 2 backend rejected with 401

**Solution - JWT Token Passing Chain:**

**Step 1:** Update chat.py to extract and pass JWT token
```python
# app/routes/chat.py:84-92
jwt_token = credentials.credentials
agent_response = await process_chat_message(
    user_id=user_id,
    session_id=chat_request.session_id,
    message=chat_request.message,
    history=formatted_history,
    jwt_token=jwt_token  # Pass JWT to agent
)
```

**Step 2:** Update agent to accept and pass JWT to tools
```python
# app/agents/todo_agent.py:56
async def process_chat_message(
    user_id: int,
    session_id: str,
    message: str,
    history: List[Dict],
    jwt_token: str = "",  # Accept JWT token
    ...
)

# app/agents/todo_agent.py:298-305
tool_args_with_auth = {
    **tool_args,
    "user_id": user_id,  # Override with real UUID
    "jwt_token": jwt_token  # Pass JWT to tools
}
```

**Step 3:** Update MCP client to accept JWT token
```python
# mcp_server/client.py:16-34
def __init__(self, jwt_token: Optional[str] = None):
    auth_header = f"Bearer {jwt_token}" if jwt_token else f"Bearer {config.INTERNAL_SERVICE_TOKEN}"

    self.client = httpx.AsyncClient(
        base_url=config.PHASE2_API_URL,
        headers={
            "Authorization": auth_header,
            "X-Internal-Service": "mcp-server",
            "Content-Type": "application/json"
        }
    )
```

**Step 4:** Update MCP tools to accept jwt_token parameter
- `mcp_server/tools/create_todo.py` - Added jwt_token parameter
- `mcp_server/tools/list_todos.py` - Added jwt_token parameter
- `mcp_server/tools/update_todo.py` - Added jwt_token parameter
- `mcp_server/tools/delete_todo.py` - Added jwt_token parameter
- `mcp_server/tools/search_todos.py` - Added jwt_token parameter

**Related Files:**
- `phase3-chatbot/app/routes/chat.py`
- `phase3-chatbot/app/agents/todo_agent.py`
- `phase3-chatbot/mcp_server/client.py`
- `phase3-chatbot/mcp_server/tools/*.py`

**Outcome:** MCP tools now successfully authenticate with Phase 2 backend using user JWT tokens

---

### PHR-004: Fix MCP Tool Endpoint Format
**Timestamp:** 2026-01-02T02:20:00Z
**Type:** Bug Fix

Fixed 404 Not Found errors - MCP tools were calling wrong endpoint format.

**Problem:** MCP tools called `/todos` but Phase 2 backend uses `/api/{user_id}/tasks`

**Solution:** Updated endpoint format in all MCP tools:
```python
# Before
response = await client.client.post("/todos", json=payload)

# After
user_id_str = str(user_id)
response = await client.client.post(f"/api/{user_id_str}/tasks", json=payload)
```

**Changes:**
- `create_todo.py` - Line 92: Changed to `/api/{user_id_str}/tasks`
- `list_todos.py` - Line 123: Changed to `/api/{user_id_str}/tasks`
- `update_todo.py` - Changed endpoint format
- `delete_todo.py` - Changed endpoint format

**Related Files:**
- `phase3-chatbot/mcp_server/tools/create_todo.py`
- `phase3-chatbot/mcp_server/tools/list_todos.py`

**References:**
- Phase 2 REST API spec: `/api/{user_id}/tasks`

---

### PHR-005: Fix MCP Tool Payload Schema
**Timestamp:** 2026-01-02T02:30:00Z
**Type:** Bug Fix

Fixed 422 Unprocessable Content errors - MCP tools sending unsupported fields to Phase 2 backend.

**Problem:** Phase 2 TaskCreate schema only accepts `title` and `description`, but MCP tools were sending `user_id`, `status`, `priority`, `due_date`.

**Solution:** Updated create_todo to only send supported fields:
```python
# mcp_server/tools/create_todo.py:78-86
# Phase 2 TaskCreate schema only accepts title and description
payload = {
    "title": title.strip()
}

if description:
    payload["description"] = description.strip()

# Note: priority and due_date are not supported by Phase 2 backend yet
```

**Removed from payload:**
- `user_id` (comes from JWT token, not request body)
- `status` (automatically set to "pending" by backend)
- `priority` (not yet supported in Phase 2 schema)
- `due_date` (not yet supported in Phase 2 schema)

**Related Files:**
- `phase3-chatbot/mcp_server/tools/create_todo.py` (lines 78-93)

**References:**
- Phase 2 TaskCreate schema in `phase2-web/backend/models.py`

---

### PHR-006: Fix UUID vs Integer User ID Mismatch
**Timestamp:** 2026-01-02T02:40:00Z
**Type:** Bug Fix

Fixed AI generating integer user_ids instead of using UUID from JWT token.

**Problem:**
- AI was generating random integers (6, 654321) for user_id parameter
- Phase 2 backend expects UUID strings
- JWT token contains correct UUID but AI didn't use it

**Solution:** Override user_id in tool calls with actual UUID from JWT:
```python
# app/agents/todo_agent.py:298-305
tool_args_with_auth = {
    **tool_args,
    "user_id": user_id,  # Use actual UUID user_id from JWT, not AI-generated number
    "jwt_token": jwt_token
}
tool_result = await tool_map[tool_name](**tool_args_with_auth)
```

**Also updated MCP tools to accept both int and str:**
```python
# mcp_server/tools/create_todo.py:16
async def create_todo(
    user_id: Union[int, str],  # Accept both int and UUID string
    ...
)
```

**Related Files:**
- `phase3-chatbot/app/agents/todo_agent.py` (lines 298-305)
- `phase3-chatbot/mcp_server/tools/create_todo.py` (line 16)
- `phase3-chatbot/mcp_server/tools/list_todos.py` (line 46)

**Outcome:** MCP tools now use correct UUID from JWT token instead of AI-generated integers

---

### PHR-007: Fix AI Response Generation After Tool Calls
**Timestamp:** 2026-01-02T03:00:00Z
**Type:** Enhancement

Fixed generic "I've processed your request" responses after tool execution.

**Problem:** After calling MCP tools, AI returned generic message instead of natural language response about the action taken.

**Root Cause:** OpenAI function calling returns empty `assistant_message.content` after tool execution. Need second API call with tool results to generate proper response.

**Solution:** Implemented two-step API call process:

**Step 1 - Tool Selection (First API Call):**
```python
# app/agents/todo_agent.py:250-256
response = await openai_client.chat.completions.create(
    model=AGENT_MODEL,
    messages=messages,
    tools=tools,  # AI decides which tool to call
    temperature=AGENT_TEMPERATURE,
    max_tokens=AGENT_MAX_TOKENS
)
```

**Step 2 - Response Generation (Second API Call):**
```python
# app/agents/todo_agent.py:314-348
if tool_calls_made:
    # Add assistant message with tool calls
    messages.append({
        "role": "assistant",
        "content": assistant_message.content,
        "tool_calls": [...]
    })

    # Add tool results
    for i, tool_call in enumerate(assistant_message.tool_calls):
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_calls_made[i]["result"])
        })

    # Get final response with tool results
    final_response = await openai_client.chat.completions.create(
        model=AGENT_MODEL,
        messages=messages,  # Now includes tool results
        temperature=AGENT_TEMPERATURE,
        max_tokens=AGENT_MAX_TOKENS
    )

    response_content = final_response.choices[0].message.content
```

**Related Files:**
- `phase3-chatbot/app/agents/todo_agent.py` (lines 312-354)

**Outcome:**
- Before: "I've processed your request"
- After: "I've added 'buy fruits' to your task list!"

**References:**
- OpenAI function calling documentation
- Two-step process: (1) tool selection, (2) response generation

---

### PHR-008: Fix Task List Parsing from Phase 2 Response
**Timestamp:** 2026-01-02T03:15:00Z
**Type:** Bug Fix

Fixed empty task list display despite tasks existing in database.

**Problem:**
- Tasks were successfully created in database (verified via direct curl)
- "Show my tasks" command returned empty list
- MCP list_todos tool was looking for "todos" key but Phase 2 returns "tasks" key

**Root Cause:** Response parsing mismatch:
```python
# Before - only checked for "todos" key
todos = data.get("todos", [])

# Phase 2 actually returns
{"tasks": [...], "count": 5}
```

**Solution:** Updated list_todos to check both keys:
```python
# mcp_server/tools/list_todos.py:125-136
if response.status_code == 200:
    data = response.json()
    # Phase 2 backend returns {"tasks": [...], "count": N}
    todos = data if isinstance(data, list) else data.get("tasks", data.get("todos", []))

    return {
        "success": True,
        "todos": todos,  # Return as "todos" for consistency with MCP interface
        "count": len(todos),
        "total": data.get("total", data.get("count", len(todos))) if isinstance(data, dict) else len(todos),
        "has_more": len(todos) == limit
    }
```

**Related Files:**
- `phase3-chatbot/mcp_server/tools/list_todos.py` (lines 125-136)

**Outcome:** "Show my tasks" now correctly displays all 5 tasks from database

---

### PHR-009: Architecture Documentation - MCP Server Explanation
**Timestamp:** 2026-01-02T03:30:00Z
**Type:** Documentation

User requested explanation of how chatbot works using MCP server.

**Output:** Provided comprehensive documentation of MCP architecture:

1. **Overall Architecture Flow:**
   - User (Browser) → Phase 3 Backend → AI Agent → MCP Tools → Phase 2 Backend → Database

2. **Request Flow (9 Steps):**
   - Step 1: User sends message with JWT token
   - Step 2: Extract JWT and call agent
   - Step 3: AI Agent processes message
   - Step 4: OpenAI Function Calling (First API Call)
   - Step 5: Execute MCP Tool
   - Step 6: MCP Tool calls Phase 2 Backend
   - Step 7: Phase 2 validates JWT and creates task
   - Step 8: Generate Natural Language Response (Second API Call)
   - Step 9: Return response to user

3. **Key Components:**
   - MCP Tools act as bridge between AI and backend
   - Authentication chain passes JWT through entire flow
   - Two-step AI process: (1) tool selection, (2) response generation

4. **Benefits of MCP Architecture:**
   - Separation of Concerns (AI logic vs business logic)
   - Reusability (MCP tools used by multiple agents)
   - Security (JWT validation in Phase 2)
   - Type Safety (MCP tools validate inputs)
   - Error Handling (MCP tools catch and format errors)

**Related Files:**
- All Phase 3 chatbot files
- Documentation provided in conversation

**References:**
- Model Context Protocol (MCP) design pattern
- OpenAI function calling documentation

---

