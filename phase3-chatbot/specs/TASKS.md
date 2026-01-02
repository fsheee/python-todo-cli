# Phase 3 Implementation Tasks

## 🎯 Overview

This document breaks down the implementation plan into atomic, testable tasks. Each task is small, deterministic, and directly traceable to specifications.

**Status:** Ready for implementation via Claude Code
**Total Tasks:** 85 tasks across 7 phases
**Estimated Effort:** 2-3 weeks with automated implementation

---

## 📋 Task Format

Each task follows this structure:
```
### Task ID: [PHASE]-[NUMBER]

**Description:** [What to build]
**Spec Reference:** [Which spec file]
**Dependencies:** [Previous tasks required]
**Acceptance Criteria:**
- [x] Criterion 1
- [x] Criterion 2

**Test Cases:**
- TC-X: [Test description]
```

---

## Phase 1: Database Foundation (8 tasks)

### Task 1.1: Create Database Migration for ChatHistory Table ✅

**Description:** Create Alembic migration file to add chat_history table with all required fields and constraints.

**Spec Reference:** `specs/database/chat-history.md` - Schema Definition

**Dependencies:** None (first task)

**Acceptance Criteria:**
- [x] Migration file created in `migrations/versions/003_create_chat_history.py`
- [x] Table definition includes all 8 fields (id, user_id, session_id, role, content, metadata, timestamp, is_deleted)
- [x] Foreign key to users table with ON DELETE CASCADE
- [x] CHECK constraint on role field (user/assistant/system)
- [x] Default values for timestamp and is_deleted
- [x] Migration runs successfully with `alembic upgrade head`
- [x] Migration can be rolled back with `alembic downgrade -1`

**Test Cases:**
- TC-1.1.1: Run migration on clean database - succeeds
- TC-1.1.2: Rollback migration - succeeds
- TC-1.1.3: Verify foreign key constraint - cascades on user delete
- TC-1.1.4: Verify role CHECK constraint - rejects invalid values

---

### Task 1.2: Create Database Indexes for ChatHistory ✅

**Description:** Create performance indexes for common query patterns on chat_history table.

**Spec Reference:** `specs/database/chat-history.md` - Indexing Strategy

**Dependencies:** Task 1.1

**Acceptance Criteria:**
- [x] Index on user_id created
- [x] Index on session_id created
- [x] Index on timestamp created
- [x] Composite index on (user_id, session_id, is_deleted, timestamp DESC) created
- [x] All indexes created successfully
- [x] Query planner uses indexes (verify with EXPLAIN ANALYZE)

**Test Cases:**
- TC-1.2.1: Query by user_id - uses index
- TC-1.2.2: Query by session_id - uses index
- TC-1.2.3: Query with user_id + session_id - uses composite index
- TC-1.2.4: Sort by timestamp DESC - uses index

---

### Task 1.3: Define ChatHistory SQLModel ✅

**Description:** Create SQLModel class for ChatHistory with proper field types and validation.

**Spec Reference:** `specs/database/chat-history.md` - SQLModel Model

**Dependencies:** Task 1.1

**Acceptance Criteria:**
- [x] ChatHistory class defined in `app/models/chat_history.py`
- [x] All fields properly typed (int, str, datetime, Dict, bool)
- [x] Field constraints match database schema (max_length, nullable)
- [x] Foreign key relationship to User model
- [x] JSON/JSONB column for metadata field
- [x] Default factories for timestamp and is_deleted
- [x] Model validates correctly

**Test Cases:**
- TC-1.3.1: Create instance with all fields - succeeds
- TC-1.3.2: Create instance with minimal fields - succeeds
- TC-1.3.3: Invalid role value - validation fails
- TC-1.3.4: Metadata as dict - serializes to JSON correctly

---

### Task 1.4: Implement load_chat_history Query Function ✅

**Description:** Create async function to load recent chat messages for a user session.

**Spec Reference:** `specs/database/chat-history.md` - Query 1

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [x] Function signature: `async def load_chat_history(session, user_id, session_id, limit=20) -> list[ChatHistory]`
- [x] Filters by user_id, session_id, and is_deleted=False
- [x] Orders by timestamp DESC
- [x] Limits to specified number of messages
- [x] Returns messages in chronological order (oldest first)
- [x] Returns empty list if no messages found

**Test Cases:**
- TC-1.4.1: Load 5 messages from session with 10 - returns 5 most recent
- TC-1.4.2: Load from empty session - returns empty list
- TC-1.4.3: Load with limit=20 from session with 25 - returns last 20
- TC-1.4.4: User A cannot load User B's messages - returns empty
- TC-1.4.5: Soft-deleted messages excluded from results

---

### Task 1.5: Implement save_message Mutation Function ✅

**Description:** Create async function to save a new chat message to database.

**Spec Reference:** `specs/database/chat-history.md` - Query 2

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [x] Function signature: `async def save_message(session, user_id, session_id, role, content, metadata=None) -> ChatHistory`
- [x] Creates new ChatHistory instance
- [x] Sets timestamp automatically
- [x] Commits to database
- [x] Refreshes instance to get generated ID
- [x] Returns saved message with ID

**Test Cases:**
- TC-1.5.1: Save user message - succeeds, returns ID
- TC-1.5.2: Save assistant message with metadata - succeeds
- TC-1.5.3: Save without metadata - succeeds with None
- TC-1.5.4: Timestamp auto-generated - within 1 second of now
- TC-1.5.5: Invalid user_id - foreign key error

---

### Task 1.6: Implement get_user_sessions Query Function ✅

**Description:** Create async function to retrieve all sessions for a user with summary info.

**Spec Reference:** `specs/database/chat-history.md` - Query 3

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [x] Function signature: `async def get_user_sessions(session, user_id, limit=50) -> list[Dict]`
- [x] Groups by session_id
- [x] Aggregates: MIN(timestamp) as started_at, MAX(timestamp) as last_message_at, COUNT(*) as message_count
- [x] Filters is_deleted=False
- [x] Orders by last_message_at DESC
- [x] Returns list of dicts with session metadata

**Test Cases:**
- TC-1.6.1: User with 3 sessions - returns 3 summaries
- TC-1.6.2: Each summary has started_at, last_message_at, message_count
- TC-1.6.3: Ordered by most recent first
- TC-1.6.4: User with no sessions - returns empty list
- TC-1.6.5: Limit works correctly

---

### Task 1.7: Implement delete_session Soft Delete Function ✅

**Description:** Create async function to soft delete all messages in a session.

**Spec Reference:** `specs/database/chat-history.md` - Query 4

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [x] Function signature: `async def delete_session(session, user_id, session_id) -> int`
- [x] Updates is_deleted=True for all matching messages
- [x] Filters by user_id and session_id
- [x] Only affects messages where is_deleted=False
- [x] Returns count of deleted messages
- [x] Commits transaction

**Test Cases:**
- TC-1.7.1: Delete session with 10 messages - returns 10
- TC-1.7.2: Messages no longer appear in load_chat_history
- TC-1.7.3: Delete non-existent session - returns 0
- TC-1.7.4: User A cannot delete User B's session - returns 0
- TC-1.7.5: Double delete same session - second returns 0

---

### Task 1.8: Implement cleanup_old_deleted_sessions Maintenance Function ✅

**Description:** Create async function to permanently delete old soft-deleted messages.

**Spec Reference:** `specs/database/chat-history.md` - Query 6

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [x] Function signature: `async def cleanup_old_deleted_sessions(session, days=90) -> int`
- [x] Calculates cutoff date (now - days)
- [x] Deletes messages where is_deleted=True AND timestamp < cutoff
- [x] Returns count of permanently deleted messages
- [x] Commits transaction

**Test Cases:**
- TC-1.8.1: Delete messages older than 90 days - succeeds
- TC-1.8.2: Recent deleted messages preserved
- TC-1.8.3: Non-deleted old messages preserved
- TC-1.8.4: Returns correct count
- TC-1.8.5: No messages to delete - returns 0

---

## Phase 2: MCP Server Foundation (12 tasks)

### Task 2.1: Set Up MCP Server Project Structure

**Description:** Initialize MCP server project with Official MCP SDK and dependencies.

**Spec Reference:** `specs/api/mcp-tools.md` - MCP Server Setup

**Dependencies:** None

**Acceptance Criteria:**
- [x] Directory created: `mcp_server/`
- [x] Install mcp-sdk package
- [x] Install httpx for HTTP calls
- [x] Create `mcp_server/__init__.py`
- [x] Create `mcp_server/server.py` (main file)
- [x] Create `mcp_server/config.py` for configuration
- [x] Create `requirements.txt` with dependencies
- [x] Server can be imported successfully

**Test Cases:**
- TC-2.1.1: Import mcp_server - succeeds
- TC-2.1.2: All dependencies installed - import succeeds
- TC-2.1.3: Config loads environment variables

