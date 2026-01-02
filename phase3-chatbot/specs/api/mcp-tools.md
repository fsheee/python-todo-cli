# MCP Tools Specification

## 🎯 Overview

This document specifies the MCP (Model Context Protocol) server tools that expose todo operations to the AI agent. All tools are stateless and integrate with Phase 2 backend CRUD operations.

---

## 🏗 Architecture

### MCP Server Design

```
┌─────────────────────────────────────────────────────────┐
│                    OpenAI Agent                         │
│              (Makes tool call decisions)                │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ Tool Calls (JSON)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    MCP Server                           │
│              (Official MCP SDK)                         │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Tool Registry                                   │  │
│  │  - create_todo                                   │  │
│  │  - list_todos                                    │  │
│  │  - update_todo                                   │  │
│  │  │  - delete_todo                                   │  │
│  │  - search_todos                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Each tool:                                             │
│  1. Validates input parameters                          │
│  2. Calls Phase 2 backend endpoint                      │
│  3. Transforms response to MCP format                   │
│  4. Returns result to agent                             │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Phase 2 Backend (FastAPI)                  │
│                    CRUD Operations                      │
│  - POST /todos                                          │
│  - GET /todos                                           │
│  - PUT /todos/{id}                                      │
│  - DELETE /todos/{id}                                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Neon PostgreSQL Database                   │
└─────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Stateless Design:** Tools don't maintain state between calls
2. **Phase 2 Reuse:** Tools wrap existing CRUD endpoints, never access database directly
3. **User Isolation:** All operations require `user_id` parameter from validated JWT
4. **Error Propagation:** Backend errors are caught and returned in standardized format
5. **Type Safety:** Strong input validation using JSON schemas

---

## 🛠 Tool Definitions

### Tool 1: create_todo

**Purpose:** Create a new todo item for the user

**MCP Tool Signature:**
```json
{
  "name": "create_todo",
  "description": "Create a new todo item for the authenticated user. Returns the created todo with its ID.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "ID of the authenticated user (from JWT token)"
      },
      "title": {
        "type": "string",
        "description": "Title of the todo (required, max 200 chars)",
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "Detailed description of the todo (optional, max 1000 chars)",
        "maxLength": 1000
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Priority level (optional, defaults to 'medium')"
      },
      "due_date": {
        "type": "string",
        "format": "date-time",
        "description": "Due date in ISO 8601 format (optional, e.g., '2025-12-25T00:00:00Z')"
      }
    },
    "required": ["user_id", "title"]
  }
}
```

**Phase 2 Backend Mapping:**
- **Endpoint:** `POST /todos`
- **Headers:** `Authorization: Bearer <internal_service_token>`
- **Body:**
```json
{
  "user_id": 123,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "due_date": "2025-12-19T00:00:00Z"
}
```

**Response Format:**
```json
{
  "success": true,
  "todo": {
    "id": 456,
    "user_id": 123,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "priority": "high",
    "due_date": "2025-12-19T00:00:00Z",
    "created_at": "2025-12-18T10:30:00Z",
    "updated_at": "2025-12-18T10:30:00Z"
  },
  "message": "Todo created successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Validation error: title is required",
  "code": "VALIDATION_ERROR"
}
```

**Implementation Example:**
```python
async def create_todo(user_id: int, title: str, description: str = None,
                      priority: str = "medium", due_date: str = None) -> dict:
    """
    MCP tool: Create a new todo item
    """
    try:
        # Validate inputs
        if not title or len(title.strip()) == 0:
            return {
                "success": False,
                "error": "Title cannot be empty",
                "code": "VALIDATION_ERROR"
            }

        if len(title) > 200:
            return {
                "success": False,
                "error": "Title exceeds maximum length of 200 characters",
                "code": "VALIDATION_ERROR"
            }

        # Prepare request to Phase 2 backend
        payload = {
            "user_id": user_id,
            "title": title.strip(),
            "status": "pending"
        }

        if description:
            payload["description"] = description.strip()

        if priority:
            payload["priority"] = priority

        if due_date:
            payload["due_date"] = due_date

        # Call Phase 2 backend
        response = await http_client.post(
            f"{PHASE2_API_URL}/todos",
            json=payload,
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )

        if response.status_code == 201:
            todo = response.json()
            return {
                "success": True,
                "todo": todo,
                "message": "Todo created successfully"
            }
        else:
            error_data = response.json()
            return {
                "success": False,
                "error": error_data.get("detail", "Failed to create todo"),
                "code": "BACKEND_ERROR"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Internal error: {str(e)}",
            "code": "INTERNAL_ERROR"
        }
