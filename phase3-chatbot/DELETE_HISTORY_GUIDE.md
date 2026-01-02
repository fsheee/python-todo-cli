# Delete History/Prompt Logic - Complete Guide

## Overview

This guide explains all the deletion operations available for managing chat history and prompts in Phase 3. The system supports both **soft delete** (reversible) and **hard delete** (permanent) operations.

---

## Deletion Types

### 1. Soft Delete (Reversible)
- Marks sessions as deleted without removing files
- Can be restored later
- Automatically cleaned up after 90 days (configurable)
- Default behavior for safety

### 2. Hard Delete (Permanent)
- Permanently removes session files
- Cannot be undone
- Immediate file system deletion
- Requires explicit `permanent=True` flag

---

## Available Operations

### Operation 1: Delete Single Session

**Purpose:** Delete one conversation session

**Methods:**
- **Soft Delete:** Mark as deleted, can restore later
- **Hard Delete:** Permanently remove from filesystem

**API Endpoint:**
```http
POST /history/delete-session
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "session_id": "sess_1703433600_a7f3k9x2",
  "permanent": false
}
```

**Python Usage:**
```python
from app.storage import FileBasedChatStorage

storage = FileBasedChatStorage()

# Soft delete (can restore)
success = storage.delete_session(
    user_id=123,
    session_id="sess_1703433600_a7f3k9x2"
)

# Hard delete (permanent)
success = storage.delete_session_permanent(
    user_id=123,
    session_id="sess_1703433600_a7f3k9x2"
)
```

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

---

### Operation 2: Delete Multiple Sessions

**Purpose:** Batch delete several sessions at once

**API Endpoint:**
```http
POST /history/delete-multiple-sessions
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "session_ids": [
    "sess_1703433600_a7f3k9x2",
    "sess_1703433700_b8g4m1y3",
    "sess_1703433800_c9h5n2z4"
  ],
  "permanent": false
}
```

**Python Usage:**
```python
results = storage.delete_multiple_sessions(
    user_id=123,
    session_ids=[
        "sess_1703433600_a7f3k9x2",
        "sess_1703433700_b8g4m1y3",
        "sess_1703433800_c9h5n2z4"
    ],
    permanent=False
)

# Results: {"sess_1703433600_a7f3k9x2": True, "sess_...": True, ...}
```

**Response:**
```json
{
  "success": true,
  "message": "3 sessions deleted successfully",
  "deleted_count": 3
}
```

---

### Operation 3: Delete All User Sessions

**Purpose:** Delete ALL sessions for a user (nuclear option)

**⚠️ WARNING:** This affects ALL user sessions. Requires explicit confirmation.

**API Endpoint:**
```http
POST /history/delete-all-sessions
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "permanent": false,
  "confirm": true
}
```

**Python Usage:**
```python
deleted_count = storage.delete_all_user_sessions(
    user_id=123,
    permanent=False,
    confirm=True  # REQUIRED - safety check
)
```

**Response:**
```json
{
  "success": true,
  "message": "All 15 sessions deleted successfully",
  "deleted_count": 15
}
```

**Error without confirmation:**
```json
{
  "detail": "Must confirm deletion of all sessions with confirm=true"
}
```

---

### Operation 4: Delete Specific Messages

**Purpose:** Delete individual messages within a session

**API Endpoint:**
```http
POST /history/delete-messages
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "session_id": "sess_1703433600_a7f3k9x2",
  "message_sequences": [1, 3, 5]
}
```

**Python Usage:**
```python
deleted_count = storage.delete_messages_in_session(
    user_id=123,
    session_id="sess_1703433600_a7f3k9x2",
    message_sequences=[1, 3, 5]  # Delete messages 1, 3, and 5
)
```

**What Happens:**
1. Individual message files are deleted
2. `conversation.json` is rebuilt without deleted messages
3. `conversation.md` is regenerated
4. Session metadata is updated

**Response:**
```json
{
  "success": true,
  "message": "3 messages deleted successfully",
  "deleted_count": 3
}
```

---

### Operation 5: Restore Deleted Session

**Purpose:** Restore a soft-deleted session

**API Endpoint:**
```http
POST /history/restore-session
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "session_id": "sess_1703433600_a7f3k9x2"
}
```

**Python Usage:**
```python
success = storage.restore_session(
    user_id=123,
    session_id="sess_1703433600_a7f3k9x2"
)
```

**Response:**
```json
{
  "success": true,
  "message": "Session restored successfully"
}
```

**Error Cases:**
- Session not found: `404 Not Found`
- Session not deleted: `Session is not deleted, cannot restore`

---

### Operation 6: Cleanup Old Deleted Sessions

**Purpose:** Automatically clean up old soft-deleted sessions