---

### Task 2.2: Initialize MCP Server Instance

**Description:** Create base MCP server instance and configure connection protocol.

**Spec Reference:** `specs/api/mcp-tools.md` - Server Setup

**Dependencies:** Task 2.1

**Acceptance Criteria:**
- [x] Server instance created with name "todo-mcp-server"
- [x] STDIO protocol configured
- [x] Server can start successfully
- [x] Server can be stopped gracefully
- [x] Logging configured (INFO level)

**Test Cases:**
- TC-2.2.1: Start server - succeeds without errors
- TC-2.2.2: Server accepts tool registration
- TC-2.2.3: Server logs startup message
- TC-2.2.4: Stop server - cleanup complete

---

### Task 2.3: Configure MCP Server Environment

**Description:** Set up environment variables and configuration for MCP server.

**Spec Reference:** `specs/api/mcp-tools.md` - Configuration

**Dependencies:** Task 2.1

**Acceptance Criteria:**
- [x] Environment variables defined: PHASE2_API_URL, INTERNAL_SERVICE_TOKEN
- [x] Config class loads from environment
- [x] Default values for development
- [x] Validation for required variables
- [x] HTTP client timeout configurable

**Test Cases:**
- TC-2.3.1: Load config with all env vars - succeeds
- TC-2.3.2: Missing required var - raises error
- TC-2.3.3: Default values used when optional vars missing
- TC-2.3.4: Config accessible from tools

---

### Task 2.4: Create HTTP Client for Phase 2 Backend

**Description:** Set up async HTTP client to communicate with Phase 2 backend.

**Spec Reference:** `specs/api/mcp-tools.md` - Service Authentication

**Dependencies:** Task 2.3

**Acceptance Criteria:**
- [x] httpx.AsyncClient created with connection pooling
- [x] Service token added to Authorization header
- [x] X-Internal-Service header added
- [x] Timeout configured (30 seconds)
- [x] Connection reuse enabled
- [x] Client can be closed properly

**Test Cases:**
- TC-2.4.1: Create client - succeeds
- TC-2.4.2: Headers include service token
- TC-2.4.3: Timeout works correctly
- TC-2.4.4: Connection pooling active

---

### Task 2.5: Implement create_todo MCP Tool

**Description:** Create MCP tool to create a new todo item.

**Spec Reference:** `specs/api/mcp-tools.md` - Tool 1: create_todo

**Dependencies:** Task 2.2, Task 2.4

**Acceptance Criteria:**
- [x] Tool registered with @mcp_server.tool() decorator
- [x] Input schema: user_id (int), title (str), description (str?), priority (str?), due_date (str?)
- [x] Input validation: user_id > 0, title non-empty, max 200 chars
- [x] Priority validation: must be low/medium/high or None
- [x] HTTP POST to Phase 2: /todos
- [x] Returns {success: bool, todo: dict, message: str}
- [x] Error handling for all failure cases

**Test Cases:**
- TC-2.5.1: Create with title only - succeeds
- TC-2.5.2: Create with all fields - succeeds
- TC-2.5.3: Empty title - returns VALIDATION_ERROR
- TC-2.5.4: Invalid priority - returns VALIDATION_ERROR
- TC-2.5.5: Phase 2 backend down - returns BACKEND_ERROR
- TC-2.5.6: Title too long (>200 chars) - returns VALIDATION_ERROR

---

### Task 2.6: Implement list_todos MCP Tool

**Description:** Create MCP tool to retrieve todos with optional filters.

**Spec Reference:** `specs/api/mcp-tools.md` - Tool 2: list_todos

**Dependencies:** Task 2.2, Task 2.4

**Acceptance Criteria:**
- [x] Tool registered with @mcp_server.tool() decorator
- [x] Input schema: user_id (int), status (str?), priority (str?), due_date (str?), due_date_range (str?), limit (int), offset (int)
- [x] Date range conversion: today/tomorrow/this_week/next_week/overdue → actual dates
- [x] HTTP GET to Phase 2: /todos with query parameters
- [x] Returns {success: bool, todos: list, count: int, total: int, has_more: bool}
- [x] Handles empty results gracefully

**Test Cases:**
- TC-2.6.1: List all pending - succeeds
- TC-2.6.2: Filter by status - correct results
- TC-2.6.3: Filter by priority - correct results
- TC-2.6.4: Filter by due_date_range="today" - correct conversion
- TC-2.6.5: Empty result set - returns empty array
- TC-2.6.6: Pagination with limit and offset - works correctly

---

### Task 2.7: Implement update_todo MCP Tool

**Description:** Create MCP tool to update an existing todo.

**Spec Reference:** `specs/api/mcp-tools.md` - Tool 3: update_todo

**Dependencies:** Task 2.2, Task 2.4

**Acceptance Criteria:**
- [x] Tool registered with @mcp_server.tool() decorator
- [x] Input schema: user_id (int), todo_id (int), title (str?), description (str?), status (str?), priority (str?), due_date (str?)
- [x] Validation: at least one field to update
- [x] Validation: title not empty if provided
- [x] HTTP PUT to Phase 2: /todos/{todo_id}
- [x] Returns {success: bool, todo: dict, message: str, changes: list}
- [x] Tracks which fields were changed

**Test Cases:**
- TC-2.7.1: Update single field - succeeds
- TC-2.7.2: Update multiple fields - succeeds
- TC-2.7.3: No fields provided - returns VALIDATION_ERROR
- TC-2.7.4: Todo not found - returns NOT_FOUND
- TC-2.7.5: Empty title - returns VALIDATION_ERROR
- TC-2.7.6: Changes list populated correctly

---

### Task 2.8: Implement delete_todo MCP Tool

**Description:** Create MCP tool to delete a todo with confirmation.

**Spec Reference:** `specs/api/mcp-tools.md` - Tool 4: delete_todo

**Dependencies:** Task 2.2, Task 2.4

**Acceptance Criteria:**
- [x] Tool registered with @mcp_server.tool() decorator
- [x] Input schema: user_id (int), todo_id (int), confirm (bool)
- [x] Validation: confirm must be True explicitly
- [x] Fetch todo first to get details
- [x] HTTP DELETE to Phase 2: /todos/{todo_id}
- [x] Returns {success: bool, deleted_todo: dict, message: str}
- [x] Returns CONFIRMATION_REQUIRED if confirm=False

**Test Cases:**
- TC-2.8.1: Delete without confirmation - returns CONFIRMATION_REQUIRED
- TC-2.8.2: Delete with confirmation - succeeds
- TC-2.8.3: Todo not found - returns NOT_FOUND
- TC-2.8.4: Returns deleted todo details
- TC-2.8.5: User A cannot delete User B's todo - returns NOT_FOUND

---

### Task 2.9: Implement search_todos MCP Tool

**Description:** Create MCP tool to search todos by keyword.

**Spec Reference:** `specs/api/mcp-tools.md` - Tool 5: search_todos

**Dependencies:** Task 2.2, Task 2.4

**Acceptance Criteria:**
- [x] Tool registered with @mcp_server.tool() decorator
- [x] Input schema: user_id (int), query (str), status (str?), limit (int)
- [x] Validation: query non-empty, max 100 chars
- [x] Query sanitization to prevent injection
- [x] HTTP GET to Phase 2: /todos/search?q={query}&user_id={user_id}
- [x] Returns {success: bool, todos: list, count: int, query: str}
- [x] Handles no results gracefully

**Test Cases:**
- TC-2.9.1: Search with results - returns matching todos
- TC-2.9.2: Search with no results - returns empty array
- TC-2.9.3: Empty query - returns VALIDATION_ERROR
- TC-2.9.4: Query too long - truncates or errors
- TC-2.9.5: Filter by status - combines with search
- TC-2.9.6: Limit parameter works correctly

---

### Task 2.10: Add Input Validation to All MCP Tools

**Description:** Implement comprehensive input validation for all MCP tools.

**Spec Reference:** `specs/api/mcp-tools.md` - Validation Rules

**Dependencies:** Tasks 2.5-2.9

**Acceptance Criteria:**
- [x] user_id validation: positive integer
- [x] todo_id validation: positive integer
- [x] title validation: non-empty, max length
- [x] priority validation: enum check
- [x] status validation: enum check
- [x] date validation: ISO 8601 format
- [x] Returns consistent error format

**Test Cases:**
- TC-2.10.1: Invalid user_id (negative) - validation error
- TC-2.10.2: Invalid priority (typo) - validation error
- TC-2.10.3: Invalid date format - validation error
- TC-2.10.4: All validations enforced consistently

---

### Task 2.11: Add Error Handling to All MCP Tools

**Description:** Implement comprehensive error handling and standardized error responses.

**Spec Reference:** `specs/api/mcp-tools.md` - Error Codes

**Dependencies:** Tasks 2.5-2.9

