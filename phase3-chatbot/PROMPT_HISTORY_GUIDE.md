# User Prompt History - Complete Guide

## Overview

This guide explains the user prompt history tracking system in Phase 3. The system saves all user prompts separately from conversations, enabling analytics, search, and historical review.

---

## Storage Structure

### File Organization

```
data/chat-history/users/{user_id}/
├── prompt-history/
│   ├── 2025-12/                      # Organized by month
│   │   ├── prompts-2025-12-24.jsonl  # Daily JSONL files
│   │   ├── prompts-2025-12-23.jsonl
│   │   └── prompts-2025-12-22.jsonl
│   ├── 2025-11/
│   │   ├── prompts-2025-11-30.jsonl
│   │   └── ...
│   └── prompt-index.json             # Searchable index
└── sessions/                         # Regular conversation sessions
```

### Why Separate Prompt History?

1. **Analytics** - Track what users are asking over time
2. **Search** - Quickly find previous prompts without loading full conversations
3. **Statistics** - Analyze prompt patterns, frequency, length
4. **Privacy** - Users can delete prompts separately from conversations
5. **Performance** - JSONL format is efficient for append-only operations

---

## Prompt Entry Format

### JSONL Entry Example

```json
{
  "prompt_id": "prompt_1703433600123456",
  "user_id": 123,
  "session_id": "sess_1703433600_a7f3k9x2",
  "prompt": "Show me my high priority tasks",
  "timestamp": "2025-12-24T10:30:15.123456Z",
  "date": "2025-12-24",
  "metadata": {
    "intent": "LIST_TODOS",
    "tokens": 8,
    "response_time_ms": 850,
    "client_ip": "192.168.1.1"
  }
}
```

### Prompt Index Format

```json
{
  "user_id": 123,
  "last_updated": "2025-12-24T10:30:15Z",
  "total_prompts": 342,
  "dates": ["2025-12-01", "2025-12-02", "...", "2025-12-24"]
}
```

---

## Core Operations

### 1. Save Prompt

**Purpose:** Automatically save user prompts to history

**Python Usage:**
```python
from app.storage import FileBasedChatStorage

storage = FileBasedChatStorage()

# Save a prompt
prompt_entry = storage.save_prompt(
    user_id=123,
    prompt="Show me my tasks",
    session_id="sess_abc123",  # Optional
    metadata={                   # Optional
        "intent": "LIST_TODOS",
        "tokens": 5,
        "response_time_ms": 750
    }
)

print(f"Saved prompt: {prompt_entry['prompt_id']}")
```

**What Happens:**
1. Creates `prompt-history/` directory if needed
2. Creates month directory (e.g., `2025-12/`)
3. Appends to daily JSONL file (`prompts-2025-12-24.jsonl`)
4. Updates prompt index for fast lookups

**Response:**
```python
{
  "prompt_id": "prompt_1703433600123456",
  "user_id": 123,
  "session_id": "sess_abc123",
  "prompt": "Show me my tasks",
  "timestamp": "2025-12-24T10:30:15.123456Z",
  "date": "2025-12-24",
  "metadata": {...}
}
```

---

### 2. Get Prompt History

**Purpose:** Retrieve user's prompt history with filters

**API Endpoint:**
```http
GET /prompts/history?limit=100&offset=0&start_date=2025-12-01&end_date=2025-12-24
Authorization: Bearer {jwt_token}
```

**Python Usage:**
```python
# Get last 100 prompts
prompts = storage.get_prompt_history(
    user_id=123,
    limit=100,
    offset=0
)

# Filter by date range
prompts = storage.get_prompt_history(
    user_id=123,
    start_date="2025-12-01",
    end_date="2025-12-24",
    limit=100
)

# Filter by session
prompts = storage.get_prompt_history(
    user_id=123,
    session_id="sess_abc123",
    limit=50
)
```

**Response:**
```json
[
  {
    "prompt_id": "prompt_1703433600123456",
    "user_id": 123,
    "session_id": "sess_abc123",
    "prompt": "Show me my tasks",
    "timestamp": "2025-12-24T10:30:15Z",
    "date": "2025-12-24",
    "metadata": {...}
  },
  ...
]
```