**Scheduled Task:**
```python
# Run daily via cron job or scheduler
deleted_count = storage.cleanup_old_sessions(days=90)
```

**Process:**
1. Finds all sessions with `status="deleted"`
2. Checks if `deleted_at` is older than N days
3. Permanently deletes those sessions

**Configuration:**
```bash
# .env
CHAT_RETENTION_DAYS=90  # Default retention period
```

---

### Operation 7: Get Deleted Sessions

**Purpose:** View all soft-deleted sessions (recycle bin)

**API Endpoint:**
```http
GET /history/deleted-sessions?limit=50
Authorization: Bearer {jwt_token}
```

**Python Usage:**
```python
deleted_sessions = storage.get_deleted_sessions(
    user_id=123,
    limit=50
)
```

**Response:**
```json
[
  {
    "session_id": "sess_1703433600_a7f3k9x2",
    "user_id": 123,
    "created_at": "2025-12-24T10:00:00Z",
    "updated_at": "2025-12-24T10:35:00Z",
    "deleted_at": "2025-12-24T11:00:00Z",
    "message_count": 8,
    "status": "deleted"
  }
]
```

---

## File System Changes

### Soft Delete
**Before:**
```
sessions/sess_1703433600_a7f3k9x2/
├── metadata.json         # status: "active"
├── conversation.md
├── conversation.json
└── messages/
```

**After:**
```
sessions/sess_1703433600_a7f3k9x2/
├── metadata.json         # status: "deleted", deleted_at: "..."
├── conversation.md       # Still exists
├── conversation.json     # Still exists
└── messages/            # Still exists
```

### Hard Delete
**Before:**
```
sessions/sess_1703433600_a7f3k9x2/
├── metadata.json
├── conversation.md
├── conversation.json
└── messages/
```

**After:**
```
sessions/
# Directory completely removed
```

### Message Deletion
**Before:**
```
messages/
├── 001_user_2025-12-24T10-00-15.json
├── 002_assistant_2025-12-24T10-00-18.json
├── 003_user_2025-12-24T10-01-30.json
└── 004_assistant_2025-12-24T10-01-35.json
```

**After (deleting message 2):**
```
messages/
├── 001_user_2025-12-24T10-00-15.json
├── 003_user_2025-12-24T10-01-30.json
└── 004_assistant_2025-12-24T10-01-35.json

# conversation.json and conversation.md are rebuilt
```

---

## Safety Features

### 1. Confirmation Required
```python
# This will raise an error
storage.delete_all_user_sessions(user_id=123, confirm=False)
# ValueError: Must confirm deletion of all sessions with confirm=True

# This will work
storage.delete_all_user_sessions(user_id=123, confirm=True)
```

### 2. User Isolation
```python
# User 123 cannot delete User 456's sessions
storage.delete_session(user_id=123, session_id="user_456_session")
# Returns: False (not found)
```

### 3. Soft Delete Default
```python
# Default is soft delete (safe)
storage.delete_session(user_id=123, session_id="sess_...")

# Must explicitly request permanent deletion
storage.delete_session_permanent(user_id=123, session_id="sess_...")
```

### 4. Logging
All deletion operations are logged:
```python
logger.info("Soft deleted session sess_... for user 123")
logger.warning("Deleted ALL 15 sessions for user 123 (permanent)")
```

---

## Usage Examples

### Example 1: User Wants to Clear Recent Conversations

```python
# Get last 10 sessions
sessions = storage.get_user_sessions(user_id=123, limit=10)

# Soft delete them (can restore later)
session_ids = [s["session_id"] for s in sessions]
results = storage.delete_multiple_sessions(
    user_id=123,
    session_ids=session_ids,
    permanent=False
)

print(f"Deleted {sum(results.values())} sessions")
```

### Example 2: User Wants to Delete Specific Messages

```python
# User regrets sending messages 3 and 4
deleted_count = storage.delete_messages_in_session(
    user_id=123,
    session_id="sess_abc123",
    message_sequences=[3, 4]
)

print(f"Deleted {deleted_count} messages")
# conversation.json and conversation.md are automatically rebuilt
```

### Example 3: User Accidentally Deleted a Session

```python
# User wants it back
success = storage.restore_session(
    user_id=123,
    session_id="sess_abc123"
)

if success:
    print("Session restored!")
else:
    print("Session not found or already active")
```

### Example 4: Admin Cleanup Old Data

```python
# Run as scheduled task (e.g., daily cron job)
deleted_count = storage.cleanup_old_sessions(days=90)
print(f"Cleaned up {deleted_count} old sessions")
```

### Example 5: GDPR Data Deletion Request

```python
# User requests all their data be deleted
deleted_count = storage.delete_all_user_sessions(
    user_id=123,
    permanent=True,  # Permanent deletion
    confirm=True     # Required confirmation
)

print(f"Permanently deleted all {deleted_count} sessions")
```