**Acceptance Criteria:**
- [x] Try-catch blocks around all HTTP calls
- [x] Backend timeout handling (30s)
- [x] Backend unavailable handling
- [x] Network error handling
- [x] Standardized error response format
- [x] Error codes: VALIDATION_ERROR, NOT_FOUND, BACKEND_ERROR, TIMEOUT, INTERNAL_ERROR

**Test Cases:**
- TC-2.11.1: Backend timeout - returns TIMEOUT error
- TC-2.11.2: Backend 500 error - returns BACKEND_ERROR
- TC-2.11.3: Network error - returns SERVICE_UNAVAILABLE
- TC-2.11.4: All errors return consistent format
- TC-2.11.5: Error messages are user-friendly

---

### Task 2.12: Write Unit Tests for All MCP Tools

**Description:** Create comprehensive unit tests for all 5 MCP tools.

**Spec Reference:** `specs/api/mcp-tools.md` - Testing Strategy

**Dependencies:** Tasks 2.5-2.11

**Acceptance Criteria:**
- [x] Test file: `tests/test_mcp_tools.py`
- [x] Mock HTTP client for Phase 2 calls
- [x] Test all success paths
- [x] Test all error paths
- [x] Test input validation
- [x] >95% code coverage for MCP tools

**Test Cases:**
- TC-2.12.1: All tools have success tests
- TC-2.12.2: All tools have validation tests
- TC-2.12.3: All tools have error handling tests
- TC-2.12.4: Tests run successfully with pytest
- TC-2.12.5: Coverage report shows >95%

---

## Phase 3: AI Agent Implementation (15 tasks)

### Task 3.1: Set Up OpenAI Agents SDK

**Description:** Initialize OpenAI Agents SDK and configure authentication.

**Spec Reference:** `specs/agents/todo-agent.md` - Agent Configuration

**Dependencies:** None

**Acceptance Criteria:**
- [x] Install openai package (latest version)
- [x] Create `app/agents/` directory
- [x] Create `app/agents/__init__.py`
- [x] Environment variable: OPENAI_API_KEY
- [x] OpenAI client initialized successfully
- [x] API key validated (test connection)

**Test Cases:**
- TC-3.1.1: Import openai - succeeds
- TC-3.1.2: API key loaded from environment
- TC-3.1.3: Test API call succeeds
- TC-3.1.4: Invalid API key - raises auth error

---

### Task 3.2: Define Agent System Prompt

**Description:** Create base system prompt for the Todo Assistant agent.

**Spec Reference:** `specs/agents/todo-agent.md` - System Prompt

**Dependencies:** None

**Acceptance Criteria:**
- [x] System prompt template created in `app/agents/prompts.py`
- [x] Includes role definition (helpful AI assistant)
- [x] Includes capabilities list
- [x] Includes guidelines (friendly, concise, confirm actions)
- [x] Includes important rules (user_id security, date calculations)
- [x] Template supports variable injection (current_date, user_timezone)
- [x] Prompt is clear and well-structured

**Test Cases:**
- TC-3.2.1: Load prompt template - succeeds
- TC-3.2.2: Inject current_date - formats correctly
- TC-3.2.3: Final prompt under token limit
- TC-3.2.4: Prompt reads naturally

---

### Task 3.3: Create Agent Context Builder

**Description:** Build function to construct agent context from chat history and user data.

**Spec Reference:** `specs/agents/todo-agent.md` - Context Management

**Dependencies:** Phase 1 (database), Task 3.2

**Acceptance Criteria:**
- [x] Function: `build_agent_context(user_id, session_id, user_email) -> str`
- [x] Loads last 20 messages from chat_history
- [x] Formats messages as OpenAI message format
- [x] Includes user stats (pending count, completed today)
- [x] Includes current date and timezone
- [x] Returns formatted context string

**Test Cases:**
- TC-3.3.1: Build context with history - includes messages
- TC-3.3.2: Build context with no history - includes system info only
- TC-3.3.3: Message format matches OpenAI spec
- TC-3.3.4: User stats calculated correctly
- TC-3.3.5: Context under token limit

---

### Task 3.4: Register MCP Tools with Agent

**Description:** Register all 5 MCP tools as available functions for the agent.

**Spec Reference:** `specs/agents/todo-agent.md` - Tool Registration

**Dependencies:** Phase 2 (MCP tools), Task 3.1

**Acceptance Criteria:**
- [x] All 5 tools registered with OpenAI function calling
- [x] Function schemas match MCP tool schemas
- [x] Tool descriptions are clear and helpful
- [x] Parameter descriptions guide the agent
- [x] Required parameters marked correctly
- [x] Agent can see all available tools

**Test Cases:**
- TC-3.4.1: List available tools - returns 5
- TC-3.4.2: Each tool has name, description, parameters
- TC-3.4.3: Schemas validate correctly
- TC-3.4.4: Agent can call each tool

---

### Task 3.5: Implement Intent Recognition Logic

**Description:** Create logic to recognize user intent from messages.

**Spec Reference:** `specs/agents/todo-agent.md` - Intent Recognition

**Dependencies:** Task 3.2

**Acceptance Criteria:**
- [x] Recognizes 9 intent types: CREATE_TODO, LIST_TODOS, UPDATE_TODO, COMPLETE_TODO, DELETE_TODO, SEARCH_TODOS, GET_DETAILS, HELP, GREETING
- [x] Pattern matching for each intent
- [x] Confidence scoring (0.0 to 1.0)
- [x] Returns intent + confidence + extracted parameters
- [x] Handles ambiguous input gracefully

**Test Cases:**
- TC-3.5.1: "Add buy milk" - recognizes CREATE_TODO
- TC-3.5.2: "Show my tasks" - recognizes LIST_TODOS
- TC-3.5.3: "I finished X" - recognizes COMPLETE_TODO
- TC-3.5.4: "Delete X" - recognizes DELETE_TODO
- TC-3.5.5: "Find X" - recognizes SEARCH_TODOS
- TC-3.5.6: Ambiguous input - low confidence score

---

### Task 3.6: Implement Parameter Extraction

**Description:** Extract parameters from user messages for tool calls.

**Spec Reference:** `specs/agents/todo-agent.md` - Intent Recognition Examples

**Dependencies:** Task 3.5

**Acceptance Criteria:**
- [x] Extracts title from create requests
- [x] Extracts due_date from natural language ("tomorrow", "next Friday")
- [x] Extracts priority from text ("high priority", "urgent")
- [x] Extracts filters from list requests
- [x] Extracts search query
- [x] Extracts todo identifiers (title match, number reference)

**Test Cases:**
- TC-3.6.1: "Add buy milk tomorrow" - extracts title and due_date
- TC-3.6.2: "Create high priority task" - extracts priority
- TC-3.6.3: "Show tasks due today" - extracts filter
- TC-3.6.4: "Find work tasks" - extracts query
- TC-3.6.5: "Complete task 1" - extracts number reference

---

### Task 3.7: Implement Tool Selection Logic

**Description:** Create decision tree to select appropriate MCP tool based on intent.

**Spec Reference:** `specs/agents/todo-agent.md` - Tool Selection Logic

**Dependencies:** Task 3.5, Task 3.6

**Acceptance Criteria:**
- [x] CREATE_TODO intent → create_todo tool
- [x] LIST_TODOS intent → list_todos tool
- [x] UPDATE_TODO intent → search first if needed, then update_todo
- [x] COMPLETE_TODO intent → update_todo with status="completed"
- [x] DELETE_TODO intent → search first if needed, then delete_todo (with confirmation)
- [x] SEARCH_TODOS intent → search_todos tool
- [x] HELP/GREETING → no tool, direct response
- [x] Handles multi-step flows (search then action)

**Test Cases:**
- TC-3.7.1: Clear intent - immediate tool call
- TC-3.7.2: Ambiguous todo reference - search first
- TC-3.7.3: Delete request - requires confirmation
- TC-3.7.4: Multi-step flow executes correctly
- TC-3.7.5: Help request - no tool called

---

### Task 3.8: Implement Reference Resolution

**Description:** Resolve user references to todos from conversation context.

**Spec Reference:** `specs/agents/todo-agent.md` - Context and Reference Resolution

**Dependencies:** Task 3.3

**Acceptance Criteria:**
- [x] Stores last list_todos result in context (expires after 5 messages)
- [x] Resolves numeric references ("task 1", "the second one")
- [x] Stores last created/updated task (expires after 3 messages)
- [x] Resolves pronoun references ("it", "that one")
- [x] Handles expired context gracefully (asks for clarification)
- [x] Reference storage persists within conversation turn

**Test Cases:**
- TC-3.8.1: "Show tasks" then "Complete 1" - resolves correctly
- TC-3.8.2: "Add task" then "Make it high priority" - resolves correctly
- TC-3.8.3: Reference after 6 messages - asks for clarification
- TC-3.8.4: No context available - asks which task
- TC-3.8.5: Multiple matches - asks for clarification

