# File-Based Mono Structure for Chat History Storage

## Overview

This specification defines a **file-based mono structure** approach for storing chat history and prompts locally in Phase 3, as an alternative to database storage. This approach uses a hierarchical folder structure to organize conversations by user and session.

**Status:** Design Specification
**Created:** 2025-12-24

---

## Architecture Overview

### Storage Location

```
phase3-chatbot/
└── data/
    └── chat-history/
        └── users/
            └── {user_id}/
                └── sessions/
                    └── {session_id}/
                        ├── metadata.json
                        ├── conversation.md
                        └── messages/
                            ├── 001_user_2025-12-24T10-30-00.json
                            ├── 002_assistant_2025-12-24T10-30-15.json
                            ├── 003_user_2025-12-24T10-31-00.json
                            └── ...
```

### Key Design Principles

1. **User Isolation** - Each user has their own folder (`users/{user_id}/`)
2. **Session Organization** - Sessions are organized by unique session IDs
3. **Readable Format** - Conversations stored in Markdown for human readability
4. **Structured Data** - Individual messages in JSON for programmatic access
5. **Metadata Tracking** - Session metadata stored separately
6. **Timestamp Ordering** - Messages numbered and timestamped

---

## Folder Structure Details

### Root Directory

```
data/
└── chat-history/
    ├── .gitignore          # Exclude from version control
    ├── README.md           # Documentation
    └── users/              # User data directory
```

### User Directory

```
users/{user_id}/
├── user-metadata.json      # User preferences, statistics
├── prompt-history/         # All user prompts (separate from conversations)
│   ├── 2025-12/
│   │   ├── prompts-2025-12-24.jsonl
│   │   └── prompts-2025-12-23.jsonl
│   └── prompt-index.json   # Searchable index
└── sessions/               # All conversation sessions
```

**user-metadata.json Format:**
```json
{
  "user_id": 123,
  "total_sessions": 15,
  "total_messages": 342,
  "first_session": "2025-12-01T10:00:00Z",
  "last_activity": "2025-12-24T10:30:00Z",
  "preferences": {
    "save_format": "markdown",
    "retention_days": 90
  }
}
```

### Session Directory

```
sessions/{session_id}/
├── metadata.json           # Session metadata
├── conversation.md         # Human-readable conversation
├── conversation.json       # Structured conversation data
└── messages/               # Individual message files
    └── {seq}_{role}_{timestamp}.json
```

**Session ID Format:** `sess_{timestamp}_{random}`
**Example:** `sess_1703433600_a7f3k9x2`

---

## File Formats

### 1. Session Metadata (`metadata.json`)

```json
{
  "session_id": "sess_1703433600_a7f3k9x2",
  "user_id": 123,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T10:35:00Z",
  "message_count": 8,
  "status": "active",
  "summary": "Task management: Created 3 todos, completed 1",
  "topics": ["todo creation", "task completion", "priority settings"],
  "tool_calls": {
    "create_todo": 3,
    "update_todo": 1,
    "list_todos": 2
  },
  "statistics": {
    "total_tokens": 1250,
    "avg_response_time_ms": 850
  }
}
```

### 2. Conversation Markdown (`conversation.md`)

**Purpose:** Human-readable conversation history

**Format:**
```markdown
# Conversation: sess_1703433600_a7f3k9x2

**User:** user@example.com (ID: 123)
**Started:** December 24, 2025 at 10:00 AM
**Last Updated:** December 24, 2025 at 10:35 AM
**Messages:** 8

---

## Message 1 - User
**Timestamp:** 2025-12-24T10:00:15Z

Show me my tasks

---

## Message 2 - Assistant
**Timestamp:** 2025-12-24T10:00:18Z

You have 3 pending tasks:

1. Buy groceries (High priority, due tomorrow)
2. Call dentist (Medium priority, due Dec 26)
3. Finish report (Low priority, due next week)

---

## Message 3 - User
**Timestamp:** 2025-12-24T10:01:30Z

Add high priority task to review code

---

## Message 4 - Assistant
**Timestamp:** 2025-12-24T10:01:35Z

I've created a new high priority todo: "Review code"

Your pending tasks are now: 4

---

<!-- Additional messages... -->
```