```

**Validation Rules:**
- `user_id`: Must be positive integer
- `title`: Required, non-empty, max 200 chars
- `description`: Optional, max 1000 chars
- `priority`: Must be one of ["low", "medium", "high"]
- `due_date`: Must be valid ISO 8601 datetime, future date recommended

**Edge Cases:**
1. **Empty title:** Return validation error
2. **Very long title:** Truncate or reject
3. **Past due date:** Accept but flag as immediately overdue
4. **Invalid priority:** Default to "medium"
5. **Backend unavailable:** Return service unavailable error

---

### Tool 2: list_todos

**Purpose:** Retrieve user's todos with optional filters

**MCP Tool Signature:**
```json
{
  "name": "list_todos",
  "description": "Retrieve todos for the authenticated user with optional filters for status, priority, and due date. Returns an array of todo items.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "ID of the authenticated user (from JWT token)"
      },
      "status": {
        "type": "string",
        "enum": ["pending", "completed", "all"],
        "description": "Filter by status (optional, defaults to 'pending')"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Filter by priority (optional)"
      },
      "due_date": {
        "type": "string",
        "format": "date",
        "description": "Filter by due date (optional, e.g., '2025-12-25')"
      },
      "due_date_range": {
        "type": "string",
        "enum": ["today", "tomorrow", "this_week", "next_week", "overdue"],
        "description": "Filter by relative date range (optional)"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results (optional, default 50, max 100)",
        "minimum": 1,
        "maximum": 100
      },
      "offset": {
        "type": "integer",
        "description": "Number of results to skip for pagination (optional, default 0)",
        "minimum": 0
      }
    },
    "required": ["user_id"]
  }
}
```

**Phase 2 Backend Mapping:**
- **Endpoint:** `GET /todos`
- **Query Parameters:**
  - `user_id={user_id}`
  - `status={status}` (optional)
  - `priority={priority}` (optional)
  - `due_date={due_date}` (optional)
  - `limit={limit}` (optional)
  - `offset={offset}` (optional)
- **Headers:** `Authorization: Bearer <internal_service_token>`

**Response Format:**
```json
{
  "success": true,
  "todos": [
    {
      "id": 456,
      "user_id": 123,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "priority": "high",
      "due_date": "2025-12-19T00:00:00Z",
      "created_at": "2025-12-18T10:30:00Z",
      "updated_at": "2025-12-18T10:30:00Z"
    },
    {
      "id": 457,
      "user_id": 123,
      "title": "Call dentist",
      "description": null,
      "status": "pending",
      "priority": "medium",
      "due_date": "2025-12-19T00:00:00Z",
      "created_at": "2025-12-18T09:15:00Z",
      "updated_at": "2025-12-18T09:15:00Z"
    }
  ],
  "count": 2,
  "total": 15,
  "has_more": true
}
```

**Implementation Example:**
```python
async def list_todos(user_id: int, status: str = "pending", priority: str = None,
                     due_date: str = None, due_date_range: str = None,
                     limit: int = 50, offset: int = 0) -> dict:
    """
    MCP tool: List todos with filters
    """
    try:
        # Build query parameters
        params = {
            "user_id": user_id,
            "limit": min(limit, 100),
            "offset": offset
        }

        if status and status != "all":
            params["status"] = status

        if priority:
            params["priority"] = priority

        # Handle date filters
        if due_date_range:
            # Convert relative range to actual dates
            date_filter = calculate_date_range(due_date_range)
            params.update(date_filter)
        elif due_date:
            params["due_date"] = due_date

        # Call Phase 2 backend
        response = await http_client.get(
            f"{PHASE2_API_URL}/todos",
            params=params,
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "todos": data.get("todos", []),
                "count": len(data.get("todos", [])),
                "total": data.get("total", 0),
                "has_more": data.get("has_more", False)
            }
        else:
            return {
                "success": False,
                "error": "Failed to retrieve todos",
                "code": "BACKEND_ERROR"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Internal error: {str(e)}",
            "code": "INTERNAL_ERROR"
        }

