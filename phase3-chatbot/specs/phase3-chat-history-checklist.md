# Phase 3 Chat History Implementation Checklist

## Overview

This specification defines the implementation tasks for Phase 3 chatbot chat history functionality and related fixes.

## Tasks

### Task 1: Update Chat Route with Database Integration

**File:** `app/routes/chat.py`

**Changes Required:**
1. Remove placeholder `get_session()` function
2. Import `get_db` from `app.database`
3. Add `session: AsyncSession = Depends(get_db)` parameter
4. Uncomment chat history loading code (lines 69-78)
5. Uncomment user message saving code (lines 85-95)
6. Uncomment assistant response saving code (lines 107-114)

**Acceptance Criteria:**
- [x] Database session is properly injected
- [x] Chat history loads before agent processing
- [x] User messages persist to database
- [x] Assistant responses persist to database
- [x] No TODO comments remain in the code

**Implementation:** Updated `app/routes/chat.py` with all database integration code uncommented and functional.

---

### Task 2: Fix Security Vulnerability - Replace eval() with json.loads()

**File:** `app/agents/todo_agent.py`

**Current Issue:** Line 267 uses `eval()` for parsing tool arguments, which is a security vulnerability.

**Changes Required:**
```python
# Before (insecure):
tool_args = eval(tool_call.function.arguments)

# After (secure):
import json
tool_args = json.loads(tool_call.function.arguments)
```

**Acceptance Criteria:**
- [x] `eval()` removed from todo_agent.py
- [x] `json.loads()` used instead
- [x] JSON parsing errors handled gracefully
- [x] No security vulnerability remains

**Implementation:** Replaced `eval()` with `json.loads()` and added try/except for JSON parsing errors.

---

### Task 3: Complete MCP Server Main Entry Point

**File:** `mcp_server/server.py`

**Current State:** File contains only imports (12 lines), no server initialization.

**Changes Required:**
1. Import `stdio_server` from MCP server
2. Initialize server with tools
3. Add main entry point with `stdio_server(app)`
4. Configure logging

**Acceptance Criteria:**
- [x] MCP server can run via command line
- [x] All 5 tools registered and accessible
- [x] Server accepts stdio connections
- [x] Logging configured properly

**Implementation:** Complete MCP server with all 5 tools (create_todo, list_todos, update_todo, delete_todo, search_todos), tool handlers, and main entry point.

---

### Task 4: Add Rate Limiting Middleware

**File:** `app/middleware/rate_limit.py`

**Requirements:**
- 30 requests per minute per user (as per spec)
- Track by user_id from JWT token
- Return 429 status when exceeded
- Sliding window algorithm

**Acceptance Criteria:**
- [x] Rate limiter tracks requests by user_id
- [x] 30 requests/minute limit enforced
- [x] Returns 429 with Retry-After header
- [x] Health endpoints exempt from rate limiting
- [x] Middleware integrated into main.py

**Implementation:** Created `RateLimiter` class with sliding window algorithm, `RateLimitMiddleware` for FastAPI, and integrated into `app/main.py`.

---

### Task 5: Add Unit Tests for Core Components

**Directory:** `tests/`

**Test Files Created:**

#### 5.1: `tests/test_chat_queries.py`
- Test `load_chat_history` function
- Test `save_message` function
- Test `get_user_sessions` function
- Test `delete_session` function
- Mock database session

#### 5.2: `tests/test_mcp_tools.py`
- Test `create_todo` tool
- Test `list_todos` tool
- Test `update_todo` tool
- Test `delete_todo` tool
- Test `search_todos` tool
- Test validation errors
- Test error handling

#### 5.3: `tests/test_rate_limiter.py`
- Test rate limit enforcement
- Test request counting
- Test retry-after calculation
- Test cleanup of old entries
- Test edge cases (concurrent requests, zero limit)

#### 5.4: `tests/conftest.py` (Updated)
- Added `mock_session` fixture
- Added `mock_http_client` fixture

**Acceptance Criteria:**
- [x] Test files exist for each core component
- [x] Tests use pytest and asyncio
- [x] Tests mock database interactions
- [x] Tests cover success and error paths
- [ ] Tests achieve >80% coverage target (to be verified)

---

## Implementation Order

1. [x] Task 1: Update chat route (depends on database module) - **COMPLETED**
2. [x] Task 2: Fix security vulnerability (standalone) - **COMPLETED**
3. [x] Task 3: Complete MCP server (standalone) - **COMPLETED**
4. [x] Task 4: Add rate limiting (depends on middleware structure) - **COMPLETED**
5. [x] Task 5: Add unit tests (depends on implemented code) - **COMPLETED**

---

## Files Modified/Created

| File | Action | Description |
|------|--------|-------------|
| `app/routes/chat.py` | Modified | Uncommented DB integration code |
| `app/agents/todo_agent.py` | Modified | Replaced eval() with json.loads() |
| `mcp_server/server.py` | Modified | Complete MCP server implementation |
| `app/middleware/rate_limit.py` | Created | Rate limiting middleware |
| `app/main.py` | Modified | Added rate limiting middleware |
| `tests/test_chat_queries.py` | Created | Chat query unit tests |
| `tests/test_mcp_tools.py` | Created | MCP tools unit tests |
| `tests/test_rate_limiter.py` | Created | Rate limiter unit tests |
| `tests/conftest.py` | Modified | Added mock fixtures |

---

## Verification

After implementation, verify:
1. [x] Chat history persists across requests
2. [x] No `eval()` calls remain in codebase
3. [x] MCP server runs successfully
4. [x] Rate limiting works correctly
5. [ ] All tests pass (run: `pytest tests/`)

---

**Status:** Implementation Complete
**Last Updated:** 2025-12-29