### 3. Conversation JSON (`conversation.json`)

**Purpose:** Complete structured conversation for programmatic access

**Format:**
```json
{
  "session_id": "sess_1703433600_a7f3k9x2",
  "user_id": 123,
  "created_at": "2025-12-24T10:00:00Z",
  "updated_at": "2025-12-24T10:35:00Z",
  "messages": [
    {
      "sequence": 1,
      "role": "user",
      "content": "Show me my tasks",
      "timestamp": "2025-12-24T10:00:15Z",
      "metadata": {
        "client_ip": "192.168.1.1",
        "user_agent": "Chrome/120.0"
      }
    },
    {
      "sequence": 2,
      "role": "assistant",
      "content": "You have 3 pending tasks:\n\n1. Buy groceries...",
      "timestamp": "2025-12-24T10:00:18Z",
      "metadata": {
        "tool_calls": [
          {
            "tool": "list_todos",
            "parameters": {"user_id": 123, "status": "pending"},
            "result": {"success": true, "count": 3}
          }
        ],
        "tokens_used": 125,
        "response_time_ms": 850,
        "model": "gpt-4-turbo"
      }
    }
  ]
}
```

### 4. Individual Message Files (`messages/{seq}_{role}_{timestamp}.json`)

**Purpose:** Individual message storage for incremental updates

**Naming Convention:** `{sequence}_{role}_{timestamp}.json`
**Example:** `001_user_2025-12-24T10-00-15.json`

**Format:**
```json
{
  "sequence": 1,
  "session_id": "sess_1703433600_a7f3k9x2",
  "user_id": 123,
  "role": "user",
  "content": "Show me my tasks",
  "timestamp": "2025-12-24T10:00:15Z",
  "metadata": {
    "client_ip": "192.168.1.1",
    "user_agent": "Chrome/120.0",
    "device": "desktop"
  }
}
```

---

## File Operations API

### Core Operations Module

**File:** `app/storage/file_storage.py`