def calculate_date_range(range_type: str) -> dict:
    """
    Convert relative date range to start/end dates
    """
    today = datetime.now().date()

    if range_type == "today":
        return {"due_date": today.isoformat()}
    elif range_type == "tomorrow":
        return {"due_date": (today + timedelta(days=1)).isoformat()}
    elif range_type == "this_week":
        week_end = today + timedelta(days=(6 - today.weekday()))
        return {"due_date_start": today.isoformat(), "due_date_end": week_end.isoformat()}
    elif range_type == "next_week":
        next_week_start = today + timedelta(days=(7 - today.weekday()))
        next_week_end = next_week_start + timedelta(days=6)
        return {"due_date_start": next_week_start.isoformat(), "due_date_end": next_week_end.isoformat()}
    elif range_type == "overdue":
        return {"due_date_end": (today - timedelta(days=1)).isoformat(), "status": "pending"}
    else:
        return {}
```

**Edge Cases:**
1. **No todos found:** Return empty array with count 0
2. **Invalid date range:** Return all todos with warning
3. **Pagination beyond results:** Return empty array
4. **Conflicting filters:** Prioritize more specific filter

---

### Tool 3: update_todo

**Purpose:** Update an existing todo item

**MCP Tool Signature:**
```json
{
  "name": "update_todo",
  "description": "Update an existing todo item. Only provided fields will be updated. Returns the updated todo.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "ID of the authenticated user (from JWT token)"
      },
      "todo_id": {
        "type": "integer",
        "description": "ID of the todo to update"
      },
      "title": {
        "type": "string",
        "description": "New title (optional)",
        "maxLength": 200
      },
      "description": {
        "type": "string",
        "description": "New description (optional, use empty string to clear)",
        "maxLength": 1000
      },
      "status": {
        "type": "string",
        "enum": ["pending", "completed"],
        "description": "New status (optional)"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "New priority (optional)"
      },
      "due_date": {
        "type": "string",
        "format": "date-time",
        "description": "New due date in ISO 8601 format (optional, use null to clear)"
      }
    },
    "required": ["user_id", "todo_id"]
  }
}
```

**Phase 2 Backend Mapping:**
- **Endpoint:** `PUT /todos/{todo_id}`
- **Headers:** `Authorization: Bearer <internal_service_token>`
- **Body:** Only fields to update
```json
{
  "user_id": 123,
  "priority": "high",
  "due_date": "2025-12-20T00:00:00Z"
}
```

**Response Format:**
```json
{
  "success": true,
  "todo": {
    "id": 456,
    "user_id": 123,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "pending",
    "priority": "high",
    "due_date": "2025-12-20T00:00:00Z",
    "created_at": "2025-12-18T10:30:00Z",
    "updated_at": "2025-12-18T14:25:00Z"
  },
  "message": "Todo updated successfully",
  "changes": ["priority", "due_date"]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Todo not found or access denied",
  "code": "NOT_FOUND"
}
```

**Implementation Example:**
```python
async def update_todo(user_id: int, todo_id: int, title: str = None,
                      description: str = None, status: str = None,
                      priority: str = None, due_date: str = None) -> dict:
    """
    MCP tool: Update an existing todo
    """
    try:
        # Build update payload with only provided fields
        updates = {"user_id": user_id}
        changes = []

        if title is not None:
            if len(title.strip()) == 0:
                return {
                    "success": False,
                    "error": "Title cannot be empty",
                    "code": "VALIDATION_ERROR"
                }
            updates["title"] = title.strip()
            changes.append("title")

        if description is not None:
            updates["description"] = description.strip() if description else None
            changes.append("description")

        if status is not None:
            updates["status"] = status
            changes.append("status")

        if priority is not None:
            updates["priority"] = priority
            changes.append("priority")

        if due_date is not None:
            updates["due_date"] = due_date
            changes.append("due_date")

        # Check if there are any updates
        if not changes:
            return {
                "success": False,
                "error": "No fields to update",
                "code": "VALIDATION_ERROR"
            }

        # Call Phase 2 backend
        response = await http_client.put(
            f"{PHASE2_API_URL}/todos/{todo_id}",
            json=updates,
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )

        if response.status_code == 200:
            todo = response.json()
            return {
                "success": True,
                "todo": todo,
                "message": "Todo updated successfully",
                "changes": changes
            }
        elif response.status_code == 404:
            return {
                "success": False,
                "error": "Todo not found or access denied",
                "code": "NOT_FOUND"
            }
        else:
            return {
                "success": False,
                "error": "Failed to update todo",
                "code": "BACKEND_ERROR"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Internal error: {str(e)}",
            "code": "INTERNAL_ERROR"
        }