---

### Task 3.9: Create Response Generation Templates

**Description:** Define templates for generating natural language responses.

**Spec Reference:** `specs/agents/todo-agent.md` - Response Generation

**Dependencies:** Task 3.2

**Acceptance Criteria:**
- [x] Templates for all response types (create, list, update, complete, delete, search, error)
- [x] Multiple variations per type (avoid repetition)
- [x] Includes emojis appropriately
- [x] Formatting rules (bullets, numbers)
- [x] Personalization (encouragement, empathy)
- [x] Templates support variable substitution

**Test Cases:**
- TC-3.9.1: Create response - includes task details
- TC-3.9.2: List response - formatted with numbers
- TC-3.9.3: Complete response - includes encouragement
- TC-3.9.4: Error response - helpful and clear
- TC-3.9.5: Response variations used correctly

---

### Task 3.10: Implement Response Formatter

**Description:** Format tool results into conversational responses.

**Spec Reference:** `specs/agents/todo-agent.md` - Response Generation

**Dependencies:** Task 3.9

**Acceptance Criteria:**
- [x] Formats create_todo result: "I've created {title}..."
- [x] Formats list_todos result: numbered list with details
- [x] Formats update_todo result: "Updated! {title} is now {change}"
- [x] Formats delete_todo result: "Done! {title} has been removed"
- [x] Formats search_todos result: numbered list with highlights
- [x] Formats errors: clear message + suggestion
- [x] Keeps responses under 150 words

**Test Cases:**
- TC-3.10.1: Format create response - clear and concise
- TC-3.10.2: Format list response - readable structure
- TC-3.10.3: Format error response - helpful
- TC-3.10.4: Response includes emojis appropriately
- TC-3.10.5: Response length within limit

---

### Task 3.11: Implement Agent Main Processing Function

**Description:** Create main function that processes user messages through the agent.

**Spec Reference:** `specs/agents/todo-agent.md` - Agent Configuration

**Dependencies:** Tasks 3.1-3.10

**Acceptance Criteria:**
- [x] Function: `async def process_chat_message(user_id, session_id, message, history) -> dict`
- [x] Builds context from history
- [x] Calls OpenAI Agent with context + message
- [x] Agent recognizes intent and selects tool
- [x] Agent calls appropriate MCP tool
- [x] Agent generates response from tool result
- [x] Returns {content: str, metadata: dict}
- [x] Handles all error cases

**Test Cases:**
- TC-3.11.1: Process "Add task" - creates todo and responds
- TC-3.11.2: Process "Show tasks" - lists todos and responds
- TC-3.11.3: Process with context - uses reference resolution
- TC-3.11.4: Process ambiguous input - asks for clarification
- TC-3.11.5: Process with tool error - generates error response

---

### Task 3.12: Implement Clarification Question Logic

**Description:** Add logic for agent to ask clarifying questions when needed.

**Spec Reference:** `specs/agents/todo-agent.md` - Ambiguity Resolution

**Dependencies:** Task 3.5, Task 3.11

**Acceptance Criteria:**
- [x] Detects ambiguous input (low confidence, missing params)
- [x] Asks specific clarifying questions
- [x] Multiple matches - lists options with numbers
- [x] Missing required info - asks for it
- [x] Unclear date - asks for specific date
- [x] Provides examples in questions

**Test Cases:**
- TC-3.12.1: Missing title - asks "What should the task be?"
- TC-3.12.2: Multiple matches - lists and asks "Which one?"
- TC-3.12.3: Ambiguous date - asks for specific day
- TC-3.12.4: Empty input - prompts for action
- TC-3.12.5: Clarification questions are clear

---

### Task 3.13: Implement Agent Error Handling

**Description:** Add comprehensive error handling for all agent operations.

**Spec Reference:** `specs/agents/todo-agent.md` - Error Handling

**Dependencies:** Task 3.11

**Acceptance Criteria:**
- [x] Handles OpenAI API errors (rate limit, timeout)
- [x] Handles MCP tool errors (propagates error codes)
- [x] Handles invalid context errors
- [x] Never exposes technical details to user
- [x] Always provides recovery suggestions
- [x] Logs errors for debugging

**Test Cases:**
- TC-3.13.1: OpenAI API error - user sees friendly message
- TC-3.13.2: Tool returns error - agent explains and suggests action
- TC-3.13.3: Context loading fails - recovers gracefully
- TC-3.13.4: All errors logged properly
- TC-3.13.5: User never sees stack traces

---

### Task 3.14: Add Agent Response Logging

**Description:** Implement logging for all agent interactions and tool calls.

**Spec Reference:** `specs/agents/todo-agent.md` - Testing Strategy

**Dependencies:** Task 3.11

**Acceptance Criteria:**
- [x] Log every user message processed
- [x] Log recognized intent and confidence
- [x] Log tool calls with parameters
- [x] Log tool responses
- [x] Log generated responses
- [x] Log errors with full context
- [x] Structured logging (JSON format)

**Test Cases:**
- TC-3.14.1: Process message - all steps logged
- TC-3.14.2: Logs include timestamps
- TC-3.14.3: Logs include user_id (for debugging)
- TC-3.14.4: Logs are structured and searchable
- TC-3.14.5: Sensitive data not logged

---

### Task 3.15: Write Unit Tests for Agent

**Description:** Create comprehensive unit tests for agent logic.

**Spec Reference:** `specs/agents/todo-agent.md` - Testing Strategy

**Dependencies:** Tasks 3.1-3.14

**Acceptance Criteria:**
- [x] Test file: `tests/test_agent.py`
- [x] Mock OpenAI API calls
- [x] Mock MCP tool calls
- [x] Test all intent recognition
- [x] Test tool selection logic
- [x] Test reference resolution
- [x] Test response generation
- [x] >85% code coverage

**Test Cases:**
- TC-3.15.1: Test each intent type recognized correctly
- TC-3.15.2: Test parameter extraction
- TC-3.15.3: Test tool selection
- TC-3.15.4: Test reference resolution
- TC-3.15.5: Test error handling
- TC-3.15.6: Tests pass successfully

---

## Phase 4: Backend API Implementation (10 tasks)

### Task 4.1: Create FastAPI Chat Endpoint

**Description:** Implement POST /chat endpoint in FastAPI backend.

**Spec Reference:** `specs/PLAN.md` - Frontend ↔ Backend Integration

**Dependencies:** Phase 1 (database), Phase 3 (agent)

**Acceptance Criteria:**
- [x] Endpoint: POST /chat
- [x] Request schema: {message: str, session_id: str}
- [x] Response schema: {response: str, session_id: str, timestamp: str}
- [x] Validates JWT token (extracts user_id)
- [x] Returns 401 if unauthorized
- [x] Returns 400 if invalid input
- [x] Returns 200 with response on success

**Test Cases:**
- TC-4.1.1: Valid request with auth - returns 200
- TC-4.1.2: Missing JWT token - returns 401
- TC-4.1.3: Invalid session_id - returns 400
- TC-4.1.4: Empty message - returns 400
- TC-4.1.5: Response has correct schema

---

### Task 4.2: Implement JWT Validation Middleware

**Description:** Create middleware to validate JWT tokens and extract user_id.

**Spec Reference:** `specs/overview.md` - Authentication Flow

**Dependencies:** None (Phase 2 Better Auth already exists)

**Acceptance Criteria:**
- [x] Middleware validates JWT using BETTER_AUTH_SECRET
- [x] Extracts user_id from validated token
- [x] Injects user_id into request context
- [x] Returns 401 for invalid/expired tokens
- [x] Works with Better Auth JWT format

**Test Cases:**
- TC-4.2.1: Valid token - user_id extracted
- TC-4.2.2: Invalid token - returns 401
- TC-4.2.3: Expired token - returns 401
- TC-4.2.4: Missing token - returns 401
- TC-4.2.5: User_id available in endpoint

---

### Task 4.3: Implement Chat History Loading in Endpoint

**Description:** Load chat history for agent context in /chat endpoint.

**Spec Reference:** `specs/PLAN.md` - Backend ↔ Database

**Dependencies:** Phase 1 (database), Task 4.1

**Acceptance Criteria:**
- [x] Loads last 20 messages using load_chat_history()
- [x] Filters by user_id and session_id
- [x] Formats for agent consumption
- [x] Handles empty history gracefully
- [x] Query optimized (uses indexes)

**Test Cases:**
- TC-4.3.1: Load existing history - succeeds
- TC-4.3.2: New session (no history) - returns empty
- TC-4.3.3: History formatted correctly for agent
- TC-4.3.4: Only user's history loaded (isolation)
- TC-4.3.5: Query performance <100ms

---

### Task 4.4: Implement User Message Saving

