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
- [ ] Criterion 1
- [ ] Criterion 2

**Test Cases:**
- TC-X: [Test description]
```

---

## Phase 1: Database Foundation (8 tasks)

### Task 1.1: Create Database Migration for ChatHistory Table

**Description:** Create Alembic migration file to add chat_history table with all required fields and constraints.

**Spec Reference:** `specs/database/chat-history.md` - Schema Definition

**Dependencies:** None (first task)

**Acceptance Criteria:**
- [ ] Migration file created in `migrations/versions/003_create_chat_history.py`
- [ ] Table definition includes all 8 fields (id, user_id, session_id, role, content, metadata, timestamp, is_deleted)
- [ ] Foreign key to users table with ON DELETE CASCADE
- [ ] CHECK constraint on role field (user/assistant/system)
- [ ] Default values for timestamp and is_deleted
- [ ] Migration runs successfully with `alembic upgrade head`
- [ ] Migration can be rolled back with `alembic downgrade -1`

**Test Cases:**
- TC-1.1.1: Run migration on clean database - succeeds
- TC-1.1.2: Rollback migration - succeeds
- TC-1.1.3: Verify foreign key constraint - cascades on user delete
- TC-1.1.4: Verify role CHECK constraint - rejects invalid values

---

### Task 1.2: Create Database Indexes for ChatHistory

**Description:** Create performance indexes for common query patterns on chat_history table.

**Spec Reference:** `specs/database/chat-history.md` - Indexing Strategy

**Dependencies:** Task 1.1

**Acceptance Criteria:**
- [ ] Index on user_id created
- [ ] Index on session_id created
- [ ] Index on timestamp created
- [ ] Composite index on (user_id, session_id, is_deleted, timestamp DESC) created
- [ ] All indexes created successfully
- [ ] Query planner uses indexes (verify with EXPLAIN ANALYZE)

**Test Cases:**
- TC-1.2.1: Query by user_id - uses index
- TC-1.2.2: Query by session_id - uses index
- TC-1.2.3: Query with user_id + session_id - uses composite index
- TC-1.2.4: Sort by timestamp DESC - uses index

---

### Task 1.3: Define ChatHistory SQLModel

**Description:** Create SQLModel class for ChatHistory with proper field types and validation.

**Spec Reference:** `specs/database/chat-history.md` - SQLModel Model

**Dependencies:** Task 1.1

**Acceptance Criteria:**
- [ ] ChatHistory class defined in `app/models/chat_history.py`
- [ ] All fields properly typed (int, str, datetime, Dict, bool)
- [ ] Field constraints match database schema (max_length, nullable)
- [ ] Foreign key relationship to User model
- [ ] JSON/JSONB column for metadata field
- [ ] Default factories for timestamp and is_deleted
- [ ] Model validates correctly

**Test Cases:**
- TC-1.3.1: Create instance with all fields - succeeds
- TC-1.3.2: Create instance with minimal fields - succeeds
- TC-1.3.3: Invalid role value - validation fails
- TC-1.3.4: Metadata as dict - serializes to JSON correctly

---

### Task 1.4: Implement load_chat_history Query Function

**Description:** Create async function to load recent chat messages for a user session.

**Spec Reference:** `specs/database/chat-history.md` - Query 1

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [ ] Function signature: `async def load_chat_history(session, user_id, session_id, limit=20) -> list[ChatHistory]`
- [ ] Filters by user_id, session_id, and is_deleted=False
- [ ] Orders by timestamp DESC
- [ ] Limits to specified number of messages
- [ ] Returns messages in chronological order (oldest first)
- [ ] Returns empty list if no messages found

**Test Cases:**
- TC-1.4.1: Load 5 messages from session with 10 - returns 5 most recent
- TC-1.4.2: Load from empty session - returns empty list
- TC-1.4.3: Load with limit=20 from session with 25 - returns last 20
- TC-1.4.4: User A cannot load User B's messages - returns empty
- TC-1.4.5: Soft-deleted messages excluded from results

---

### Task 1.5: Implement save_message Mutation Function

**Description:** Create async function to save a new chat message to database.

**Spec Reference:** `specs/database/chat-history.md` - Query 2

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [ ] Function signature: `async def save_message(session, user_id, session_id, role, content, metadata=None) -> ChatHistory`
- [ ] Creates new ChatHistory instance
- [ ] Sets timestamp automatically
- [ ] Commits to database
- [ ] Refreshes instance to get generated ID
- [ ] Returns saved message with ID

**Test Cases:**
- TC-1.5.1: Save user message - succeeds, returns ID
- TC-1.5.2: Save assistant message with metadata - succeeds
- TC-1.5.3: Save without metadata - succeeds with None
- TC-1.5.4: Timestamp auto-generated - within 1 second of now
- TC-1.5.5: Invalid user_id - foreign key error

---

### Task 1.6: Implement get_user_sessions Query Function

**Description:** Create async function to retrieve all sessions for a user with summary info.

**Spec Reference:** `specs/database/chat-history.md` - Query 3

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [ ] Function signature: `async def get_user_sessions(session, user_id, limit=50) -> list[Dict]`
- [ ] Groups by session_id
- [ ] Aggregates: MIN(timestamp) as started_at, MAX(timestamp) as last_message_at, COUNT(*) as message_count
- [ ] Filters is_deleted=False
- [ ] Orders by last_message_at DESC
- [ ] Returns list of dicts with session metadata

**Test Cases:**
- TC-1.6.1: User with 3 sessions - returns 3 summaries
- TC-1.6.2: Each summary has started_at, last_message_at, message_count
- TC-1.6.3: Ordered by most recent first
- TC-1.6.4: User with no sessions - returns empty list
- TC-1.6.5: Limit works correctly

---

### Task 1.7: Implement delete_session Soft Delete Function

**Description:** Create async function to soft delete all messages in a session.

**Spec Reference:** `specs/database/chat-history.md` - Query 4

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [ ] Function signature: `async def delete_session(session, user_id, session_id) -> int`
- [ ] Updates is_deleted=True for all matching messages
- [ ] Filters by user_id and session_id
- [ ] Only affects messages where is_deleted=False
- [ ] Returns count of deleted messages
- [ ] Commits transaction

**Test Cases:**
- TC-1.7.1: Delete session with 10 messages - returns 10
- TC-1.7.2: Messages no longer appear in load_chat_history
- TC-1.7.3: Delete non-existent session - returns 0
- TC-1.7.4: User A cannot delete User B's session - returns 0
- TC-1.7.5: Double delete same session - second returns 0

---

### Task 1.8: Implement cleanup_old_deleted_sessions Maintenance Function

**Description:** Create async function to permanently delete old soft-deleted messages.

**Spec Reference:** `specs/database/chat-history.md` - Query 6

**Dependencies:** Task 1.3

**Acceptance Criteria:**
- [ ] Function signature: `async def cleanup_old_deleted_sessions(session, days=90) -> int`
- [ ] Calculates cutoff date (now - days)
- [ ] Deletes messages where is_deleted=True AND timestamp < cutoff
- [ ] Returns count of permanently deleted messages
- [ ] Commits transaction

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
- [ ] Directory created: `mcp_server/`
- [ ] Install mcp-sdk package
- [ ] Install httpx for HTTP calls
- [ ] Create `mcp_server/__init__.py`
- [ ] Create `mcp_server/server.py` (main file)
- [ ] Create `mcp_server/config.py` for configuration
- [ ] Create `requirements.txt` with dependencies
- [ ] Server can be imported successfully

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
- [ ] Server instance created with name "todo-mcp-server"
- [ ] STDIO protocol configured
- [ ] Server can start successfully
- [ ] Server can be stopped gracefully
- [ ] Logging configured (INFO level)

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
- [ ] Environment variables defined: PHASE2_API_URL, INTERNAL_SERVICE_TOKEN
- [ ] Config class loads from environment
- [ ] Default values for development
- [ ] Validation for required variables
- [ ] HTTP client timeout configurable

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
- [ ] httpx.AsyncClient created with connection pooling
- [ ] Service token added to Authorization header
- [ ] X-Internal-Service header added
- [ ] Timeout configured (30 seconds)
- [ ] Connection reuse enabled
- [ ] Client can be closed properly

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
- [ ] Tool registered with @mcp_server.tool() decorator
- [ ] Input schema: user_id (int), title (str), description (str?), priority (str?), due_date (str?)
- [ ] Input validation: user_id > 0, title non-empty, max 200 chars
- [ ] Priority validation: must be low/medium/high or None
- [ ] HTTP POST to Phase 2: /todos
- [ ] Returns {success: bool, todo: dict, message: str}
- [ ] Error handling for all failure cases

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
- [ ] Tool registered with @mcp_server.tool() decorator
- [ ] Input schema: user_id (int), status (str?), priority (str?), due_date (str?), due_date_range (str?), limit (int), offset (int)
- [ ] Date range conversion: today/tomorrow/this_week/next_week/overdue → actual dates
- [ ] HTTP GET to Phase 2: /todos with query parameters
- [ ] Returns {success: bool, todos: list, count: int, total: int, has_more: bool}
- [ ] Handles empty results gracefully

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
- [ ] Tool registered with @mcp_server.tool() decorator
- [ ] Input schema: user_id (int), todo_id (int), title (str?), description (str?), status (str?), priority (str?), due_date (str?)
- [ ] Validation: at least one field to update
- [ ] Validation: title not empty if provided
- [ ] HTTP PUT to Phase 2: /todos/{todo_id}
- [ ] Returns {success: bool, todo: dict, message: str, changes: list}
- [ ] Tracks which fields were changed

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
- [ ] Tool registered with @mcp_server.tool() decorator
- [ ] Input schema: user_id (int), todo_id (int), confirm (bool)
- [ ] Validation: confirm must be True explicitly
- [ ] Fetch todo first to get details
- [ ] HTTP DELETE to Phase 2: /todos/{todo_id}
- [ ] Returns {success: bool, deleted_todo: dict, message: str}
- [ ] Returns CONFIRMATION_REQUIRED if confirm=False

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
- [ ] Tool registered with @mcp_server.tool() decorator
- [ ] Input schema: user_id (int), query (str), status (str?), limit (int)
- [ ] Validation: query non-empty, max 100 chars
- [ ] Query sanitization to prevent injection
- [ ] HTTP GET to Phase 2: /todos/search?q={query}&user_id={user_id}
- [ ] Returns {success: bool, todos: list, count: int, query: str}
- [ ] Handles no results gracefully

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
- [ ] user_id validation: positive integer
- [ ] todo_id validation: positive integer
- [ ] title validation: non-empty, max length
- [ ] priority validation: enum check
- [ ] status validation: enum check
- [ ] date validation: ISO 8601 format
- [ ] Returns consistent error format

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
- [ ] Try-catch blocks around all HTTP calls
- [ ] Backend timeout handling (30s)
- [ ] Backend unavailable handling
- [ ] Network error handling
- [ ] Standardized error response format
- [ ] Error codes: VALIDATION_ERROR, NOT_FOUND, BACKEND_ERROR, TIMEOUT, INTERNAL_ERROR

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
- [ ] Test file: `tests/test_mcp_tools.py`
- [ ] Mock HTTP client for Phase 2 calls
- [ ] Test all success paths
- [ ] Test all error paths
- [ ] Test input validation
- [ ] >95% code coverage for MCP tools

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
- [ ] Install openai package (latest version)
- [ ] Create `app/agents/` directory
- [ ] Create `app/agents/__init__.py`
- [ ] Environment variable: OPENAI_API_KEY
- [ ] OpenAI client initialized successfully
- [ ] API key validated (test connection)

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
- [ ] System prompt template created in `app/agents/prompts.py`
- [ ] Includes role definition (helpful AI assistant)
- [ ] Includes capabilities list
- [ ] Includes guidelines (friendly, concise, confirm actions)
- [ ] Includes important rules (user_id security, date calculations)
- [ ] Template supports variable injection (current_date, user_timezone)
- [ ] Prompt is clear and well-structured

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
- [ ] Function: `build_agent_context(user_id, session_id, user_email) -> str`
- [ ] Loads last 20 messages from chat_history
- [ ] Formats messages as OpenAI message format
- [ ] Includes user stats (pending count, completed today)
- [ ] Includes current date and timezone
- [ ] Returns formatted context string

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
- [ ] All 5 tools registered with OpenAI function calling
- [ ] Function schemas match MCP tool schemas
- [ ] Tool descriptions are clear and helpful
- [ ] Parameter descriptions guide the agent
- [ ] Required parameters marked correctly
- [ ] Agent can see all available tools

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
- [ ] Recognizes 9 intent types: CREATE_TODO, LIST_TODOS, UPDATE_TODO, COMPLETE_TODO, DELETE_TODO, SEARCH_TODOS, GET_DETAILS, HELP, GREETING
- [ ] Pattern matching for each intent
- [ ] Confidence scoring (0.0 to 1.0)
- [ ] Returns intent + confidence + extracted parameters
- [ ] Handles ambiguous input gracefully

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
- [ ] Extracts title from create requests
- [ ] Extracts due_date from natural language ("tomorrow", "next Friday")
- [ ] Extracts priority from text ("high priority", "urgent")
- [ ] Extracts filters from list requests
- [ ] Extracts search query
- [ ] Extracts todo identifiers (title match, number reference)

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
- [ ] CREATE_TODO intent → create_todo tool
- [ ] LIST_TODOS intent → list_todos tool
- [ ] UPDATE_TODO intent → search first if needed, then update_todo
- [ ] COMPLETE_TODO intent → update_todo with status="completed"
- [ ] DELETE_TODO intent → search first if needed, then delete_todo (with confirmation)
- [ ] SEARCH_TODOS intent → search_todos tool
- [ ] HELP/GREETING → no tool, direct response
- [ ] Handles multi-step flows (search then action)

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
- [ ] Stores last list_todos result in context (expires after 5 messages)
- [ ] Resolves numeric references ("task 1", "the second one")
- [ ] Stores last created/updated task (expires after 3 messages)
- [ ] Resolves pronoun references ("it", "that one")
- [ ] Handles expired context gracefully (asks for clarification)
- [ ] Reference storage persists within conversation turn

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
- [ ] Templates for all response types (create, list, update, complete, delete, search, error)
- [ ] Multiple variations per type (avoid repetition)
- [ ] Includes emojis appropriately
- [ ] Formatting rules (bullets, numbers)
- [ ] Personalization (encouragement, empathy)
- [ ] Templates support variable substitution

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
- [ ] Formats create_todo result: "I've created {title}..."
- [ ] Formats list_todos result: numbered list with details
- [ ] Formats update_todo result: "Updated! {title} is now {change}"
- [ ] Formats delete_todo result: "Done! {title} has been removed"
- [ ] Formats search_todos result: numbered list with highlights
- [ ] Formats errors: clear message + suggestion
- [ ] Keeps responses under 150 words

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
- [ ] Function: `async def process_chat_message(user_id, session_id, message, history) -> dict`
- [ ] Builds context from history
- [ ] Calls OpenAI Agent with context + message
- [ ] Agent recognizes intent and selects tool
- [ ] Agent calls appropriate MCP tool
- [ ] Agent generates response from tool result
- [ ] Returns {content: str, metadata: dict}
- [ ] Handles all error cases

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
- [ ] Detects ambiguous input (low confidence, missing params)
- [ ] Asks specific clarifying questions
- [ ] Multiple matches - lists options with numbers
- [ ] Missing required info - asks for it
- [ ] Unclear date - asks for specific date
- [ ] Provides examples in questions

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
- [ ] Handles OpenAI API errors (rate limit, timeout)
- [ ] Handles MCP tool errors (propagates error codes)
- [ ] Handles invalid context errors
- [ ] Never exposes technical details to user
- [ ] Always provides recovery suggestions
- [ ] Logs errors for debugging

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
- [ ] Log every user message processed
- [ ] Log recognized intent and confidence
- [ ] Log tool calls with parameters
- [ ] Log tool responses
- [ ] Log generated responses
- [ ] Log errors with full context
- [ ] Structured logging (JSON format)

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
- [ ] Test file: `tests/test_agent.py`
- [ ] Mock OpenAI API calls
- [ ] Mock MCP tool calls
- [ ] Test all intent recognition
- [ ] Test tool selection logic
- [ ] Test reference resolution
- [ ] Test response generation
- [ ] >85% code coverage

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
- [ ] Endpoint: POST /chat
- [ ] Request schema: {message: str, session_id: str}
- [ ] Response schema: {response: str, session_id: str, timestamp: str}
- [ ] Validates JWT token (extracts user_id)
- [ ] Returns 401 if unauthorized
- [ ] Returns 400 if invalid input
- [ ] Returns 200 with response on success

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
- [ ] Middleware validates JWT using BETTER_AUTH_SECRET
- [ ] Extracts user_id from validated token
- [ ] Injects user_id into request context
- [ ] Returns 401 for invalid/expired tokens
- [ ] Works with Better Auth JWT format

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
- [ ] Loads last 20 messages using load_chat_history()
- [ ] Filters by user_id and session_id
- [ ] Formats for agent consumption
- [ ] Handles empty history gracefully
- [ ] Query optimized (uses indexes)

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
- [ ] Saves user message using save_message()
- [ ] Sets role="user"
- [ ] Includes metadata (client_ip, user_agent)
- [ ] Committed to database before agent call
- [ ] Returns message ID

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
- [ ] Calls process_chat_message() with user_id, session_id, message, history
- [ ] Passes loaded history to agent
- [ ] Receives agent response with content and metadata
- [ ] Handles agent errors gracefully
- [ ] Timeout protection (30 seconds)

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
- [ ] Saves assistant message using save_message()
- [ ] Sets role="assistant"
- [ ] Includes metadata (tool_calls, tokens_used)
- [ ] Committed to database before returning response
- [ ] Returns message ID

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
- [ ] Database errors caught and logged
- [ ] Agent errors caught and returned gracefully
- [ ] Validation errors return 400 with clear message
- [ ] Internal errors return 500 (but user sees friendly message)
- [ ] All errors logged with full context
- [ ] Error response format consistent

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
- [ ] Log incoming requests (method, path, user_id, session_id)
- [ ] Log response status and timing
- [ ] Log message length (for monitoring)
- [ ] Structured logging (JSON format)
- [ ] Don't log sensitive data (message content optional)
- [ ] Performance metrics tracked

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
- [ ] Rate limit: 30 requests per minute per user
- [ ] Returns 429 when limit exceeded
- [ ] Rate limit headers in response
- [ ] Redis or in-memory store for counters
- [ ] Configurable limits

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
- [ ] Test file: `tests/test_chat_endpoint.py`
- [ ] Test complete flow: request → agent → tools → database → response
- [ ] Test authentication flow
- [ ] Test error scenarios
- [ ] Test conversation continuity
- [ ] Tests use test database

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
- [ ] Project created with `npm create vite@latest`
- [ ] TypeScript template selected
- [ ] Project structure created
- [ ] Dev server runs successfully
- [ ] Build succeeds

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
- [ ] Install @openai/chatkit
- [ ] Install axios
- [ ] Install zustand
- [ ] Install react-router-dom
- [ ] All dependencies in package.json
- [ ] node_modules populated

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
- [ ] src/components/ created
- [ ] src/pages/ created
- [ ] src/stores/ created
- [ ] src/api/ created
- [ ] src/utils/ created
- [ ] src/styles/ created
- [ ] Index files in each directory

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
- [ ] File: src/stores/authStore.ts
- [ ] State: token, user, isAuthenticated
- [ ] Actions: login(), logout()
- [ ] Persists to localStorage
- [ ] TypeScript interfaces defined
- [ ] Store can be imported and used

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
- [ ] File: src/utils/sessionManager.ts
- [ ] Function: generateSessionId() -> string (format: sess_{timestamp}_{random})
- [ ] Function: getSessionId() -> string (get or create)
- [ ] Function: startNewSession() -> string
- [ ] Function: clearSession() -> void
- [ ] Uses localStorage for persistence

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
- [ ] File: src/api/chatApi.ts
- [ ] Axios instance with base URL from env
- [ ] Request interceptor adds JWT token
- [ ] Response interceptor handles 401 (logout)
- [ ] Timeout set to 30 seconds
- [ ] TypeScript types for all API calls

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
- [ ] Function: sendChatMessage(message, sessionId) -> Promise<ChatResponse>
- [ ] POST to /chat endpoint
- [ ] Sends {message, session_id} in body
- [ ] Returns {response, session_id, timestamp}
- [ ] Handles errors and throws
- [ ] TypeScript types for request/response

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
- [ ] Function: loadChatHistory(sessionId) -> Promise<ChatMessage[]>
- [ ] GET to /chat/history/{sessionId}
- [ ] Returns array of messages
- [ ] Handles empty history
- [ ] TypeScript types defined

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
- [ ] File: src/pages/LoginPage.tsx
- [ ] Form with email and password fields
- [ ] Submit calls /auth/login endpoint
- [ ] On success: stores token and redirects to /chat
- [ ] On error: displays error message
- [ ] Loading state during submission
- [ ] Responsive design

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
- [ ] File: src/App.tsx
- [ ] React Router setup (BrowserRouter)
- [ ] Routes: /login, /chat, / (redirect)
- [ ] Protected routes (require authentication)
- [ ] Public routes (redirect if authenticated)
- [ ] Layout wrapper if needed

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
- [ ] File: src/components/TodoChatInterface.tsx
- [ ] State: messages, isLoading, sessionId
- [ ] Loads session ID on mount
- [ ] Loads chat history on mount (optional)
- [ ] Handler: handleSendMessage()
- [ ] Handler: handleNewConversation()
- [ ] Handler: handleLogout()
- [ ] Renders ChatKit component

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
- [ ] Validates non-empty message
- [ ] Adds user message to UI immediately
- [ ] Sets loading state
- [ ] Calls sendChatMessage()
- [ ] Adds assistant response to UI
- [ ] Handles errors (shows error message in UI)
- [ ] Clears loading state

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
- [ ] ChatKit component imported and rendered
- [ ] Props: messages, onSendMessage, isLoading
- [ ] Props: placeholder, welcomeMessage, theme
- [ ] Props: showTimestamps, enableMarkdown
- [ ] ChatKit displays messages correctly
- [ ] Input field functional

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
- [ ] Custom renderMessage function
- [ ] Formats **bold** and *italic*
- [ ] Formats `code` snippets
- [ ] Renders line breaks
- [ ] Displays emojis correctly
- [ ] Formats timestamps

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
- [ ] Shows app title "Todo Assistant"
- [ ] Displays user email
- [ ] Button: "New Chat"
- [ ] Button: "Logout"
- [ ] Responsive design
- [ ] Styling matches design

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
- [ ] Click "New Chat" button
- [ ] Generates new session ID
- [ ] Clears messages array
- [ ] Updates localStorage
- [ ] Shows confirmation toast (optional)

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
- [ ] File: src/styles/TodoChatInterface.css
- [ ] Container layout (header + chat area)
- [ ] Header styling
- [ ] Message styling (user vs assistant)
- [ ] Loading indicator styling
- [ ] Responsive design (mobile-first)
- [ ] Emoji support

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
- [ ] Toast component or library integrated
- [ ] Success toasts (green)
- [ ] Error toasts (red)
- [ ] Info toasts (blue)
- [ ] Auto-dismiss after 3 seconds
- [ ] Positioned correctly (top-right)

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
- [ ] File: .env.development
- [ ] File: .env.production
- [ ] Variable: VITE_API_URL
- [ ] Variable: VITE_APP_NAME (optional)
- [ ] Variables loaded correctly in code
- [ ] .env files in .gitignore

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
- [ ] Test files for each component
- [ ] Test library: @testing-library/react
- [ ] Test rendering
- [ ] Test user interactions
- [ ] Test API calls (mocked)
- [ ] >80% component coverage

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
- [ ] Test database configured
- [ ] Migrations run on test DB
- [ ] Test DB isolated from development DB
- [ ] Can be reset between tests
- [ ] Environment variable for test DB URL

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
- [ ] Test file: tests/integration/test_database.py
- [ ] Test all query functions
- [ ] Test user isolation
- [ ] Test soft delete
- [ ] Test cleanup
- [ ] Uses test database

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
- [ ] Test file: tests/integration/test_mcp_tools.py
- [ ] Mock Phase 2 HTTP responses
- [ ] Test all tools end-to-end
- [ ] Test error scenarios
- [ ] Test with real MCP server

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
- [ ] Test file: tests/integration/test_agent.py
- [ ] Mock OpenAI API responses
- [ ] Use real MCP tools (with mocked backend)
- [ ] Test complete conversation flows
- [ ] Test all intents

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
- [ ] Test file: tests/integration/test_api.py
- [ ] Uses TestClient from FastAPI
- [ ] Tests with real database (test DB)
- [ ] Tests authentication flow
- [ ] Tests complete message flow
- [ ] Tests error scenarios

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
- [ ] Test file: tests/e2e/test_conversations.py
- [ ] Tests complete user flows
- [ ] Tests: create, list, update, complete, delete todos
- [ ] Tests multi-turn conversations
- [ ] Tests context and reference resolution
- [ ] Uses all layers (frontend API, backend, agent, MCP, database)

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
- [ ] Test chat endpoint response time <2s
- [ ] Test database queries <100ms
- [ ] Test concurrent users (10 simultaneous)
- [ ] Test message throughput
- [ ] Identify bottlenecks

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
- [ ] Test JWT validation
- [ ] Test user isolation (User A cannot access User B's data)
- [ ] Test SQL injection prevention
- [ ] Test XSS prevention in messages
- [ ] Test rate limiting
- [ ] Test service token validation (MCP to Phase 2)

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
- [ ] Test OpenAI API failure
- [ ] Test Phase 2 backend unavailable
- [ ] Test database connection failure
- [ ] Test network timeouts
- [ ] Test partial failures
- [ ] Verify graceful degradation

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
- [ ] Coverage tool configured (pytest-cov)
- [ ] Generate coverage report
- [ ] Backend coverage >90%
- [ ] MCP tools coverage >95%
- [ ] Agent coverage >85%
- [ ] Frontend coverage >80%
- [ ] Identify gaps

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
- [ ] Production .env template created
- [ ] All required environment variables documented
- [ ] Secrets management strategy defined
- [ ] Database connection string for Neon
- [ ] CORS settings configured
- [ ] Production vs development differences documented

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
- [ ] Backup existing database
- [ ] Run alembic upgrade head
- [ ] Verify all tables created
- [ ] Verify all indexes created
- [ ] Test queries work
- [ ] Document rollback procedure

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
- [ ] Install dependencies on server
- [ ] Set environment variables
- [ ] Start MCP server process
- [ ] Configure process manager (systemd/supervisor)
- [ ] Test server responds
- [ ] Set up logging

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
- [ ] Install dependencies
- [ ] Set environment variables
- [ ] Start with uvicorn (multiple workers)
- [ ] Configure reverse proxy (nginx)
- [ ] Enable HTTPS
- [ ] Health check endpoint works

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
- [ ] Run npm run build
- [ ] Set production environment variables
- [ ] Deploy to Vercel/Netlify/similar
- [ ] Configure custom domain (optional)
- [ ] HTTPS enabled
- [ ] Test production build locally first

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
- [ ] Logging aggregation (e.g., CloudWatch, Papertrail)
- [ ] Error tracking (e.g., Sentry)
- [ ] Performance monitoring (response times)
- [ ] Uptime monitoring (e.g., UptimeRobot)
- [ ] Alerts configured for critical issues
- [ ] Dashboard accessible

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
- [ ] CI configured (GitHub Actions/GitLab CI)
- [ ] Run tests on every commit
- [ ] Run linting and type checking
- [ ] Auto-deploy on main branch merge (optional)
- [ ] Deployment requires tests to pass
- [ ] Rollback procedure documented

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
- [ ] OpenAPI/Swagger documentation generated
- [ ] POST /chat endpoint documented
- [ ] Request/response schemas
- [ ] Authentication requirements
- [ ] Error codes explained
- [ ] Examples provided
- [ ] Documentation accessible (/docs)

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
- [ ] README.md updated with overview
- [ ] User guide: How to create todos
- [ ] User guide: How to list todos
- [ ] User guide: How to update/complete/delete
- [ ] Example conversations
- [ ] Troubleshooting section
- [ ] FAQ

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
- [ ] CONTRIBUTING.md created
- [ ] Architecture overview
- [ ] Setup instructions (local development)
- [ ] How to run tests
- [ ] How to add new features
- [ ] Code style guide
- [ ] Git workflow

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