```

**Validation Rules:**
- `user_id`: Must match todo owner (enforced by backend)
- `todo_id`: Must exist and belong to user
- `title`: If provided, cannot be empty
- At least one field must be provided for update

**Edge Cases:**
1. **Todo not found:** Return NOT_FOUND error
2. **Access denied:** User tries to update another user's todo
3. **No changes provided:** Return validation error
4. **Empty title update:** Reject with error
5. **Status change to completed:** Update updated_at timestamp

---

### Tool 4: delete_todo

**Purpose:** Delete a todo item (soft or hard delete)

**MCP Tool Signature:**
```json
{
  "name": "delete_todo",
  "description": "Delete a todo item. This action is permanent and cannot be undone. Returns confirmation of deletion.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "ID of the authenticated user (from JWT token)"
      },
      "todo_id": {
        "type": "integer",
        "description": "ID of the todo to delete"
      },
      "confirm": {
        "type": "boolean",
        "description": "Confirmation flag (must be true for deletion to proceed)",
        "default": false
      }
    },
    "required": ["user_id", "todo_id", "confirm"]
  }
}
```

**Phase 2 Backend Mapping:**
- **Endpoint:** `DELETE /todos/{todo_id}`
- **Query Parameters:** `user_id={user_id}`
- **Headers:** `Authorization: Bearer <internal_service_token>`

**Response Format:**
```json
{
  "success": true,
  "message": "Todo deleted successfully",
  "deleted_todo": {
    "id": 456,
    "title": "Buy groceries"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Todo not found or access denied",
  "code": "NOT_FOUND"
}
```

**Implementation Example:**
```python
async def delete_todo(user_id: int, todo_id: int, confirm: bool = False) -> dict:
    """
    MCP tool: Delete a todo item
    """
    try:
        # Safety check: require confirmation
        if not confirm:
            return {
                "success": False,
                "error": "Deletion requires confirmation. Set confirm=true to proceed.",
                "code": "CONFIRMATION_REQUIRED"
            }

        # First, fetch the todo to get its details for confirmation message
        get_response = await http_client.get(
            f"{PHASE2_API_URL}/todos/{todo_id}",
            params={"user_id": user_id},
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )

        if get_response.status_code != 200:
            return {
                "success": False,
                "error": "Todo not found or access denied",
                "code": "NOT_FOUND"
            }

        todo = get_response.json()

        # Delete the todo
        delete_response = await http_client.delete(
            f"{PHASE2_API_URL}/todos/{todo_id}",
            params={"user_id": user_id},
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )

        if delete_response.status_code == 200:
            return {
                "success": True,
                "message": "Todo deleted successfully",
                "deleted_todo": {
                    "id": todo["id"],
                    "title": todo["title"]
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to delete todo",
                "code": "BACKEND_ERROR"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Internal error: {str(e)}",
            "code": "INTERNAL_ERROR"
        }
```

**Validation Rules:**
- `user_id`: Must match todo owner
- `todo_id`: Must exist and belong to user
- `confirm`: Must be explicitly set to true

**Edge Cases:**
1. **Todo not found:** Return NOT_FOUND error
2. **Access denied:** User tries to delete another user's todo
3. **Missing confirmation:** Return CONFIRMATION_REQUIRED error
4. **Already deleted:** Return NOT_FOUND error
5. **Backend error during deletion:** Return error but don't retry automatically

**Safety Features:**
- Requires explicit `confirm=true` parameter
- Agent should ask user for confirmation before calling with confirm=true
- Returns deleted todo details for potential undo feature

---

### Tool 5: search_todos

**Purpose:** Search todos by keyword in title and description

**MCP Tool Signature:**
```json
{
  "name": "search_todos",
  "description": "Search todos by keyword. Searches in both title and description fields. Returns matching todos ranked by relevance.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "ID of the authenticated user (from JWT token)"
      },
      "query": {
        "type": "string",
        "description": "Search keyword or phrase",
        "minLength": 1,
        "maxLength": 100
      },
      "status": {
        "type": "string",
        "enum": ["pending", "completed", "all"],
        "description": "Filter results by status (optional, defaults to 'all')"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results (optional, default 20, max 50)",
        "minimum": 1,
        "maximum": 50
      }
    },
    "required": ["user_id", "query"]
  }
}
```

**Phase 2 Backend Mapping:**
- **Endpoint:** `GET /todos/search`
- **Query Parameters:**
  - `user_id={user_id}`
  - `q={query}`
  - `status={status}` (optional)
  - `limit={limit}` (optional)
- **Headers:** `Authorization: Bearer <internal_service_token>`

**Response Format:**
```json
{
  "success": true,
  "todos": [
    {
      "id": 456,
      "user_id": 123,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "priority": "high",
      "due_date": "2025-12-19T00:00:00Z",
      "created_at": "2025-12-18T10:30:00Z",
      "updated_at": "2025-12-18T10:30:00Z",
      "relevance_score": 0.95,
      "match_location": "title"
    }
  ],
  "count": 1,
  "query": "groceries"
}
```

**Implementation Example:**
```python
async def search_todos(user_id: int, query: str, status: str = "all",
                       limit: int = 20) -> dict:
    """
    MCP tool: Search todos by keyword
    """
    try:
        # Validate query
        if not query or len(query.strip()) == 0:
            return {
                "success": False,
                "error": "Search query cannot be empty",
                "code": "VALIDATION_ERROR"
            }

        # Clean and prepare query
        clean_query = query.strip()[:100]

        # Build parameters
        params = {
            "user_id": user_id,
            "q": clean_query,
            "limit": min(limit, 50)
        }

        if status and status != "all":
            params["status"] = status

        # Call Phase 2 backend search endpoint
        response = await http_client.get(
            f"{PHASE2_API_URL}/todos/search",
            params=params,
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "todos": data.get("todos", []),
                "count": len(data.get("todos", [])),
                "query": clean_query
            }
        else:
            return {
                "success": False,
                "error": "Search failed",
                "code": "BACKEND_ERROR"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Internal error: {str(e)}",
            "code": "INTERNAL_ERROR"
        }