---

### 3. Search Prompts

**Purpose:** Search through prompt history by text

**API Endpoint:**
```http
GET /prompts/search?query=high%20priority&limit=50
Authorization: Bearer {jwt_token}
```

**Python Usage:**
```python
# Search for prompts containing "high priority"
matching_prompts = storage.search_prompts(
    user_id=123,
    query="high priority",
    limit=50
)

for prompt in matching_prompts:
    print(f"[{prompt['timestamp']}] {prompt['prompt']}")
```

**Search Features:**
- Case-insensitive
- Partial matching
- Returns results in chronological order (newest first)

**Response:**
```json
[
  {
    "prompt_id": "prompt_...",
    "prompt": "Show me my high priority tasks",
    "timestamp": "2025-12-24T10:30:15Z",
    ...
  },
  {
    "prompt_id": "prompt_...",
    "prompt": "Add high priority task to call client",
    "timestamp": "2025-12-23T15:20:00Z",
    ...
  }
]
```

---

### 4. Get Prompt Statistics

**Purpose:** Analyze user's prompt patterns

**API Endpoint:**
```http
GET /prompts/statistics
Authorization: Bearer {jwt_token}
```

**Python Usage:**
```python
stats = storage.get_prompt_statistics(user_id=123)

print(f"Total prompts: {stats['total_prompts']}")
print(f"Most active date: {stats['most_active_date']}")
print(f"Average prompt length: {stats['average_prompt_length']:.1f} chars")
```

**Response:**
```json
{
  "total_prompts": 342,
  "first_prompt": "2025-12-01T08:00:00Z",
  "last_prompt": "2025-12-24T10:30:15Z",
  "prompts_by_date": {
    "2025-12-24": 15,
    "2025-12-23": 22,
    "2025-12-22": 18,
    ...
  },
  "prompts_by_session": {
    "sess_abc123": 45,
    "sess_def456": 38,
    ...
  },
  "average_prompt_length": 28.5,
  "most_active_date": "2025-12-23"
}
```

---

### 5. Delete Prompt History

**Purpose:** Remove prompts permanently (GDPR, privacy)

**API Endpoint:**
```http
POST /prompts/delete
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "start_date": "2025-12-01",
  "end_date": "2025-12-24",
  "session_id": null,
  "confirm": true
}
```

**Python Usage:**
```python
# Delete all prompt history
deleted = storage.delete_prompt_history(
    user_id=123,
    confirm=True
)
print(f"Deleted all prompts")

# Delete prompts from date range
deleted = storage.delete_prompt_history(
    user_id=123,
    start_date="2025-12-01",
    end_date="2025-12-10",
    confirm=True
)
print(f"Deleted {deleted} prompts from Dec 1-10")

# Delete prompts from specific session
deleted = storage.delete_prompt_history(
    user_id=123,
    session_id="sess_abc123",
    confirm=True
)
print(f"Deleted {deleted} prompts from session")
```

**Safety Features:**
- Requires `confirm=True` to proceed
- Supports filtered deletion (date range, session)
- Logging for audit trails

---

### 6. Export Prompt History

**Purpose:** Download prompts for backup or analysis

**API Endpoint:**
```http
GET /prompts/export?format=json
Authorization: Bearer {jwt_token}
```

**Python Usage:**
```python
# Export as JSON
storage.export_prompt_history(
    user_id=123,
    output_path="prompts-export.json",
    format="json"
)

# Export as JSONL (one prompt per line)
storage.export_prompt_history(
    user_id=123,
    output_path="prompts-export.jsonl",
    format="jsonl"
)

# Export as CSV
storage.export_prompt_history(
    user_id=123,
    output_path="prompts-export.csv",
    format="csv"
)

# Export as plain text
storage.export_prompt_history(
    user_id=123,
    output_path="prompts-export.txt",
    format="txt"
)
```

**Export Formats:**

