# Feature Specification: Task CRUD

> **Feature ID:** TASK-CRUD-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

This specification defines the Create, Read, Update, and Delete (CRUD) operations for tasks in the multi-user todo web application. All operations are user-scoped—users can only access and modify their own tasks.

---

## User Stories

### US-001: Create Task
**As a** registered user
**I want to** create a new task with a title and optional description
**So that** I can track work items I need to complete

**Details:**
- User must be authenticated
- Task title is required (1-255 characters)
- Description is optional (0-2000 characters)
- New tasks default to `completed = false`
- Tasks are automatically associated with the authenticated user
- Tasks receive a server-generated UUID and creation timestamp

---

### US-002: Read Task List
**As a** registered user
**I want to** view a list of all my tasks
**So that** I can see what work I have pending and completed

**Details:**
- Only tasks belonging to the authenticated user are returned
- List should display: title, completion status, created date
- Empty state shown when user has no tasks
- List is sorted by creation date (newest first) by default

---

### US-003: Read Single Task
**As a** registered user
**I want to** view the full details of a specific task
**So that** I can see the complete description and metadata

**Details:**
- User can only access their own tasks
- Returns 404 if task does not exist or belongs to another user
- Response includes: id, title, description, completed, created_at, updated_at

---

### US-004: Update Task
**As a** registered user
**I want to** edit the title and description of an existing task
**So that** I can correct mistakes or add more details

**Details:**
- User can only update their own tasks
- Partial updates allowed (PATCH semantics via PUT)
- Updated_at timestamp is automatically refreshed
- Returns 404 if task does not exist or belongs to another user

---

### US-005: Delete Task
**As a** registered user
**I want to** permanently remove a task
**So that** I can clean up completed or irrelevant items

**Details:**
- User can only delete their own tasks
- Deletion is permanent (no soft delete)
- Returns 404 if task does not exist or belongs to another user
- Returns 204 No Content on successful deletion

---

### US-006: Toggle Task Completion
**As a** registered user
**I want to** mark a task as complete or incomplete
**So that** I can track my progress

**Details:**
- Single action toggles the `completed` boolean
- User can only toggle their own tasks
- Updated_at timestamp is automatically refreshed

---

## Acceptance Criteria

### Create Task (POST /api/{user_id}/tasks)
- [ ] Request with valid title creates task and returns 201 with task object
- [ ] Request without title returns 422 with validation error
- [ ] Request with title > 255 chars returns 422 with validation error
- [ ] Request with description > 2000 chars returns 422 with validation error
- [ ] Request without valid JWT returns 401 Unauthorized
- [ ] Request with mismatched user_id (vs JWT) returns 403 Forbidden
- [ ] Created task has `completed = false` by default
- [ ] Created task has server-generated `id` (UUID v4)
- [ ] Created task has server-generated `created_at` and `updated_at` timestamps
- [ ] Response includes Location header with resource URL

### Read Task List (GET /api/{user_id}/tasks)
- [ ] Returns 200 with array of tasks belonging to the authenticated user
- [ ] Returns empty array `[]` when user has no tasks
- [ ] Does NOT return tasks belonging to other users
- [ ] Request without valid JWT returns 401 Unauthorized
- [ ] Request with mismatched user_id (vs JWT) returns 403 Forbidden
- [ ] Tasks are sorted by `created_at` descending (newest first)

### Read Single Task (GET /api/{user_id}/tasks/{task_id})
- [ ] Returns 200 with complete task object for valid request
- [ ] Returns 404 when task_id does not exist
- [ ] Returns 404 when task belongs to a different user (no information leakage)
- [ ] Request without valid JWT returns 401 Unauthorized
- [ ] Request with mismatched user_id (vs JWT) returns 403 Forbidden
- [ ] Response includes all task fields: id, title, description, completed, created_at, updated_at

### Update Task (PUT /api/{user_id}/tasks/{task_id})
- [ ] Returns 200 with updated task object for valid request
- [ ] Allows updating title only
- [ ] Allows updating description only
- [ ] Allows updating both title and description
- [ ] Validates title length (1-255 chars) if provided
- [ ] Validates description length (0-2000 chars) if provided
- [ ] Returns 404 when task_id does not exist
- [ ] Returns 404 when task belongs to a different user
- [ ] Request without valid JWT returns 401 Unauthorized
- [ ] Request with mismatched user_id (vs JWT) returns 403 Forbidden
- [ ] `updated_at` is refreshed on successful update
- [ ] Cannot update `id`, `user_id`, `created_at`, or `completed` via this endpoint