```

**Search Algorithm (Backend Implementation):**
```python
# This is implemented in Phase 2 backend, not MCP server
def search_todos_in_db(user_id: int, query: str, status: str = None):
    """
    Full-text search in todos table
    """
    # Use PostgreSQL full-text search or simple ILIKE
    sql = """
        SELECT *,
               ts_rank(
                   to_tsvector('english', title || ' ' || COALESCE(description, '')),
                   to_tsquery('english', %(query)s)
               ) as relevance_score,
               CASE
                   WHEN title ILIKE %(pattern)s THEN 'title'
                   WHEN description ILIKE %(pattern)s THEN 'description'
                   ELSE 'other'
               END as match_location
        FROM todos
        WHERE user_id = %(user_id)s
          AND (title ILIKE %(pattern)s OR description ILIKE %(pattern)s)
          {status_filter}
        ORDER BY relevance_score DESC, created_at DESC
        LIMIT %(limit)s
    """
    # Execute and return results
```

**Validation Rules:**
- `query`: Required, non-empty, max 100 chars
- `user_id`: Must be valid user
- `limit`: Max 50 results

**Edge Cases:**
1. **Empty query:** Return validation error
2. **No matches:** Return empty array with count 0
3. **Special characters:** Escape SQL injection attempts
4. **Very short query (1-2 chars):** May return many results
5. **Query with stop words:** Filter or handle appropriately

---

## 🔐 Security and Authentication

### Service-to-Service Authentication

**Problem:** MCP server needs to call Phase 2 backend endpoints that are protected by Better Auth.

**Solution:** Internal service token

```python
# Environment variable
SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN")

# All backend requests include service token
headers = {
    "Authorization": f"Bearer {SERVICE_TOKEN}",
    "X-Internal-Service": "mcp-server"
}
```

### User Isolation Enforcement

**Critical:** Every tool call MUST include `user_id` parameter

**Enforcement Layers:**

1. **MCP Tool Level:**
```python
# All tools require user_id as first parameter
async def create_todo(user_id: int, title: str, ...) -> dict:
    # user_id is required and validated
    pass