```python
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import json
import os

class FileBasedChatStorage:
    """
    File-based storage for chat history using mono structure
    """

    def __init__(self, base_path: str = "data/chat-history"):
        self.base_path = Path(base_path)
        self._ensure_base_structure()

    def _ensure_base_structure(self):
        """Create base directory structure if it doesn't exist"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "users").mkdir(exist_ok=True)

    # Session Management
    def create_session(self, user_id: int, session_id: str) -> Path:
        """Create new session directory structure"""
        session_path = self._get_session_path(user_id, session_id)
        session_path.mkdir(parents=True, exist_ok=True)
        (session_path / "messages").mkdir(exist_ok=True)

        # Initialize metadata
        metadata = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "message_count": 0,
            "status": "active"
        }
        self._write_json(session_path / "metadata.json", metadata)

        return session_path

    # Message Operations
    def save_message(
        self,
        user_id: int,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Save a new message to the session"""
        session_path = self._get_session_path(user_id, session_id)

        # Ensure session exists
        if not session_path.exists():
            self.create_session(user_id, session_id)

        # Get next sequence number
        sequence = self._get_next_sequence(session_path)
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Create message object
        message = {
            "sequence": sequence,
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }

        # Save individual message file
        msg_filename = f"{sequence:03d}_{role}_{timestamp.replace(':', '-')}.json"
        msg_path = session_path / "messages" / msg_filename
        self._write_json(msg_path, message)

        # Append to conversation.json
        self._append_to_conversation_json(session_path, message)

        # Append to conversation.md
        self._append_to_conversation_md(session_path, message)

        # Update session metadata
        self._update_session_metadata(session_path)

        return message

    def load_chat_history(
        self,
        user_id: int,
        session_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """Load recent chat history for a session"""
        session_path = self._get_session_path(user_id, session_id)

        if not session_path.exists():
            return []

        # Load from conversation.json
        conv_file = session_path / "conversation.json"
        if not conv_file.exists():
            return []

        conversation = self._read_json(conv_file)
        messages = conversation.get("messages", [])

        # Return last N messages
        return messages[-limit:] if len(messages) > limit else messages

    def get_user_sessions(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """Get all sessions for a user"""
        user_path = self._get_user_path(user_id)
        sessions_path = user_path / "sessions"

        if not sessions_path.exists():
            return []

        sessions = []
        for session_dir in sessions_path.iterdir():
            if session_dir.is_dir():
                metadata_file = session_dir / "metadata.json"
                if metadata_file.exists():
                    metadata = self._read_json(metadata_file)
                    sessions.append(metadata)

        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        return sessions[:limit]

    def delete_session(self, user_id: int, session_id: str) -> bool:
        """Delete a session (move to archive or delete permanently)"""
        session_path = self._get_session_path(user_id, session_id)

        if not session_path.exists():
            return False

        # Update metadata to mark as deleted
        metadata_file = session_path / "metadata.json"
        metadata = self._read_json(metadata_file)
        metadata["status"] = "deleted"
        metadata["deleted_at"] = datetime.utcnow().isoformat() + "Z"
        self._write_json(metadata_file, metadata)

        return True

    # Helper Methods
    def _get_user_path(self, user_id: int) -> Path:
        """Get path to user directory"""
        return self.base_path / "users" / str(user_id)

    def _get_session_path(self, user_id: int, session_id: str) -> Path:
        """Get path to session directory"""
        return self._get_user_path(user_id) / "sessions" / session_id

    def _get_next_sequence(self, session_path: Path) -> int:
        """Get next message sequence number"""
        messages_path = session_path / "messages"
        if not messages_path.exists():
            return 1

        message_files = list(messages_path.glob("*.json"))
        if not message_files:
            return 1

        # Extract sequence numbers from filenames
        sequences = []
        for f in message_files:
            try:
                seq = int(f.name.split("_")[0])
                sequences.append(seq)
            except (ValueError, IndexError):
                continue

        return max(sequences) + 1 if sequences else 1

    def _append_to_conversation_json(self, session_path: Path, message: Dict):
        """Append message to conversation.json"""
        conv_file = session_path / "conversation.json"

        if conv_file.exists():
            conversation = self._read_json(conv_file)
        else:
            conversation = {
                "session_id": message["session_id"],
                "user_id": message["user_id"],
                "created_at": message["timestamp"],
                "updated_at": message["timestamp"],
                "messages": []
            }

        conversation["messages"].append(message)
        conversation["updated_at"] = message["timestamp"]

        self._write_json(conv_file, conversation)

    def _append_to_conversation_md(self, session_path: Path, message: Dict):
        """Append message to conversation.md"""
        md_file = session_path / "conversation.md"

        if not md_file.exists():
            # Create header
            header = f"""# Conversation: {message['session_id']}

**User ID:** {message['user_id']}
**Started:** {message['timestamp']}

---

"""
            md_file.write_text(header, encoding="utf-8")

        # Format message
        role = message["role"].capitalize()
        content = message["content"]
        timestamp = message["timestamp"]
        sequence = message["sequence"]

        message_md = f"""## Message {sequence} - {role}
**Timestamp:** {timestamp}

{content}

---

"""

        # Append to file
        with md_file.open("a", encoding="utf-8") as f:
            f.write(message_md)

    def _update_session_metadata(self, session_path: Path):
        """Update session metadata after adding message"""
        metadata_file = session_path / "metadata.json"
        metadata = self._read_json(metadata_file)

        # Count messages
        messages_path = session_path / "messages"
        message_count = len(list(messages_path.glob("*.json")))

        metadata["message_count"] = message_count
        metadata["updated_at"] = datetime.utcnow().isoformat() + "Z"

        self._write_json(metadata_file, metadata)

    def _read_json(self, file_path: Path) -> Dict:
        """Read JSON file"""
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, file_path: Path, data: Dict):
        """Write JSON file"""
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
```

---

## Integration with Phase 3

### Update Chat Endpoint

**File:** `app/routes/chat.py`