### Delete Task (DELETE /api/{user_id}/tasks/{task_id})
- [ ] Returns 204 No Content on successful deletion
- [ ] Task is permanently removed from database
- [ ] Returns 404 when task_id does not exist
- [ ] Returns 404 when task belongs to a different user
- [ ] Request without valid JWT returns 401 Unauthorized
- [ ] Request with mismatched user_id (vs JWT) returns 403 Forbidden
- [ ] Subsequent GET for deleted task returns 404

### Toggle Completion (PATCH /api/{user_id}/tasks/{task_id}/complete)
- [ ] Returns 200 with updated task object
- [ ] Toggles `completed` from `false` to `true`
- [ ] Toggles `completed` from `true` to `false`
- [ ] Returns 404 when task_id does not exist
- [ ] Returns 404 when task belongs to a different user
- [ ] Request without valid JWT returns 401 Unauthorized
- [ ] Request with mismatched user_id (vs JWT) returns 403 Forbidden
- [ ] `updated_at` is refreshed on successful toggle

---

## Edge Cases

### Input Validation
| Case | Expected Behavior |
|------|-------------------|
| Empty title (`""`) | 422 Validation Error: "Title is required" |
| Whitespace-only title (`"   "`) | 422 Validation Error: "Title cannot be blank" |
| Title with 255 chars | Accepted |
| Title with 256 chars | 422 Validation Error: "Title must be 255 characters or less" |
| Description with 2000 chars | Accepted |
| Description with 2001 chars | 422 Validation Error: "Description must be 2000 characters or less" |
| Null description | Accepted (stored as null) |
| HTML/script in title | Stored as-is; frontend must sanitize on display |
| Unicode characters in title | Accepted and preserved |
| SQL injection attempt in title | Safely escaped by ORM; stored as literal text |

### Authorization Edge Cases
| Case | Expected Behavior |
|------|-------------------|
| Expired JWT token | 401 Unauthorized with "Token expired" message |
| Malformed JWT token | 401 Unauthorized with "Invalid token" message |
| Valid JWT but user_id in URL doesn't match JWT | 403 Forbidden |
| Valid JWT for deleted/deactivated user | 401 Unauthorized |
| Missing Authorization header | 401 Unauthorized |

### Resource Edge Cases
| Case | Expected Behavior |
|------|-------------------|
| Task ID as invalid UUID format | 422 Validation Error: "Invalid task ID format" |
| Task ID as valid UUID but non-existent | 404 Not Found |
| Concurrent update to same task | Last write wins; no optimistic locking |
| Delete already-deleted task | 404 Not Found |
| Create task when at storage limit | 507 Insufficient Storage (if limits enforced) |

### Data Integrity
| Case | Expected Behavior |
|------|-------------------|
| Creating task with duplicate title (same user) | Allowed (titles are not unique) |
| Very long Unicode strings | Character count based on Unicode codepoints |
| Emoji in title/description | Accepted and preserved |
| Newlines in description | Accepted and preserved |
| Leading/trailing whitespace in title | Trimmed before storage |

---

## API Requirements

> **Reference:** See `/specs/api/rest-endpoints.md` for complete API documentation

### Endpoints Summary

| Method | Endpoint | Description | Success | Errors |
|--------|----------|-------------|---------|--------|
| `POST` | `/api/{user_id}/tasks` | Create task | 201 | 401, 403, 422 |
| `GET` | `/api/{user_id}/tasks` | List tasks | 200 | 401, 403 |
| `GET` | `/api/{user_id}/tasks/{task_id}` | Get task | 200 | 401, 403, 404 |
| `PUT` | `/api/{user_id}/tasks/{task_id}` | Update task | 200 | 401, 403, 404, 422 |
| `DELETE` | `/api/{user_id}/tasks/{task_id}` | Delete task | 204 | 401, 403, 404 |
| `PATCH` | `/api/{user_id}/tasks/{task_id}/complete` | Toggle complete | 200 | 401, 403, 404 |

### Request/Response Schemas