**Description:** Save user message to database before processing.

**Spec Reference:** `specs/PLAN.md` - Backend ↔ Database

**Dependencies:** Phase 1 (database), Task 4.1

**Acceptance Criteria:**
- [x] Saves user message using save_message()
- [x] Sets role="user"
- [x] Includes metadata (client_ip, user_agent)
- [x] Committed to database before agent call
- [x] Returns message ID

**Test Cases:**
- TC-4.4.1: Save user message - succeeds
- TC-4.4.2: Message has correct user_id and session_id
- TC-4.4.3: Metadata populated
- TC-4.4.4: Timestamp auto-generated
- TC-4.4.5: Can be retrieved immediately

---

### Task 4.5: Integrate Agent Processing in Endpoint

**Description:** Call agent to process user message and generate response.

**Spec Reference:** `specs/PLAN.md` - Backend ↔ Agent

**Dependencies:** Phase 3 (agent), Task 4.1, Task 4.3

**Acceptance Criteria:**
- [x] Calls process_chat_message() with user_id, session_id, message, history
- [x] Passes loaded history to agent
- [x] Receives agent response with content and metadata
- [x] Handles agent errors gracefully
- [x] Timeout protection (30 seconds)

**Test Cases:**
- TC-4.5.1: Agent processes successfully - returns response
- TC-4.5.2: Agent returns tool call results - formatted correctly
- TC-4.5.3: Agent error - returns friendly error message
- TC-4.5.4: Agent timeout - returns timeout error
- TC-4.5.5: Response includes metadata

---

### Task 4.6: Implement Assistant Message Saving

**Description:** Save agent response to database after processing.

**Spec Reference:** `specs/PLAN.md` - Backend ↔ Database

**Dependencies:** Phase 1 (database), Task 4.5

**Acceptance Criteria:**
- [x] Saves assistant message using save_message()
- [x] Sets role="assistant"
- [x] Includes metadata (tool_calls, tokens_used)
- [x] Committed to database before returning response
- [x] Returns message ID

**Test Cases:**
- TC-4.6.1: Save assistant message - succeeds
- TC-4.6.2: Metadata includes tool calls
- TC-4.6.3: Both user and assistant messages saved
- TC-4.6.4: Chat history can be retrieved
- TC-4.6.5: Conversation flow preserved

---

### Task 4.7: Add Error Handling to Chat Endpoint

**Description:** Implement comprehensive error handling for all failure scenarios.

**Spec Reference:** `specs/PLAN.md` - Backend API

**Dependencies:** Task 4.1

**Acceptance Criteria:**
- [x] Database errors caught and logged
- [x] Agent errors caught and returned gracefully
- [x] Validation errors return 400 with clear message
- [x] Internal errors return 500 (but user sees friendly message)
- [x] All errors logged with full context
- [x] Error response format consistent

**Test Cases:**
- TC-4.7.1: Database down - returns 500 with message
- TC-4.7.2: Agent error - returns agent error message
- TC-4.7.3: Validation error - returns 400
- TC-4.7.4: All errors logged
- TC-4.7.5: User never sees technical details

---

### Task 4.8: Add Request/Response Logging

**Description:** Log all requests and responses for monitoring and debugging.

**Spec Reference:** `specs/PLAN.md` - Monitoring

**Dependencies:** Task 4.1

**Acceptance Criteria:**
- [x] Log incoming requests (method, path, user_id, session_id)
- [x] Log response status and timing
- [x] Log message length (for monitoring)
- [x] Structured logging (JSON format)
- [x] Don't log sensitive data (message content optional)
- [x] Performance metrics tracked

**Test Cases:**
- TC-4.8.1: Request logged with all fields
- TC-4.8.2: Response time logged
- TC-4.8.3: Logs are structured
- TC-4.8.4: Sensitive data not logged
- TC-4.8.5: Logs searchable in production

---

### Task 4.9: Implement Rate Limiting

**Description:** Add rate limiting to prevent abuse of chat endpoint.

**Spec Reference:** `specs/PLAN.md` - Deployment

**Dependencies:** Task 4.1

**Acceptance Criteria:**
- [x] Rate limit: 30 requests per minute per user
- [x] Returns 429 when limit exceeded
- [x] Rate limit headers in response
- [x] Redis or in-memory store for counters
- [x] Configurable limits

**Test Cases:**
- TC-4.9.1: Within limit - requests succeed
- TC-4.9.2: Exceed limit - returns 429
- TC-4.9.3: Different users have separate limits
- TC-4.9.4: Limit resets after time window
- TC-4.9.5: Headers show remaining requests

---

### Task 4.10: Write Integration Tests for Chat Endpoint

**Description:** Create end-to-end integration tests for chat flow.

**Spec Reference:** `specs/PLAN.md` - Testing Strategy

**Dependencies:** Tasks 4.1-4.9

**Acceptance Criteria:**
- [x] Test file: `tests/test_chat_endpoint.py`
- [x] Test complete flow: request → agent → tools → database → response
- [x] Test authentication flow
- [x] Test error scenarios
- [x] Test conversation continuity
- [x] Tests use test database

**Test Cases:**
- TC-4.10.1: Complete create todo flow - works end-to-end
- TC-4.10.2: Complete list todos flow - works end-to-end
- TC-4.10.3: Multi-turn conversation - context preserved
- TC-4.10.4: Unauthorized request - rejected
- TC-4.10.5: All tests pass successfully

---

## Phase 5: Frontend Implementation (20 tasks)

### Task 5.1: Create React Project with Vite

**Description:** Initialize React project using Vite and TypeScript.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Frontend Setup

**Dependencies:** None

**Acceptance Criteria:**
- [x] Project created with `npm create vite@latest`
- [x] TypeScript template selected
- [x] Project structure created
- [x] Dev server runs successfully
- [x] Build succeeds

**Test Cases:**
- TC-5.1.1: npm run dev - starts dev server
- TC-5.1.2: npm run build - builds successfully
- TC-5.1.3: TypeScript compilation works
- TC-5.1.4: Hot reload works

---

### Task 5.2: Install Frontend Dependencies

**Description:** Install all required npm packages for the frontend.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Dependencies

**Dependencies:** Task 5.1

**Acceptance Criteria:**
- [x] Install @openai/chatkit
- [x] Install axios
- [x] Install zustand
- [x] Install react-router-dom
- [x] All dependencies in package.json
- [x] node_modules populated

**Test Cases:**
- TC-5.2.1: All packages installed without errors
- TC-5.2.2: Can import all packages
- TC-5.2.3: No conflicting versions
- TC-5.2.4: Lock file generated

---

### Task 5.3: Set Up Project Directory Structure

**Description:** Create organized directory structure for frontend code.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Project Structure

**Dependencies:** Task 5.1

**Acceptance Criteria:**
- [x] src/components/ created
- [x] src/pages/ created
- [x] src/stores/ created
- [x] src/api/ created
- [x] src/utils/ created
- [x] src/styles/ created
- [x] Index files in each directory

**Test Cases:**
- TC-5.3.1: All directories exist
- TC-5.3.2: Directory structure matches spec
- TC-5.3.3: Can import from directories

---

### Task 5.4: Create Authentication Store with Zustand

**Description:** Implement Zustand store for authentication state management.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Authentication Store

**Dependencies:** Task 5.2

**Acceptance Criteria:**
- [x] File: src/stores/authStore.ts
- [x] State: token, user, isAuthenticated
- [x] Actions: login(), logout()
- [x] Persists to localStorage
- [x] TypeScript interfaces defined
- [x] Store can be imported and used

**Test Cases:**
- TC-5.4.1: Initial state is unauthenticated
- TC-5.4.2: login() sets token and user
- TC-5.4.3: logout() clears state
- TC-5.4.4: State persists across page reload
- TC-5.4.5: TypeScript types correct

---

### Task 5.5: Implement Session Management Utilities

**Description:** Create utilities for generating and managing session IDs.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Session Management

**Dependencies:** None

**Acceptance Criteria:**
- [x] File: src/utils/sessionManager.ts
- [x] Function: generateSessionId() -> string (format: sess_{timestamp}_{random})
- [x] Function: getSessionId() -> string (get or create)
- [x] Function: startNewSession() -> string
- [x] Function: clearSession() -> void
- [x] Uses localStorage for persistence

**Test Cases:**
- TC-5.5.1: generateSessionId() creates unique IDs
- TC-5.5.2: Session ID format correct (sess_...)
- TC-5.5.3: getSessionId() persists across calls
- TC-5.5.4: startNewSession() creates new ID
- TC-5.5.5: clearSession() removes from localStorage

---

### Task 5.6: Create API Client with Axios

**Description:** Set up axios instance for backend communication.

**Spec Reference:** `specs/ui/chatkit-integration.md` - API Client

**Dependencies:** Task 5.2, Task 5.4