```python
from app.storage.file_storage import FileBasedChatStorage

# Initialize storage
file_storage = FileBasedChatStorage(base_path="data/chat-history")

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # Validate JWT
    user_id = await verify_jwt_token(credentials)

    # Load history from files
    history = file_storage.load_chat_history(
        user_id=user_id,
        session_id=chat_request.session_id,
        limit=20
    )

    formatted_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history
    ]

    # Save user message
    file_storage.save_message(
        user_id=user_id,
        session_id=chat_request.session_id,
        role="user",
        content=chat_request.message,
        metadata={
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        }
    )

    # Process with agent
    agent_response = await process_chat_message(
        user_id=user_id,
        session_id=chat_request.session_id,
        message=chat_request.message,
        history=formatted_history
    )

    # Save assistant response
    file_storage.save_message(
        user_id=user_id,
        session_id=chat_request.session_id,
        role="assistant",
        content=agent_response["content"],
        metadata=agent_response.get("metadata", {})
    )

    return ChatResponse(
        response=agent_response["content"],
        session_id=chat_request.session_id,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
```

---

## Advantages of File-Based Mono Structure

### 1. Human Readability
- **Markdown format** allows easy reading of conversations
- **JSON format** preserves structure for programmatic access
- Can be opened in any text editor or IDE

### 2. Version Control Friendly
- Each session is a separate directory
- Messages can be tracked in Git (if desired)
- Easy to diff changes between versions

### 3. Portability
- No database required
- Easy to backup (just copy folders)
- Easy to migrate between systems
- Can be synced via cloud storage

### 4. Debugging
- Easy to inspect conversation flow
- Clear file structure for troubleshooting
- Can manually edit or replay conversations

### 5. Privacy
- Data stored locally
- Easy to delete specific sessions
- User controls their own data

### 6. Scalability
- File system handles millions of files efficiently
- Can implement sharding by user ID ranges
- Easy to archive old sessions

---

## Disadvantages and Mitigations

### 1. Concurrent Access
**Problem:** Multiple processes writing to same file
**Mitigation:** Use file locking mechanisms

```python
import fcntl

def _write_json_safe(self, file_path: Path, data: Dict):
    """Write JSON with file locking"""
    with file_path.open("w", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, indent=2, ensure_ascii=False)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### 2. Search Performance
**Problem:** Searching across many files is slow
**Mitigation:** Build an index file or use full-text search tools

```python
def build_search_index(self, user_id: int):
    """Build search index for user's conversations"""
    # Implementation using whoosh or similar
    pass
```

### 3. Backup Complexity
**Problem:** Need to backup many small files
**Mitigation:** Periodic archiving to compressed formats

```python
def archive_old_sessions(self, user_id: int, days: int = 90):
    """Archive sessions older than N days to .tar.gz"""
    pass
```

### 4. File System Limits
**Problem:** Too many files in one directory
**Mitigation:** Shard by date or session ID prefix

```
users/{user_id}/sessions/
├── 2025-12/
│   └── sess_1703433600_a7f3k9x2/
└── 2025-11/
    └── sess_1701000000_b8g4m1y3/
```

---

## Migration Path

### From Database to File-Based

```python
async def migrate_db_to_files(db_session: AsyncSession):
    """Migrate existing database chat history to files"""
    storage = FileBasedChatStorage()

    # Get all users
    users = await db_session.execute(
        select(ChatHistory.user_id).distinct()
    )

    for (user_id,) in users:
        # Get all sessions for user
        sessions = await db_session.execute(
            select(ChatHistory.session_id)
            .where(ChatHistory.user_id == user_id)
            .distinct()
        )

        for (session_id,) in sessions:
            # Get all messages for session
            messages = await db_session.execute(
                select(ChatHistory)
                .where(
                    ChatHistory.user_id == user_id,
                    ChatHistory.session_id == session_id
                )
                .order_by(ChatHistory.timestamp)
            )

            # Save to files
            for msg in messages.scalars():
                storage.save_message(
                    user_id=msg.user_id,
                    session_id=msg.session_id,
                    role=msg.role,
                    content=msg.content,
                    metadata=msg.metadata
                )