#### Create Task Request
```json
{
  "title": "string (required, 1-255 chars)",
  "description": "string (optional, 0-2000 chars)"
}
```

#### Task Response Object
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string | null",
  "completed": "boolean",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

#### Task List Response
```json
{
  "tasks": [
    { /* Task object */ }
  ],
  "count": "integer"
}
```

#### Update Task Request
```json
{
  "title": "string (optional, 1-255 chars if provided)",
  "description": "string (optional, 0-2000 chars if provided)"
}
```

#### Error Response
```json
{
  "detail": "string",
  "errors": [
    {
      "field": "string",
      "message": "string"
    }
  ]
}
```

### Authentication
All endpoints require:
- Header: `Authorization: Bearer <jwt_token>`
- JWT must contain `sub` claim with user ID
- URL `user_id` must match JWT `sub` claim

---

## Database/Model Notes

> **Reference:** See `/specs/database/schema.md` for complete schema documentation

### Task Table Schema

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Model Constraints
- `id`: Auto-generated UUID v4, immutable after creation
- `user_id`: Foreign key to users table, immutable after creation, cascades on user delete
- `title`: Required, 1-255 characters, trimmed whitespace
- `description`: Optional, max 2000 characters
- `completed`: Boolean, defaults to false
- `created_at`: Auto-set on creation, immutable
- `updated_at`: Auto-updated on any modification

---

## UI Considerations

### Task List View
- Display tasks in a scrollable list/table
- Show task title, completion checkbox, and creation date
- Visual distinction between completed and incomplete tasks (strikethrough, opacity)
- "No tasks yet" empty state with prompt to create first task
- Loading skeleton while fetching tasks

### Task Creation
- Inline "Add task" input at top of list for quick entry (title only)
- Modal/drawer for full task creation (title + description)
- Submit on Enter key for inline input
- Clear input after successful creation
- Show validation errors inline below input field
- Disable submit button while request is pending

### Task Detail View
- Click task title to view full details
- Display all fields: title, description, status, dates
- Edit button to enter edit mode
- Delete button with confirmation dialog

### Task Editing
- Inline editing for title in list view
- Full edit form in detail view for title + description
- Cancel button to discard changes
- Save button with loading state
- Optimistic UI updates with rollback on error

### Task Deletion
- Confirmation dialog: "Delete task '{title}'? This cannot be undone."
- Optimistic removal from list with rollback on error
- Toast notification on successful deletion

### Task Completion Toggle
- Checkbox in list view for quick toggle
- Optimistic UI update (immediate visual feedback)
- Rollback with error toast if request fails
- Animation/transition on status change

### Error Handling
- Toast notifications for operation failures
- Inline error messages for validation errors
- Retry option for network errors
- Graceful degradation when offline (future enhancement)

### Accessibility
- All interactive elements keyboard accessible
- ARIA labels for checkboxes and buttons
- Focus management on modal open/close
- Screen reader announcements for status changes
- Color contrast meets WCAG 2.1 AA

### Responsive Design
- Mobile: Single column, full-width task cards
- Tablet: Two-column grid or list
- Desktop: List view with inline actions
- Touch-friendly tap targets (min 44x44px)

---

## Testing Requirements

### Unit Tests
- [ ] Task model validation (title length, description length)
- [ ] Task creation with defaults
- [ ] Task update partial fields
- [ ] Timestamp auto-update on modification

### Integration Tests
- [ ] Create task via API and verify in database
- [ ] List tasks returns only user's tasks
- [ ] Get task by ID returns correct task
- [ ] Update task persists changes
- [ ] Delete task removes from database
- [ ] Toggle completion changes boolean value
- [ ] Unauthorized requests return 401
- [ ] Cross-user access returns 403/404

### E2E Tests
- [ ] User can create task via UI and see it in list
- [ ] User can check off task and see visual update
- [ ] User can edit task title and description
- [ ] User can delete task with confirmation
- [ ] Empty state displays when no tasks exist
- [ ] Validation errors display for invalid input

---

## Related Specifications

- `/specs/api/rest-endpoints.md` - Complete API documentation
- `/specs/database/schema.md` - Database schema definitions
- `/specs/features/authentication.md` - User authentication flow
- `/specs/agents/skills/create-task.md` - Create task agent skill
- `/specs/agents/todo-agent.md` - Task management agent

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