**Acceptance Criteria:**
- [x] File: src/api/chatApi.ts
- [x] Axios instance with base URL from env
- [x] Request interceptor adds JWT token
- [x] Response interceptor handles 401 (logout)
- [x] Timeout set to 30 seconds
- [x] TypeScript types for all API calls

**Test Cases:**
- TC-5.6.1: Client created with correct base URL
- TC-5.6.2: Token added to requests automatically
- TC-5.6.3: 401 response triggers logout
- TC-5.6.4: Timeout works correctly
- TC-5.6.5: TypeScript types enforce schema

---

### Task 5.7: Implement sendChatMessage API Function

**Description:** Create function to send chat messages to backend.

**Spec Reference:** `specs/ui/chatkit-integration.md` - API Client

**Dependencies:** Task 5.6

**Acceptance Criteria:**
- [x] Function: sendChatMessage(message, sessionId) -> Promise<ChatResponse>
- [x] POST to /chat endpoint
- [x] Sends {message, session_id} in body
- [x] Returns {response, session_id, timestamp}
- [x] Handles errors and throws
- [x] TypeScript types for request/response

**Test Cases:**
- TC-5.7.1: Send message - returns response
- TC-5.7.2: Request format correct
- TC-5.7.3: Response parsed correctly
- TC-5.7.4: Network error - throws
- TC-5.7.5: TypeScript types enforced

---

### Task 5.8: Implement loadChatHistory API Function

**Description:** Create function to load chat history from backend (optional endpoint).

**Spec Reference:** `specs/ui/chatkit-integration.md` - API Client

**Dependencies:** Task 5.6

**Acceptance Criteria:**
- [x] Function: loadChatHistory(sessionId) -> Promise<ChatMessage[]>
- [x] GET to /chat/history/{sessionId}
- [x] Returns array of messages
- [x] Handles empty history
- [x] TypeScript types defined

**Test Cases:**
- TC-5.8.1: Load history - returns messages
- TC-5.8.2: Empty history - returns empty array
- TC-5.8.3: Response parsed correctly
- TC-5.8.4: Error handling works

---

### Task 5.9: Create Login Page Component

**Description:** Build login page with form for Better Auth authentication.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Login Page

**Dependencies:** Task 5.4, Task 5.6

**Acceptance Criteria:**
- [x] File: src/pages/LoginPage.tsx
- [x] Form with email and password fields
- [x] Submit calls /auth/login endpoint
- [x] On success: stores token and redirects to /chat
- [x] On error: displays error message
- [x] Loading state during submission
- [x] Responsive design

**Test Cases:**
- TC-5.9.1: Render login form - displays
- TC-5.9.2: Submit valid credentials - redirects
- TC-5.9.3: Submit invalid credentials - shows error
- TC-5.9.4: Loading state shows during submit
- TC-5.9.5: Already authenticated - redirects to chat

---

### Task 5.10: Create Main App Component with Routing

**Description:** Set up main App component with React Router.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Main App Component

**Dependencies:** Task 5.4, Task 5.9

**Acceptance Criteria:**
- [x] File: src/App.tsx
- [x] React Router setup (BrowserRouter)
- [x] Routes: /login, /chat, / (redirect)
- [x] Protected routes (require authentication)
- [x] Public routes (redirect if authenticated)
- [x] Layout wrapper if needed

**Test Cases:**
- TC-5.10.1: Navigate to / - redirects appropriately
- TC-5.10.2: Unauthenticated user to /chat - redirects to /login
- TC-5.10.3: Authenticated user to /login - redirects to /chat
- TC-5.10.4: Routes render correct components
- TC-5.10.5: Navigation works

---

### Task 5.11: Create TodoChatInterface Component

**Description:** Build main chat interface component.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Main Chat Interface Component

**Dependencies:** Task 5.4, Task 5.5, Task 5.7

**Acceptance Criteria:**
- [x] File: src/components/TodoChatInterface.tsx
- [x] State: messages, isLoading, sessionId
- [x] Loads session ID on mount
- [x] Loads chat history on mount (optional)
- [x] Handler: handleSendMessage()
- [x] Handler: handleNewConversation()
- [x] Handler: handleLogout()
- [x] Renders ChatKit component

**Test Cases:**
- TC-5.11.1: Component renders
- TC-5.11.2: Session ID loaded on mount
- TC-5.11.3: History loaded on mount
- TC-5.11.4: Send message updates UI
- TC-5.11.5: New conversation resets state

---

### Task 5.12: Implement handleSendMessage Function

**Description:** Create message sending handler with optimistic UI updates.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Main Chat Interface Component

**Dependencies:** Task 5.11, Task 5.7

**Acceptance Criteria:**
- [x] Validates non-empty message
- [x] Adds user message to UI immediately
- [x] Sets loading state
- [x] Calls sendChatMessage()
- [x] Adds assistant response to UI
- [x] Handles errors (shows error message in UI)
- [x] Clears loading state

**Test Cases:**
- TC-5.12.1: Send message - user message appears immediately
- TC-5.12.2: Response received - assistant message appears
- TC-5.12.3: Error occurs - error message shown
- TC-5.12.4: Loading state managed correctly
- TC-5.12.5: Empty message - ignored

---

### Task 5.13: Integrate OpenAI ChatKit Component

**Description:** Integrate and configure OpenAI ChatKit for message display.

**Spec Reference:** `specs/ui/chatkit-integration.md` - ChatKit Integration

**Dependencies:** Task 5.11

**Acceptance Criteria:**
- [x] ChatKit component imported and rendered
- [x] Props: messages, onSendMessage, isLoading
- [x] Props: placeholder, welcomeMessage, theme
- [x] Props: showTimestamps, enableMarkdown
- [x] ChatKit displays messages correctly
- [x] Input field functional

**Test Cases:**
- TC-5.13.1: ChatKit renders
- TC-5.13.2: Messages display in chat
- TC-5.13.3: User can type and send
- TC-5.13.4: Loading indicator shows
- TC-5.13.5: Timestamps displayed

---

### Task 5.14: Create Custom Message Formatting

**Description:** Implement custom message rendering with markdown and emojis.

**Spec Reference:** `specs/ui/chatkit-integration.md` - ChatKit Configuration

**Dependencies:** Task 5.13

**Acceptance Criteria:**
- [x] Custom renderMessage function
- [x] Formats **bold** and *italic*
- [x] Formats `code` snippets
- [x] Renders line breaks
- [x] Displays emojis correctly
- [x] Formats timestamps

**Test Cases:**
- TC-5.14.1: Bold text renders correctly
- TC-5.14.2: Italic text renders correctly
- TC-5.14.3: Code snippets styled
- TC-5.14.4: Line breaks preserved
- TC-5.14.5: Emojis display

---

### Task 5.15: Create Chat Header Component

**Description:** Build header with user info and action buttons.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Main Chat Interface Component

**Dependencies:** Task 5.4

**Acceptance Criteria:**
- [x] Shows app title "Todo Assistant"
- [x] Displays user email
- [x] Button: "New Chat"
- [x] Button: "Logout"
- [x] Responsive design
- [x] Styling matches design

**Test Cases:**
- TC-5.15.1: Header renders with title
- TC-5.15.2: User email displayed
- TC-5.15.3: Buttons clickable
- TC-5.15.4: Responsive on mobile
- TC-5.15.5: Styling correct

---

### Task 5.16: Implement New Conversation Feature

**Description:** Allow users to start a new chat session.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Main Chat Interface Component

**Dependencies:** Task 5.5, Task 5.11

**Acceptance Criteria:**
- [x] Click "New Chat" button
- [x] Generates new session ID
- [x] Clears messages array
- [x] Updates localStorage
- [x] Shows confirmation toast (optional)

**Test Cases:**
- TC-5.16.1: Click button - session ID changes
- TC-5.16.2: Messages cleared
- TC-5.16.3: localStorage updated
- TC-5.16.4: Can send message in new session
- TC-5.16.5: New session isolated from old

---

### Task 5.17: Style Chat Interface

**Description:** Create CSS styles for chat interface following design spec.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Styling

**Dependencies:** Task 5.11

**Acceptance Criteria:**
- [x] File: src/styles/TodoChatInterface.css
- [x] Container layout (header + chat area)
- [x] Header styling
- [x] Message styling (user vs assistant)
- [x] Loading indicator styling
- [x] Responsive design (mobile-first)
- [x] Emoji support

**Test Cases:**
- TC-5.17.1: Layout renders correctly
- TC-5.17.2: User/assistant messages distinct
- TC-5.17.3: Responsive on mobile
- TC-5.17.4: Colors and spacing match design
- TC-5.17.5: Animations smooth

---

### Task 5.18: Add Toast Notifications

**Description:** Implement toast notifications for user feedback.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Main Chat Interface Component

**Dependencies:** Task 5.2