```

2. **Backend API Level:**
```python
# Phase 2 backend validates user_id
@app.post("/todos")
async def create_todo_endpoint(todo_data: TodoCreate, user_id: int):
    # Verify user_id matches authenticated user from service token
    # Or validate against internal whitelist
    # Then proceed with database operation
    pass
```

3. **Database Level:**
```sql
-- All queries include user_id filter
SELECT * FROM todos WHERE user_id = $1 AND id = $2;
```

### Parameter Validation

**All tools validate inputs before calling backend:**

```python
def validate_user_id(user_id: int) -> bool:
    """Validate user_id is positive integer"""
    return isinstance(user_id, int) and user_id > 0

def validate_todo_id(todo_id: int) -> bool:
    """Validate todo_id is positive integer"""
    return isinstance(todo_id, int) and todo_id > 0

def validate_priority(priority: str) -> bool:
    """Validate priority is valid enum value"""
    return priority in ["low", "medium", "high"]

def validate_status(status: str) -> bool:
    """Validate status is valid enum value"""
    return status in ["pending", "completed"]

def validate_date(date_str: str) -> bool:
    """Validate date is ISO 8601 format"""
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except:
        return False
```

---

## 🔧 MCP Server Implementation

### Server Setup

```python
from mcp import Server, Tool
from mcp.server import stdio_server
import asyncio

# Initialize MCP server
app = Server("todo-mcp-server")

# Register all tools
@app.tool()
async def create_todo(user_id: int, title: str, description: str = None,
                      priority: str = "medium", due_date: str = None) -> dict:
    """Create a new todo item for the authenticated user"""
    # Implementation here
    pass

@app.tool()
async def list_todos(user_id: int, status: str = "pending",
                     priority: str = None, due_date: str = None,
                     due_date_range: str = None, limit: int = 50,
                     offset: int = 0) -> dict:
    """Retrieve todos with optional filters"""
    # Implementation here
    pass

@app.tool()
async def update_todo(user_id: int, todo_id: int, title: str = None,
                      description: str = None, status: str = None,
                      priority: str = None, due_date: str = None) -> dict:
    """Update an existing todo item"""
    # Implementation here
    pass

@app.tool()
async def delete_todo(user_id: int, todo_id: int, confirm: bool = False) -> dict:
    """Delete a todo item"""
    # Implementation here
    pass

@app.tool()
async def search_todos(user_id: int, query: str, status: str = "all",
                       limit: int = 20) -> dict:
    """Search todos by keyword"""
    # Implementation here
    pass

# Run server
if __name__ == "__main__":
    asyncio.run(stdio_server(app))
```

### Configuration

```yaml
# config.yaml
mcp_server:
  name: "todo-mcp-server"
  version: "1.0.0"
  phase2_api_url: "https://api.example.com/v1"
  service_token: "${INTERNAL_SERVICE_TOKEN}"
  timeout: 30
  retry_attempts: 3
  retry_delay: 1
```

### Environment Variables

```bash
# .env
INTERNAL_SERVICE_TOKEN=your_service_token_here
PHASE2_API_URL=https://api.example.com/v1
MCP_SERVER_PORT=8080
LOG_LEVEL=INFO
```

---

## 📊 Error Codes

### Standard Error Codes

| Code | Description | HTTP Status | Retry? |
|------|-------------|-------------|--------|
| `VALIDATION_ERROR` | Input validation failed | 400 | No |
| `NOT_FOUND` | Todo not found or access denied | 404 | No |
| `BACKEND_ERROR` | Phase 2 backend error | 500 | Yes |
| `INTERNAL_ERROR` | MCP server internal error | 500 | Yes |
| `TIMEOUT` | Backend request timeout | 504 | Yes |
| `CONFIRMATION_REQUIRED` | Action requires confirmation | 400 | No |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 | Yes (after delay) |
| `SERVICE_UNAVAILABLE` | Backend service down | 503 | Yes |

### Error Response Format

```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "title",
    "issue": "exceeds maximum length"
  },
  "timestamp": "2025-12-18T10:30:00Z",
  "request_id": "req_abc123"
}
```

---

## 🧪 Testing Strategy

### Unit Tests for Each Tool

```python
import pytest
from mcp_server import create_todo, list_todos, update_todo, delete_todo, search_todos