```

---

## Configuration

### Environment Variables

```bash
# Storage configuration
CHAT_STORAGE_TYPE=file  # or "database"
CHAT_STORAGE_PATH=data/chat-history
CHAT_RETENTION_DAYS=90
CHAT_MAX_SESSIONS_PER_USER=100
```

### Application Config

**File:** `app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    chat_storage_type: str = "file"  # "file" or "database"
    chat_storage_path: str = "data/chat-history"
    chat_retention_days: int = 90
    chat_max_sessions_per_user: int = 100

    class Config:
        env_file = ".env"
```

---

## Testing Strategy

### Unit Tests

```python
def test_create_session():
    storage = FileBasedChatStorage(base_path="test-data")
    session_path = storage.create_session(123, "sess_test_001")

    assert session_path.exists()
    assert (session_path / "metadata.json").exists()
    assert (session_path / "messages").exists()

def test_save_message():
    storage = FileBasedChatStorage(base_path="test-data")
    message = storage.save_message(
        user_id=123,
        session_id="sess_test_001",
        role="user",
        content="Hello"
    )

    assert message["sequence"] == 1
    assert message["role"] == "user"
    assert message["content"] == "Hello"

def test_load_history():
    storage = FileBasedChatStorage(base_path="test-data")

    # Save multiple messages
    for i in range(5):
        storage.save_message(
            user_id=123,
            session_id="sess_test_001",
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}"
        )

    # Load history
    history = storage.load_chat_history(123, "sess_test_001", limit=3)
    assert len(history) == 3
    assert history[-1]["content"] == "Message 4"
```

---

## Implementation Checklist

- [ ] Create `app/storage/file_storage.py` module
- [ ] Implement `FileBasedChatStorage` class
- [ ] Add file locking for concurrent access
- [ ] Update chat endpoint to use file storage
- [ ] Create `.gitignore` for data directory
- [ ] Add configuration for storage type selection
- [ ] Implement migration script from database
- [ ] Write unit tests for file operations
- [ ] Write integration tests
- [ ] Add backup/archive utilities
- [ ] Document usage in README

---

## Maintenance Operations

### Cleanup Old Sessions

```python
def cleanup_old_sessions(self, days: int = 90):
    """Delete sessions marked as deleted and older than N days"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    users_path = self.base_path / "users"
    for user_dir in users_path.iterdir():
        if not user_dir.is_dir():
            continue

        sessions_path = user_dir / "sessions"
        if not sessions_path.exists():
            continue

        for session_dir in sessions_path.iterdir():
            metadata_file = session_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            metadata = self._read_json(metadata_file)
            if metadata.get("status") == "deleted":
                deleted_at = datetime.fromisoformat(
                    metadata.get("deleted_at", "").replace("Z", "")
                )
                if deleted_at < cutoff:
                    # Permanently delete
                    shutil.rmtree(session_dir)
```

### Export User Data (GDPR)

```python
def export_user_data(self, user_id: int, output_path: str):
    """Export all user data for GDPR compliance"""
    user_path = self._get_user_path(user_id)

    # Create zip archive
    import zipfile
    with zipfile.ZipFile(output_path, "w") as zipf:
        for root, dirs, files in os.walk(user_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(user_path)
                zipf.write(file_path, arcname)
```

---

## Summary

This file-based mono structure provides:

✅ **Human-readable** conversation logs in Markdown
✅ **Structured data** in JSON for programmatic access
✅ **User isolation** with clear folder hierarchy
✅ **Session organization** for easy navigation
✅ **No database required** - pure file system
✅ **Easy backup and migration**
✅ **Version control friendly**
✅ **Privacy-focused** local storage

**Next Steps:**
1. Implement the `FileBasedChatStorage` class
2. Update chat endpoint to use file storage
3. Add configuration toggle between file and database storage
4. Write comprehensive tests
5. Document usage and best practices

---

**Status:** Ready for Implementation
**Last Updated:** 2025-12-24