**Acceptance Criteria:**
- [x] Toast component or library integrated
- [x] Success toasts (green)
- [x] Error toasts (red)
- [x] Info toasts (blue)
- [x] Auto-dismiss after 3 seconds
- [x] Positioned correctly (top-right)

**Test Cases:**
- TC-5.18.1: Show success toast - displays and dismisses
- TC-5.18.2: Show error toast - displays and dismisses
- TC-5.18.3: Multiple toasts stack correctly
- TC-5.18.4: Manual dismiss works
- TC-5.18.5: Styling correct

---

### Task 5.19: Configure Environment Variables

**Description:** Set up environment configuration for frontend.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Deployment

**Dependencies:** Task 5.1

**Acceptance Criteria:**
- [x] File: .env.development
- [x] File: .env.production
- [x] Variable: VITE_API_URL
- [x] Variable: VITE_APP_NAME (optional)
- [x] Variables loaded correctly in code
- [x] .env files in .gitignore

**Test Cases:**
- TC-5.19.1: Development env loads
- TC-5.19.2: Production env loads
- TC-5.19.3: API URL accessible in code
- TC-5.19.4: Build uses correct env
- TC-5.19.5: Env files not committed

---

### Task 5.20: Write Frontend Component Tests

**Description:** Create unit tests for React components.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Testing

**Dependencies:** Tasks 5.9-5.18

**Acceptance Criteria:**
- [x] Test files for each component
- [x] Test library: @testing-library/react
- [x] Test rendering
- [x] Test user interactions
- [x] Test API calls (mocked)
- [x] >80% component coverage

**Test Cases:**
- TC-5.20.1: Login form tests pass
- TC-5.20.2: Chat interface tests pass
- TC-5.20.3: Message sending tests pass
- TC-5.20.4: New session tests pass
- TC-5.20.5: All tests pass successfully

---

## Phase 6: Integration & Testing (10 tasks)

### Task 6.1: Set Up Test Database

**Description:** Configure separate test database for integration tests.

**Spec Reference:** `specs/PLAN.md` - Testing Strategy

**Dependencies:** Phase 1 (database)

**Acceptance Criteria:**
- [x] Test database configured
- [x] Migrations run on test DB
- [x] Test DB isolated from development DB
- [x] Can be reset between tests
- [x] Environment variable for test DB URL

**Test Cases:**
- TC-6.1.1: Test DB created successfully
- TC-6.1.2: Migrations applied
- TC-6.1.3: Can connect to test DB
- TC-6.1.4: Reset works correctly
- TC-6.1.5: Isolated from dev DB

---

### Task 6.2: Write Database Integration Tests

**Description:** Test all database queries with real database.

**Spec Reference:** `specs/database/chat-history.md` - Testing Strategy

**Dependencies:** Task 6.1, Phase 1

**Acceptance Criteria:**
- [x] Test file: tests/integration/test_database.py
- [x] Test all query functions
- [x] Test user isolation
- [x] Test soft delete
- [x] Test cleanup
- [x] Uses test database

**Test Cases:**
- TC-6.2.1: Save and load messages - works correctly
- TC-6.2.2: User isolation enforced
- TC-6.2.3: Soft delete works
- TC-6.2.4: Cleanup deletes old messages
- TC-6.2.5: All tests pass

---

### Task 6.3: Write MCP Tools Integration Tests

**Description:** Test MCP tools with mock Phase 2 backend.

**Spec Reference:** `specs/api/mcp-tools.md` - Testing Strategy

**Dependencies:** Phase 2 (MCP tools)

**Acceptance Criteria:**
- [x] Test file: tests/integration/test_mcp_tools.py
- [x] Mock Phase 2 HTTP responses
- [x] Test all tools end-to-end
- [x] Test error scenarios
- [x] Test with real MCP server

**Test Cases:**
- TC-6.3.1: Create todo through tool - succeeds
- TC-6.3.2: List todos through tool - succeeds
- TC-6.3.3: Update todo through tool - succeeds
- TC-6.3.4: Delete todo through tool - succeeds
- TC-6.3.5: Search todos through tool - succeeds
- TC-6.3.6: All error paths tested

---

### Task 6.4: Write Agent Integration Tests

**Description:** Test agent with mock OpenAI API and real MCP tools.

**Spec Reference:** `specs/agents/todo-agent.md` - Testing Strategy

**Dependencies:** Phase 3 (agent), Phase 2 (MCP tools)

**Acceptance Criteria:**
- [x] Test file: tests/integration/test_agent.py
- [x] Mock OpenAI API responses
- [x] Use real MCP tools (with mocked backend)
- [x] Test complete conversation flows
- [x] Test all intents

**Test Cases:**
- TC-6.4.1: "Add task" conversation - works end-to-end
- TC-6.4.2: "Show tasks" conversation - works end-to-end
- TC-6.4.3: Multi-turn conversation - context preserved
- TC-6.4.4: Ambiguous input - clarification asked
- TC-6.4.5: All tests pass

---

### Task 6.5: Write Backend API Integration Tests

**Description:** Test FastAPI chat endpoint end-to-end.

**Spec Reference:** `specs/PLAN.md` - Testing Strategy

**Dependencies:** Phase 4 (backend), Task 6.1

**Acceptance Criteria:**
- [x] Test file: tests/integration/test_api.py
- [x] Uses TestClient from FastAPI
- [x] Tests with real database (test DB)
- [x] Tests authentication flow
- [x] Tests complete message flow
- [x] Tests error scenarios

**Test Cases:**
- TC-6.5.1: POST /chat with auth - creates and lists todo
- TC-6.5.2: POST /chat unauthorized - returns 401
- TC-6.5.3: Complete conversation flow - works
- TC-6.5.4: Chat history persisted correctly
- TC-6.5.5: All tests pass

---

### Task 6.6: Write End-to-End Conversation Tests

**Description:** Test complete user journeys from frontend to database.

**Spec Reference:** `specs/PLAN.md` - Testing Strategy

**Dependencies:** All previous phases

**Acceptance Criteria:**
- [x] Test file: tests/e2e/test_conversations.py
- [x] Tests complete user flows
- [x] Tests: create, list, update, complete, delete todos
- [x] Tests multi-turn conversations
- [x] Tests context and reference resolution
- [x] Uses all layers (frontend API, backend, agent, MCP, database)

**Test Cases:**
- TC-6.6.1: User creates todo via chat - persisted to database
- TC-6.6.2: User lists todos - correct data displayed
- TC-6.6.3: User updates todo - change reflected
- TC-6.6.4: User completes todo - status changed
- TC-6.6.5: User deletes todo - removed from database
- TC-6.6.6: Multi-turn: list then complete first - works with context

---

### Task 6.7: Performance Testing

**Description:** Test response times and concurrent load.

**Spec Reference:** `specs/PLAN.md` - Performance Tests

**Dependencies:** All previous phases

**Acceptance Criteria:**
- [x] Test chat endpoint response time <2s
- [x] Test database queries <100ms
- [x] Test concurrent users (10 simultaneous)
- [x] Test message throughput
- [x] Identify bottlenecks

**Test Cases:**
- TC-6.7.1: Average response time <2s
- TC-6.7.2: P95 response time <3s
- TC-6.7.3: P99 response time <5s
- TC-6.7.4: 10 concurrent users - all succeed
- TC-6.7.5: Database queries optimized

---

### Task 6.8: Security Testing

**Description:** Test authentication, authorization, and data isolation.

**Spec Reference:** `specs/PLAN.md` - Testing Strategy

**Dependencies:** All previous phases