@pytest.mark.asyncio
async def test_create_todo_success():
    result = await create_todo(
        user_id=123,
        title="Test task",
        priority="high"
    )
    assert result["success"] == True
    assert result["todo"]["title"] == "Test task"
    assert result["todo"]["priority"] == "high"

@pytest.mark.asyncio
async def test_create_todo_empty_title():
    result = await create_todo(
        user_id=123,
        title=""
    )
    assert result["success"] == False
    assert result["code"] == "VALIDATION_ERROR"

@pytest.mark.asyncio
async def test_list_todos_with_filters():
    result = await list_todos(
        user_id=123,
        status="pending",
        priority="high"
    )
    assert result["success"] == True
    assert isinstance(result["todos"], list)

@pytest.mark.asyncio
async def test_update_todo_not_found():
    result = await update_todo(
        user_id=123,
        todo_id=99999,
        title="Updated"
    )
    assert result["success"] == False
    assert result["code"] == "NOT_FOUND"

@pytest.mark.asyncio
async def test_delete_todo_requires_confirmation():
    result = await delete_todo(
        user_id=123,
        todo_id=456,
        confirm=False
    )
    assert result["success"] == False
    assert result["code"] == "CONFIRMATION_REQUIRED"

@pytest.mark.asyncio
async def test_search_todos_empty_query():
    result = await search_todos(
        user_id=123,
        query=""
    )
    assert result["success"] == False
    assert result["code"] == "VALIDATION_ERROR"
```

### Integration Tests

```python
@pytest.mark.integration
async def test_full_todo_lifecycle():
    """Test create → update → complete → delete flow"""
    user_id = 123

    # Create
    create_result = await create_todo(user_id, "Test task")
    assert create_result["success"] == True
    todo_id = create_result["todo"]["id"]

    # List and verify
    list_result = await list_todos(user_id)
    assert any(t["id"] == todo_id for t in list_result["todos"])

    # Update
    update_result = await update_todo(user_id, todo_id, priority="high")
    assert update_result["success"] == True

    # Complete
    complete_result = await update_todo(user_id, todo_id, status="completed")
    assert complete_result["success"] == True

    # Delete
    delete_result = await delete_todo(user_id, todo_id, confirm=True)
    assert delete_result["success"] == True

    # Verify deleted
    list_result = await list_todos(user_id, status="all")
    assert not any(t["id"] == todo_id for t in list_result["todos"])
```

---

## 📈 Performance Considerations

### Response Time Targets

| Tool | Target | P95 | P99 |
|------|--------|-----|-----|
| `create_todo` | <200ms | 300ms | 500ms |
| `list_todos` | <300ms | 500ms | 1s |
| `update_todo` | <200ms | 300ms | 500ms |
| `delete_todo` | <250ms | 400ms | 600ms |
| `search_todos` | <400ms | 700ms | 1.5s |

### Optimization Strategies

1. **Connection Pooling:**
```python
# Reuse HTTP connections to Phase 2 backend
http_client = httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=20),
    timeout=httpx.Timeout(30.0)
)
```

2. **Request Timeout:**
```python
# Set reasonable timeouts
BACKEND_TIMEOUT = 10  # seconds
```

3. **Caching (Future Enhancement):**
```python
# Cache frequently accessed todos
# Cache user statistics
# Invalidate on updates
```

4. **Batch Operations (Future Enhancement):**
```python
# Allow batch create/update/delete
# Useful for "complete all today's tasks"
```

---

## 🔗 Related Specifications

- [../features/chatbot.md](../features/chatbot.md) - Chatbot features using these tools
- [../agents/todo-agent.md](../agents/todo-agent.md) - Agent that calls these tools
- [../database/chat-history.md](../database/chat-history.md) - Conversation persistence
- [../../CLAUDE.md](../../CLAUDE.md) - Project constitution

---

## 📋 Implementation Checklist

- [ ] Set up Official MCP SDK
- [ ] Implement all 5 tools with proper signatures
- [ ] Add input validation for all parameters
- [ ] Implement Phase 2 backend client
- [ ] Add service-to-service authentication
- [ ] Implement error handling and standardized responses
- [ ] Add comprehensive logging
- [ ] Write unit tests for each tool (>90% coverage)
- [ ] Write integration tests for workflows
- [ ] Set up monitoring and alerting
- [ ] Document API responses
- [ ] Performance test and optimize

---

**Status:** Draft - Ready for Review
**Last Updated:** 2025-12-18