---

## Frontend Integration

### Delete Single Session Button

```typescript
async function deleteSession(sessionId: string, permanent: boolean = false) {
  const response = await fetch('/history/delete-session', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      permanent: permanent
    })
  });

  const result = await response.json();
  return result;
}

// Usage in component
<button onClick={() => deleteSession('sess_abc123', false)}>
  Delete Conversation
</button>
```

### Restore Session from Recycle Bin

```typescript
async function restoreSession(sessionId: string) {
  const response = await fetch('/history/restore-session', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId
    })
  });

  return await response.json();
}

// Show deleted sessions
const deletedSessions = await fetch('/history/deleted-sessions?limit=20', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Restore button for each
deletedSessions.map(session => (
  <button onClick={() => restoreSession(session.session_id)}>
    Restore
  </button>
));
```

### Clear All History with Confirmation

```typescript
async function clearAllHistory(permanent: boolean = false) {
  // Show confirmation dialog
  const confirmed = window.confirm(
    `Are you sure you want to ${permanent ? 'permanently' : 'temporarily'} delete ALL conversations? ` +
    `This action ${permanent ? 'cannot be undone' : 'can be undone within 90 days'}.`
  );

  if (!confirmed) return;

  const response = await fetch('/history/delete-all-sessions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      permanent: permanent,
      confirm: true
    })
  });

  const result = await response.json();
  alert(`${result.deleted_count} conversations deleted`);
}
```

---

## Best Practices

### 1. Always Use Soft Delete First
```python
# Good: Soft delete first (reversible)
storage.delete_session(user_id, session_id)

# Risky: Permanent delete immediately
storage.delete_session_permanent(user_id, session_id)
```

### 2. Implement Recycle Bin UI
```typescript
// Show deleted sessions to users
// Allow easy restoration within retention period
const recycleBin = await getDeletedSessions();
```

### 3. Schedule Cleanup Tasks
```bash
# cron job: Run daily at 2am
0 2 * * * /usr/bin/python cleanup_sessions.py
```

### 4. Log All Deletions
```python
# All delete operations are automatically logged
# Review logs regularly for audit purposes
```

### 5. Request Confirmation for Bulk Operations
```python
# Always require explicit confirmation for delete-all
if not confirm:
    raise ValueError("Confirmation required")
```

---

## Error Handling

### Common Errors

**1. Session Not Found**
```json
{
  "detail": "Session sess_abc123 not found",
  "status_code": 404
}
```

**2. Confirmation Missing**
```json
{
  "detail": "Must confirm deletion of all sessions with confirm=true",
  "status_code": 400
}
```

**3. Authentication Failed**
```json
{
  "detail": "Invalid or expired token",
  "status_code": 401
}
```

**4. Already Deleted**
```json
{
  "detail": "Session is not deleted, cannot restore",
  "status_code": 400
}
```

---

## Testing

### Unit Tests

```python
def test_soft_delete_session():
    storage = FileBasedChatStorage(base_path="test-data")
    storage.create_session(123, "sess_test")

    # Soft delete
    success = storage.delete_session(123, "sess_test")
    assert success == True

    # Session marked as deleted
    sessions = storage.get_user_sessions(123)
    assert len(sessions) == 0  # Not in active list

    # But still exists in deleted list
    deleted = storage.get_deleted_sessions(123)
    assert len(deleted) == 1

def test_restore_session():
    storage = FileBasedChatStorage(base_path="test-data")
    storage.create_session(123, "sess_test")
    storage.delete_session(123, "sess_test")

    # Restore
    success = storage.restore_session(123, "sess_test")
    assert success == True

    # Session back in active list
    sessions = storage.get_user_sessions(123)
    assert len(sessions) == 1

def test_permanent_delete():
    storage = FileBasedChatStorage(base_path="test-data")
    storage.create_session(123, "sess_test")

    # Permanent delete
    success = storage.delete_session_permanent(123, "sess_test")
    assert success == True

    # Session completely gone
    session_path = storage._get_session_path(123, "sess_test")
    assert not session_path.exists()
```

---

## Summary

The deletion system provides flexible options:

1. **Soft Delete** - Safe, reversible, default behavior
2. **Hard Delete** - Permanent, requires explicit flag
3. **Bulk Operations** - Delete multiple sessions efficiently
4. **Message-Level** - Delete specific messages within sessions
5. **Restoration** - Recover soft-deleted sessions
6. **Auto-Cleanup** - Remove old deleted sessions automatically

All operations are:
- User-isolated (can't delete other users' data)
- Logged for audit trails
- Protected with confirmations
- Accessible via REST API and Python SDK

---

**Last Updated:** 2025-12-24