**Acceptance Criteria:**
- [x] Test JWT validation
- [x] Test user isolation (User A cannot access User B's data)
- [x] Test SQL injection prevention
- [x] Test XSS prevention in messages
- [x] Test rate limiting
- [x] Test service token validation (MCP to Phase 2)

**Test Cases:**
- TC-6.8.1: Invalid JWT - rejected
- TC-6.8.2: User A cannot see User B's todos - enforced
- TC-6.8.3: SQL injection attempts - blocked
- TC-6.8.4: XSS in messages - escaped
- TC-6.8.5: Rate limit - enforced

---

### Task 6.9: Error Recovery Testing

**Description:** Test system behavior under failure conditions.

**Spec Reference:** `specs/PLAN.md` - Testing Strategy

**Dependencies:** All previous phases

**Acceptance Criteria:**
- [x] Test OpenAI API failure
- [x] Test Phase 2 backend unavailable
- [x] Test database connection failure
- [x] Test network timeouts
- [x] Test partial failures
- [x] Verify graceful degradation

**Test Cases:**
- TC-6.9.1: OpenAI API down - user sees friendly error
- TC-6.9.2: Phase 2 backend down - error handled
- TC-6.9.3: Database down - error handled
- TC-6.9.4: Timeout - user notified
- TC-6.9.5: System recovers after failures

---

### Task 6.10: Create Test Coverage Report

**Description:** Generate and review test coverage metrics.

**Spec Reference:** `specs/PLAN.md` - Testing Strategy

**Dependencies:** All test tasks

**Acceptance Criteria:**
- [x] Coverage tool configured (pytest-cov)
- [x] Generate coverage report
- [x] Backend coverage >90%
- [x] MCP tools coverage >95%
- [x] Agent coverage >85%
- [x] Frontend coverage >80%
- [x] Identify gaps

**Test Cases:**
- TC-6.10.1: Coverage report generated
- TC-6.10.2: All targets met
- TC-6.10.3: Gaps identified and documented
- TC-6.10.4: Critical paths fully covered
- TC-6.10.5: Report readable and actionable

---

## Phase 7: Deployment & Documentation (10 tasks)

### Task 7.1: Create Production Environment Configuration

**Description:** Set up configuration for production deployment.

**Spec Reference:** `specs/PLAN.md` - Deployment Plan

**Dependencies:** None

**Acceptance Criteria:**
- [x] Production .env template created
- [x] All required environment variables documented
- [x] Secrets management strategy defined
- [x] Database connection string for Neon
- [x] CORS settings configured
- [x] Production vs development differences documented

**Test Cases:**
- TC-7.1.1: Load production config - succeeds
- TC-7.1.2: All required vars present
- TC-7.1.3: Secrets not hardcoded
- TC-7.1.4: Config validated

---

### Task 7.2: Run Database Migrations in Production

**Description:** Apply all database migrations to production database.

**Spec Reference:** `specs/database/chat-history.md` - Migration Scripts

**Dependencies:** Task 7.1, Phase 1

**Acceptance Criteria:**
- [x] Backup existing database
- [x] Run alembic upgrade head
- [x] Verify all tables created
- [x] Verify all indexes created
- [x] Test queries work
- [x] Document rollback procedure

**Test Cases:**
- TC-7.2.1: Migration runs without errors
- TC-7.2.2: Tables exist with correct schema
- TC-7.2.3: Indexes created
- TC-7.2.4: Foreign keys enforced
- TC-7.2.5: Can insert test data

---

### Task 7.3: Deploy MCP Server

**Description:** Deploy MCP server to production environment.

**Spec Reference:** `specs/PLAN.md` - Backend Deployment

**Dependencies:** Phase 2, Task 7.1

**Acceptance Criteria:**
- [x] Install dependencies on server
- [x] Set environment variables
- [x] Start MCP server process
- [x] Configure process manager (systemd/supervisor)
- [x] Test server responds
- [x] Set up logging

**Test Cases:**
- TC-7.3.1: Server starts successfully
- TC-7.3.2: Can connect to server
- TC-7.3.3: Tools respond correctly
- TC-7.3.4: Logs written correctly
- TC-7.3.5: Auto-restart on failure works

---

### Task 7.4: Deploy FastAPI Backend

**Description:** Deploy FastAPI application to production.

**Spec Reference:** `specs/PLAN.md` - Backend Deployment

**Dependencies:** Phase 4, Task 7.1, Task 7.3

**Acceptance Criteria:**
- [x] Install dependencies
- [x] Set environment variables
- [x] Start with uvicorn (multiple workers)
- [x] Configure reverse proxy (nginx)
- [x] Enable HTTPS
- [x] Health check endpoint works

**Test Cases:**
- TC-7.4.1: Server starts with multiple workers
- TC-7.4.2: HTTPS enabled
- TC-7.4.3: /health endpoint returns 200
- TC-7.4.4: Can handle concurrent requests
- TC-7.4.5: Logs configured

---

### Task 7.5: Build and Deploy Frontend

**Description:** Build production frontend and deploy to hosting service.

**Spec Reference:** `specs/ui/chatkit-integration.md` - Deployment

**Dependencies:** Phase 5, Task 7.1

**Acceptance Criteria:**
- [x] Run npm run build
- [x] Set production environment variables
- [x] Deploy to Vercel/Netlify/similar
- [x] Configure custom domain (optional)
- [x] HTTPS enabled
- [x] Test production build locally first

**Test Cases:**
- TC-7.5.1: Build succeeds without errors
- TC-7.5.2: Production site accessible
- TC-7.5.3: API calls reach backend
- TC-7.5.4: Authentication works
- TC-7.5.5: All features functional

---

### Task 7.6: Configure Monitoring and Logging

**Description:** Set up monitoring for production system.

**Spec Reference:** `specs/PLAN.md` - Monitoring

**Dependencies:** Tasks 7.3, 7.4

**Acceptance Criteria:**
- [x] Logging aggregation (e.g., CloudWatch, Papertrail)
- [x] Error tracking (e.g., Sentry)
- [x] Performance monitoring (response times)
- [x] Uptime monitoring (e.g., UptimeRobot)
- [x] Alerts configured for critical issues
- [x] Dashboard accessible

**Test Cases:**
- TC-7.6.1: Logs aggregated from all services
- TC-7.6.2: Errors tracked and alerted
- TC-7.6.3: Performance metrics visible
- TC-7.6.4: Uptime monitors active
- TC-7.6.5: Test alert triggers correctly

---

### Task 7.7: Set Up Continuous Integration/Deployment

**Description:** Configure CI/CD pipeline for automated testing and deployment.

**Spec Reference:** `specs/PLAN.md` - Deployment

**Dependencies:** All previous phases

**Acceptance Criteria:**
- [x] CI configured (GitHub Actions/GitLab CI)
- [x] Run tests on every commit
- [x] Run linting and type checking
- [x] Auto-deploy on main branch merge (optional)
- [x] Deployment requires tests to pass
- [x] Rollback procedure documented

**Test Cases:**
- TC-7.7.1: Push code - CI runs tests
- TC-7.7.2: Tests fail - deployment blocked
- TC-7.7.3: Tests pass - can deploy
- TC-7.7.4: Deployment successful
- TC-7.7.5: Rollback works

---

### Task 7.8: Write API Documentation

**Description:** Document all API endpoints for reference.

**Spec Reference:** `specs/PLAN.md` - Documentation

**Dependencies:** Phase 4

**Acceptance Criteria:**
- [x] OpenAPI/Swagger documentation generated
- [x] POST /chat endpoint documented
- [x] Request/response schemas
- [x] Authentication requirements
- [x] Error codes explained
- [x] Examples provided
- [x] Documentation accessible (/docs)

**Test Cases:**
- TC-7.8.1: Access /docs - displays API docs
- TC-7.8.2: All endpoints listed
- TC-7.8.3: Schemas accurate
- TC-7.8.4: Examples work
- TC-7.8.5: Documentation clear

---

### Task 7.9: Write User Documentation

**Description:** Create user guide for the todo assistant chatbot.

**Spec Reference:** `specs/features/chatbot.md` - User Experience

**Dependencies:** None

**Acceptance Criteria:**
- [x] README.md updated with overview
- [x] User guide: How to create todos
- [x] User guide: How to list todos
- [x] User guide: How to update/complete/delete
- [x] Example conversations
- [x] Troubleshooting section
- [x] FAQ

**Test Cases:**
- TC-7.9.1: Documentation exists and is readable
- TC-7.9.2: All features covered
- TC-7.9.3: Examples accurate
- TC-7.9.4: FAQ answers common questions
- TC-7.9.5: Screenshots/GIFs included (optional)

---

### Task 7.10: Write Developer Documentation

**Description:** Document architecture and setup for developers.

**Spec Reference:** `specs/PLAN.md`

**Dependencies:** All phases

**Acceptance Criteria:**
- [x] CONTRIBUTING.md created
- [x] Architecture overview
- [x] Setup instructions (local development)
- [x] How to run tests
- [x] How to add new features
- [x] Code style guide
- [x] Git workflow

**Test Cases:**
- TC-7.10.1: New developer can follow setup instructions
- TC-7.10.2: Architecture diagram clear
- TC-7.10.3: Test instructions work
- TC-7.10.4: Contributing guidelines clear
- TC-7.10.5: All documentation accurate

---

## Summary

**Total Tasks:** 85 tasks across 7 phases

**Phase Breakdown:**
- Phase 1: Database Foundation - 8 tasks
- Phase 2: MCP Server Foundation - 12 tasks
- Phase 3: AI Agent Implementation - 15 tasks
- Phase 4: Backend API Implementation - 10 tasks
- Phase 5: Frontend Implementation - 20 tasks
- Phase 6: Integration & Testing - 10 tasks
- Phase 7: Deployment & Documentation - 10 tasks

**Dependencies:**
- Tasks within each phase build on each other
- Later phases depend on earlier phases
- All tasks are atomic and testable
- Each task traceable to specifications

**Next Step:** Begin implementation with Task 1.1

---

**Status:** Ready for implementation via Claude Code
**Last Updated:** 2025-12-18