**JSON:**
```json
[
  {"prompt_id": "...", "prompt": "...", "timestamp": "...", ...},
  ...
]
```

**JSONL:**
```
{"prompt_id": "...", "prompt": "...", "timestamp": "..."}
{"prompt_id": "...", "prompt": "...", "timestamp": "..."}
```

**CSV:**
```csv
prompt_id,user_id,session_id,prompt,timestamp,date
prompt_...,123,sess_...,Show me my tasks,2025-12-24T10:30:15Z,2025-12-24
```

**TXT:**
```
[2025-12-24T10:30:15Z] Show me my tasks

[2025-12-24T09:15:00Z] Add buy milk to my list

```

---

### 7. Get Recent Prompts

**Purpose:** Quick access to recent prompts for suggestions/autocomplete

**API Endpoint:**
```http
GET /prompts/recent?limit=10
Authorization: Bearer {jwt_token}
```

**Python Usage:**
```python
# Get last 10 prompts (text only)
recent = storage.get_prompt_history(user_id=123, limit=10)
prompt_texts = [p["prompt"] for p in recent]

print("Recent prompts:")
for prompt in prompt_texts:
    print(f"  - {prompt}")
```

**Response:**
```json
[
  "Show me my tasks",
  "Add high priority task to call client",
  "Mark the first task as done",
  "Delete old tasks",
  ...
]
```

---

## Integration Examples

### Example 1: Auto-save Prompts in Chat Endpoint

```python
from app.storage import FileBasedChatStorage

storage = FileBasedChatStorage()

@router.post("/chat")
async def chat_endpoint(chat_request: ChatRequest, user_id: int):
    # Save user prompt to history
    storage.save_prompt(
        user_id=user_id,
        prompt=chat_request.message,
        session_id=chat_request.session_id,
        metadata={
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
    )

    # Process message...
    response = await process_chat_message(...)

    # Add intent and metrics to saved prompt
    # (This is tracked in metadata for analytics)

    return response
```

### Example 2: Prompt Suggestions Feature

```typescript
// Frontend: Show recent prompts as suggestions
async function loadPromptSuggestions() {
  const response = await fetch('/prompts/recent?limit=5', {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  const recentPrompts = await response.json();

  // Display as clickable suggestions
  return recentPrompts.map(prompt => ({
    text: prompt,
    onClick: () => sendMessage(prompt)
  }));
}
```

### Example 3: Analytics Dashboard

```python
# Backend: Generate analytics for user
stats = storage.get_prompt_statistics(user_id=123)

# Frontend can display:
# - Total prompts sent
# - Most active days
# - Prompts per session
# - Average prompt length
# - Daily prompt chart
```

### Example 4: Search Previous Prompts

```typescript
// Frontend: Search bar for prompt history
async function searchPrompts(query: string) {
  const response = await fetch(
    `/prompts/search?query=${encodeURIComponent(query)}&limit=20`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );

  const results = await response.json();

  // Display results with timestamps
  // Allow user to re-send or view context
  return results;
}
```

---

## Best Practices

### 1. Always Save Prompts Automatically
```python
# Good: Automatic saving in chat endpoint
storage.save_prompt(user_id, prompt, session_id)

# Bad: Manual/optional saving
# Users expect complete history
```

### 2. Include Metadata for Analytics
```python
# Good: Rich metadata
storage.save_prompt(
    user_id=123,
    prompt="Show tasks",
    metadata={
        "intent": "LIST_TODOS",
        "tokens": 5,
        "response_time_ms": 750,
        "tool_calls": ["list_todos"],
        "success": True
    }
)

# Okay: Minimal metadata
storage.save_prompt(user_id=123, prompt="Show tasks")
```

### 3. Respect Privacy
```python
# Provide easy deletion
deleted = storage.delete_prompt_history(
    user_id=123,
    confirm=True
)

# Export for GDPR requests
storage.export_prompt_history(
    user_id=123,
    output_path=f"user_{user_id}_prompts.json",
    format="json"
)
```

### 4. Use Pagination
```python
# Good: Paginated requests
prompts = storage.get_prompt_history(
    user_id=123,
    limit=100,
    offset=0  # Next page: offset=100
)

# Bad: Loading everything
prompts = storage.get_prompt_history(user_id=123, limit=100000)
```

### 5. Efficient File Structure
```
# Good: Monthly directories keep file counts manageable
prompt-history/
├── 2025-12/  # ~30 files
├── 2025-11/  # ~30 files
└── 2025-10/  # ~30 files

# Bad: All in one directory
prompt-history/
├── prompts-2025-12-24.jsonl
├── prompts-2025-12-23.jsonl
...  # 365+ files in one dir
```

---

## Performance Considerations

### File Size Management

**Daily JSONL files:**
- Average prompt: ~200 bytes
- 100 prompts/day: ~20 KB
- 1000 prompts/day: ~200 KB
- Very manageable file sizes

**Monthly directories:**
- Keeps directory listing fast
- Easy to archive old months
- ~900 KB per month (100 prompts/day)

### Search Performance

**Simple text search:**
- O(n) through all prompts
- Fast enough for <10,000 prompts
- Consider indexing for >100,000 prompts

**Optimization options:**
```python
# Future: Build search index
# Use tools like Whoosh, SQLite FTS, or Elasticsearch
```

### Cleanup Strategy

```python
# Archive old prompt history (e.g., >1 year)
import shutil
from pathlib import Path

def archive_old_prompts(user_id: int, months_to_keep: int = 12):
    """Move old prompt history to archive"""
    prompt_history_path = Path(f"data/chat-history/users/{user_id}/prompt-history")
    archive_path = Path(f"data/archives/users/{user_id}/prompt-history")

    # Move directories older than N months
    # ...
```

---

## Troubleshooting

### Issue: Prompts not saving

**Check:**
1. Directory permissions
2. Disk space
3. Logs for errors

```python
# Test prompt saving
try:
    result = storage.save_prompt(user_id=123, prompt="Test")
    print(f"✓ Saved: {result['prompt_id']}")
except Exception as e:
    print(f"✗ Error: {e}")
```

### Issue: Search returns no results

**Check:**
1. Query syntax (case-insensitive, partial match)
2. Date filters
3. File permissions

```python
# Debug search
all_prompts = storage.get_prompt_history(user_id=123, limit=1000)
print(f"Total prompts: {len(all_prompts)}")

results = storage.search_prompts(user_id=123, query="test")
print(f"Matching 'test': {len(results)}")
```

### Issue: Export fails

**Check:**
1. Output path writable
2. Sufficient disk space
3. Format parameter valid

```python
# Test export
try:
    success = storage.export_prompt_history(
        user_id=123,
        output_path="test-export.json",
        format="json"
    )
    print(f"✓ Export {'succeeded' if success else 'failed'}")
except Exception as e:
    print(f"✗ Error: {e}")
```

---

## API Reference Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/prompts/history` | GET | Get prompt history with filters |
| `/prompts/search` | GET | Search prompts by text |
| `/prompts/statistics` | GET | Get prompt statistics |
| `/prompts/delete` | POST | Delete prompts (requires confirmation) |
| `/prompts/export` | GET | Export prompts to file |
| `/prompts/recent` | GET | Get recent prompts (text only) |

---

## Summary

The prompt history system provides:

✅ **Automatic Tracking** - All user prompts saved automatically
✅ **Efficient Storage** - JSONL format, organized by month/day
✅ **Powerful Search** - Text search with filtering
✅ **Rich Analytics** - Statistics and usage patterns
✅ **Privacy Controls** - Easy deletion and export
✅ **Multiple Formats** - JSON, JSONL, CSV, TXT export
✅ **Performance** - Fast append-only operations

**File Structure:**
```
users/{user_id}/prompt-history/
├── 2025-12/
│   ├── prompts-2025-12-24.jsonl  # Daily logs
│   └── ...
└── prompt-index.json             # Fast lookups
```

---

**Last Updated:** 2025-12-24
