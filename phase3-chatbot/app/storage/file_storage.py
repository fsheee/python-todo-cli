"""
File-based chat history storage using mono structure.

Spec Reference: specs/storage/file-based-mono-structure.md
"""

from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json
import shutil
import logging

logger = logging.getLogger(__name__)


class FileBasedChatStorage:
    """
    File-based storage for chat history using mono structure.

    Storage hierarchy:
    data/chat-history/users/{user_id}/sessions/{session_id}/
        ├── metadata.json
        ├── conversation.md
        ├── conversation.json
        └── messages/{seq}_{role}_{timestamp}.json
    """

    def __init__(self, base_path: str = "data/chat-history"):
        """
        Initialize file-based chat storage.

        Args:
            base_path: Root directory for chat history storage
        """
        self.base_path = Path(base_path)
        self._ensure_base_structure()
        logger.info(f"Initialized FileBasedChatStorage at {self.base_path}")

    def _ensure_base_structure(self):
        """Create base directory structure if it doesn't exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "users").mkdir(exist_ok=True)

        # Create .gitignore if it doesn't exist
        gitignore_path = self.base_path / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("# Ignore all user data\nusers/\n*.json\n*.md\n*.jsonl\n")

    def _ensure_prompt_history_structure(self, user_id: int):
        """Create prompt history directory structure for a user."""
        user_path = self._get_user_path(user_id)
        prompt_history_path = user_path / "prompt-history"
        prompt_history_path.mkdir(parents=True, exist_ok=True)

    # Session Management
    def create_session(self, user_id: int, session_id: str) -> Path:
        """
        Create new session directory structure.

        Args:
            user_id: ID of the user
            session_id: Unique session identifier

        Returns:
            Path to created session directory
        """
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
            "status": "active",
            "summary": "",
            "topics": [],
            "tool_calls": {},
            "statistics": {
                "total_tokens": 0,
                "avg_response_time_ms": 0
            }
        }
        self._write_json(session_path / "metadata.json", metadata)

        logger.info(f"Created session {session_id} for user {user_id}")
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
        """
        Save a new message to the session.

        Args:
            user_id: ID of the user
            session_id: Session identifier
            role: Message role ('user', 'assistant', or 'system')
            content: Message content
            metadata: Optional metadata dictionary

        Returns:
            Created message object with sequence number and timestamp
        """
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
        msg_filename = f"{sequence:03d}_{role}_{timestamp.replace(':', '-').replace('.', '-')}.json"
        msg_path = session_path / "messages" / msg_filename
        self._write_json(msg_path, message)

        # Append to conversation.json
        self._append_to_conversation_json(session_path, message)

        # Append to conversation.md
        self._append_to_conversation_md(session_path, message)

        # Update session metadata
        self._update_session_metadata(session_path, message)

        logger.debug(f"Saved message {sequence} to session {session_id}")
        return message

    def load_chat_history(
        self,
        user_id: int,
        session_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Load recent chat history for a session.

        Args:
            user_id: ID of the user
            session_id: Session identifier
            limit: Maximum number of messages to load (default: 20)

        Returns:
            List of message objects in chronological order
        """
        session_path = self._get_session_path(user_id, session_id)

        if not session_path.exists():
            logger.debug(f"Session {session_id} not found for user {user_id}")
            return []

        # Load from conversation.json
        conv_file = session_path / "conversation.json"
        if not conv_file.exists():
            logger.debug(f"No conversation.json found for session {session_id}")
            return []

        conversation = self._read_json(conv_file)
        messages = conversation.get("messages", [])

        # Return last N messages
        result = messages[-limit:] if len(messages) > limit else messages
        logger.debug(f"Loaded {len(result)} messages from session {session_id}")
        return result

    def get_user_sessions(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get all sessions for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return (default: 50)

        Returns:
            List of session metadata objects sorted by last update
        """
        user_path = self._get_user_path(user_id)
        sessions_path = user_path / "sessions"

        if not sessions_path.exists():
            logger.debug(f"No sessions found for user {user_id}")
            return []

        sessions = []
        for session_dir in sessions_path.iterdir():
            if session_dir.is_dir():
                metadata_file = session_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = self._read_json(metadata_file)
                        # Only include active sessions by default
                        if metadata.get("status") != "deleted":
                            sessions.append(metadata)
                    except Exception as e:
                        logger.error(f"Error reading session metadata: {e}")
                        continue

        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        result = sessions[:limit]
        logger.debug(f"Found {len(result)} sessions for user {user_id}")
        return result

    def delete_session(self, user_id: int, session_id: str) -> bool:
        """
        Soft delete a session by marking it as deleted.

        Args:
            user_id: ID of the user
            session_id: Session identifier

        Returns:
            True if session was marked as deleted, False if not found
        """
        session_path = self._get_session_path(user_id, session_id)

        if not session_path.exists():
            logger.warning(f"Session {session_id} not found for deletion")
            return False

        # Update metadata to mark as deleted
        metadata_file = session_path / "metadata.json"
        metadata = self._read_json(metadata_file)
        metadata["status"] = "deleted"
        metadata["deleted_at"] = datetime.utcnow().isoformat() + "Z"
        self._write_json(metadata_file, metadata)

        logger.info(f"Soft deleted session {session_id} for user {user_id}")
        return True

    def delete_session_permanent(self, user_id: int, session_id: str) -> bool:
        """
        Permanently delete a session (hard delete).

        Args:
            user_id: ID of the user
            session_id: Session identifier

        Returns:
            True if session was permanently deleted, False if not found
        """
        session_path = self._get_session_path(user_id, session_id)

        if not session_path.exists():
            logger.warning(f"Session {session_id} not found for permanent deletion")
            return False

        try:
            shutil.rmtree(session_path)
            logger.info(f"Permanently deleted session {session_id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error permanently deleting session {session_id}: {e}")
            return False

    def delete_multiple_sessions(
        self,
        user_id: int,
        session_ids: List[str],
        permanent: bool = False
    ) -> Dict[str, bool]:
        """
        Delete multiple sessions at once.

        Args:
            user_id: ID of the user
            session_ids: List of session identifiers
            permanent: If True, permanently delete; if False, soft delete

        Returns:
            Dictionary mapping session_id to deletion success status
        """
        results = {}
        for session_id in session_ids:
            if permanent:
                results[session_id] = self.delete_session_permanent(user_id, session_id)
            else:
                results[session_id] = self.delete_session(user_id, session_id)

        successful = sum(1 for success in results.values() if success)
        logger.info(
            f"Deleted {successful}/{len(session_ids)} sessions for user {user_id} "
            f"({'permanent' if permanent else 'soft'})"
        )
        return results

    def delete_all_user_sessions(
        self,
        user_id: int,
        permanent: bool = False,
        confirm: bool = False
    ) -> int:
        """
        Delete all sessions for a user.

        Args:
            user_id: ID of the user
            permanent: If True, permanently delete; if False, soft delete
            confirm: Must be True to proceed (safety check)

        Returns:
            Number of sessions deleted
        """
        if not confirm:
            raise ValueError("Must confirm deletion of all sessions with confirm=True")

        sessions = self.get_user_sessions(user_id, limit=10000)
        session_ids = [s["session_id"] for s in sessions]

        results = self.delete_multiple_sessions(user_id, session_ids, permanent)
        deleted_count = sum(1 for success in results.values() if success)

        logger.warning(
            f"Deleted ALL {deleted_count} sessions for user {user_id} "
            f"({'permanent' if permanent else 'soft'})"
        )
        return deleted_count

    def delete_messages_in_session(
        self,
        user_id: int,
        session_id: str,
        message_sequences: List[int]
    ) -> int:
        """
        Delete specific messages from a session.

        Args:
            user_id: ID of the user
            session_id: Session identifier
            message_sequences: List of message sequence numbers to delete

        Returns:
            Number of messages deleted
        """
        session_path = self._get_session_path(user_id, session_id)
        if not session_path.exists():
            logger.warning(f"Session {session_id} not found")
            return 0

        deleted_count = 0
        messages_path = session_path / "messages"

        # Delete individual message files
        for msg_file in messages_path.glob("*.json"):
            try:
                seq = int(msg_file.name.split("_")[0])
                if seq in message_sequences:
                    msg_file.unlink()
                    deleted_count += 1
            except (ValueError, IndexError):
                continue

        # Rebuild conversation.json and conversation.md
        if deleted_count > 0:
            self._rebuild_conversation_files(session_path)
            logger.info(
                f"Deleted {deleted_count} messages from session {session_id}"
            )

        return deleted_count

    def restore_session(self, user_id: int, session_id: str) -> bool:
        """
        Restore a soft-deleted session.

        Args:
            user_id: ID of the user
            session_id: Session identifier

        Returns:
            True if session was restored, False if not found or not deleted
        """
        session_path = self._get_session_path(user_id, session_id)

        if not session_path.exists():
            logger.warning(f"Session {session_id} not found for restoration")
            return False

        metadata_file = session_path / "metadata.json"
        metadata = self._read_json(metadata_file)

        if metadata.get("status") != "deleted":
            logger.info(f"Session {session_id} is not deleted, cannot restore")
            return False

        # Restore session
        metadata["status"] = "active"
        if "deleted_at" in metadata:
            del metadata["deleted_at"]
        metadata["restored_at"] = datetime.utcnow().isoformat() + "Z"
        self._write_json(metadata_file, metadata)

        logger.info(f"Restored session {session_id} for user {user_id}")
        return True

    def cleanup_old_sessions(self, days: int = 90) -> int:
        """
        Permanently delete sessions marked as deleted and older than N days.

        Args:
            days: Number of days to keep deleted sessions (default: 90)

        Returns:
            Number of sessions permanently deleted
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0

        users_path = self.base_path / "users"
        if not users_path.exists():
            return 0

        for user_dir in users_path.iterdir():
            if not user_dir.is_dir():
                continue

            sessions_path = user_dir / "sessions"
            if not sessions_path.exists():
                continue

            for session_dir in sessions_path.iterdir():
                if not session_dir.is_dir():
                    continue

                metadata_file = session_dir / "metadata.json"
                if not metadata_file.exists():
                    continue

                try:
                    metadata = self._read_json(metadata_file)
                    if metadata.get("status") == "deleted":
                        deleted_at_str = metadata.get("deleted_at", "")
                        if deleted_at_str:
                            deleted_at = datetime.fromisoformat(
                                deleted_at_str.replace("Z", "+00:00")
                            )
                            if deleted_at < cutoff:
                                # Permanently delete
                                shutil.rmtree(session_dir)
                                deleted_count += 1
                                logger.info(f"Permanently deleted session {session_dir.name}")
                except Exception as e:
                    logger.error(f"Error during cleanup of {session_dir}: {e}")
                    continue

        logger.info(f"Cleanup completed: {deleted_count} sessions permanently deleted")
        return deleted_count

    def get_deleted_sessions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Get all soft-deleted sessions for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return

        Returns:
            List of deleted session metadata objects
        """
        user_path = self._get_user_path(user_id)
        sessions_path = user_path / "sessions"

        if not sessions_path.exists():
            return []

        deleted_sessions = []
        for session_dir in sessions_path.iterdir():
            if session_dir.is_dir():
                metadata_file = session_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = self._read_json(metadata_file)
                        if metadata.get("status") == "deleted":
                            deleted_sessions.append(metadata)
                    except Exception as e:
                        logger.error(f"Error reading session metadata: {e}")
                        continue

        # Sort by deleted_at descending
        deleted_sessions.sort(
            key=lambda x: x.get("deleted_at", ""),
            reverse=True
        )

        return deleted_sessions[:limit]

    def export_user_data(self, user_id: int, output_path: str) -> bool:
        """
        Export all user data to a zip file for GDPR compliance.

        Args:
            user_id: ID of the user
            output_path: Path to output zip file

        Returns:
            True if export succeeded, False otherwise
        """
        import zipfile

        user_path = self._get_user_path(user_id)
        if not user_path.exists():
            logger.warning(f"No data found for user {user_id}")
            return False

        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in user_path.walk():
                    for file in files:
                        file_path = root / file
                        arcname = file_path.relative_to(user_path)
                        zipf.write(file_path, arcname)

            logger.info(f"Exported user {user_id} data to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return False

    # Helper Methods
    def _get_user_path(self, user_id: int) -> Path:
        """Get path to user directory."""
        return self.base_path / "users" / str(user_id)

    def _get_session_path(self, user_id: int, session_id: str) -> Path:
        """Get path to session directory."""
        return self._get_user_path(user_id) / "sessions" / session_id

    def _get_next_sequence(self, session_path: Path) -> int:
        """Get next message sequence number for a session."""
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
        """Append message to conversation.json file."""
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
        """Append message to conversation.md file."""
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

    def _update_session_metadata(self, session_path: Path, message: Dict):
        """Update session metadata after adding a message."""
        metadata_file = session_path / "metadata.json"
        metadata = self._read_json(metadata_file)

        # Count messages
        messages_path = session_path / "messages"
        message_count = len(list(messages_path.glob("*.json")))

        metadata["message_count"] = message_count
        metadata["updated_at"] = message["timestamp"]

        # Track tool calls if present
        if "tool_calls" in message.get("metadata", {}):
            for tool_call in message["metadata"]["tool_calls"]:
                tool_name = tool_call.get("tool", "")
                if tool_name:
                    metadata["tool_calls"][tool_name] = \
                        metadata["tool_calls"].get(tool_name, 0) + 1

        # Update statistics
        msg_metadata = message.get("metadata", {})
        if "tokens_used" in msg_metadata:
            metadata["statistics"]["total_tokens"] += msg_metadata["tokens_used"]

        self._write_json(metadata_file, metadata)

    def _read_json(self, file_path: Path) -> Dict:
        """Read JSON file safely."""
        try:
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return {}

    def _write_json(self, file_path: Path, data: Dict):
        """Write JSON file with pretty formatting."""
        try:
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
            raise

    def _rebuild_conversation_files(self, session_path: Path):
        """Rebuild conversation.json and conversation.md from remaining message files."""
        messages_path = session_path / "messages"
        if not messages_path.exists():
            return

        # Load all remaining messages
        messages = []
        for msg_file in sorted(messages_path.glob("*.json")):
            try:
                message = self._read_json(msg_file)
                messages.append(message)
            except Exception as e:
                logger.error(f"Error reading message file {msg_file}: {e}")
                continue

        if not messages:
            # No messages left, just update metadata
            self._update_session_metadata_empty(session_path)
            return

        # Rebuild conversation.json
        conversation = {
            "session_id": messages[0]["session_id"],
            "user_id": messages[0]["user_id"],
            "created_at": messages[0]["timestamp"],
            "updated_at": messages[-1]["timestamp"],
            "messages": messages
        }
        self._write_json(session_path / "conversation.json", conversation)

        # Rebuild conversation.md
        md_file = session_path / "conversation.md"
        header = f"""# Conversation: {messages[0]['session_id']}

**User ID:** {messages[0]['user_id']}
**Started:** {messages[0]['timestamp']}

---

"""
        md_file.write_text(header, encoding="utf-8")

        for message in messages:
            role = message["role"].capitalize()
            content = message["content"]
            timestamp = message["timestamp"]
            sequence = message["sequence"]

            message_md = f"""## Message {sequence} - {role}
**Timestamp:** {timestamp}

{content}

---

"""
            with md_file.open("a", encoding="utf-8") as f:
                f.write(message_md)

        # Update metadata
        metadata_file = session_path / "metadata.json"
        metadata = self._read_json(metadata_file)
        metadata["message_count"] = len(messages)
        metadata["updated_at"] = messages[-1]["timestamp"]
        self._write_json(metadata_file, metadata)

    def _update_session_metadata_empty(self, session_path: Path):
        """Update session metadata when all messages are deleted."""
        metadata_file = session_path / "metadata.json"
        metadata = self._read_json(metadata_file)
        metadata["message_count"] = 0
        metadata["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self._write_json(metadata_file, metadata)

    # Prompt History Methods
    def save_prompt(
        self,
        user_id: int,
        prompt: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Save a user prompt to prompt history.

        Args:
            user_id: ID of the user
            prompt: The user's prompt text
            session_id: Optional session identifier
            metadata: Optional metadata (e.g., intent, tokens, response_time)

        Returns:
            Saved prompt object with timestamp and ID
        """
        self._ensure_prompt_history_structure(user_id)

        prompt_history_path = self._get_user_path(user_id) / "prompt-history"
        now = datetime.utcnow()
        date_str = now.strftime("%Y-%m-%d")
        month_str = now.strftime("%Y-%m")

        # Create month directory if needed
        month_dir = prompt_history_path / month_str
        month_dir.mkdir(exist_ok=True)

        # Prompt entry
        prompt_id = f"prompt_{int(now.timestamp() * 1000000)}"  # Microsecond precision
        prompt_entry = {
            "prompt_id": prompt_id,
            "user_id": user_id,
            "session_id": session_id,
            "prompt": prompt,
            "timestamp": now.isoformat() + "Z",
            "date": date_str,
            "metadata": metadata or {}
        }

        # Append to daily JSONL file
        daily_file = month_dir / f"prompts-{date_str}.jsonl"
        with daily_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(prompt_entry, ensure_ascii=False) + "\n")

        # Update index
        self._update_prompt_index(user_id, prompt_entry)

        logger.debug(f"Saved prompt {prompt_id} for user {user_id}")
        return prompt_entry

    def get_prompt_history(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get user's prompt history with optional filters.

        Args:
            user_id: ID of the user
            limit: Maximum number of prompts to return
            offset: Number of prompts to skip
            start_date: Filter by start date (YYYY-MM-DD)
            end_date: Filter by end date (YYYY-MM-DD)
            session_id: Filter by session

        Returns:
            List of prompt objects in reverse chronological order
        """
        prompt_history_path = self._get_user_path(user_id) / "prompt-history"
        if not prompt_history_path.exists():
            return []

        prompts = []

        # Read all JSONL files
        for month_dir in sorted(prompt_history_path.iterdir(), reverse=True):
            if not month_dir.is_dir():
                continue

            for daily_file in sorted(month_dir.glob("prompts-*.jsonl"), reverse=True):
                try:
                    # Check date filter
                    file_date = daily_file.stem.replace("prompts-", "")
                    if start_date and file_date < start_date:
                        continue
                    if end_date and file_date > end_date:
                        continue

                    # Read JSONL file
                    with daily_file.open("r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                prompt_entry = json.loads(line)

                                # Apply filters
                                if session_id and prompt_entry.get("session_id") != session_id:
                                    continue

                                prompts.append(prompt_entry)

                except Exception as e:
                    logger.error(f"Error reading prompt file {daily_file}: {e}")
                    continue

        # Sort by timestamp descending (newest first)
        prompts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        return prompts[start_idx:end_idx]

    def search_prompts(
        self,
        user_id: int,
        query: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search user's prompt history by text.

        Args:
            user_id: ID of the user
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching prompt objects
        """
        all_prompts = self.get_prompt_history(user_id, limit=10000)
        query_lower = query.lower()

        # Simple text search
        matching_prompts = [
            p for p in all_prompts
            if query_lower in p.get("prompt", "").lower()
        ]

        return matching_prompts[:limit]

    def get_prompt_statistics(self, user_id: int) -> Dict:
        """
        Get statistics about user's prompt history.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with statistics
        """
        all_prompts = self.get_prompt_history(user_id, limit=100000)

        if not all_prompts:
            return {
                "total_prompts": 0,
                "first_prompt": None,
                "last_prompt": None,
                "prompts_by_date": {},
                "prompts_by_session": {},
                "average_prompt_length": 0
            }

        # Calculate statistics
        prompts_by_date = {}
        prompts_by_session = {}
        total_length = 0

        for prompt in all_prompts:
            date = prompt.get("date", "")
            session = prompt.get("session_id", "unknown")
            prompt_text = prompt.get("prompt", "")

            prompts_by_date[date] = prompts_by_date.get(date, 0) + 1
            prompts_by_session[session] = prompts_by_session.get(session, 0) + 1
            total_length += len(prompt_text)

        return {
            "total_prompts": len(all_prompts),
            "first_prompt": all_prompts[-1].get("timestamp") if all_prompts else None,
            "last_prompt": all_prompts[0].get("timestamp") if all_prompts else None,
            "prompts_by_date": prompts_by_date,
            "prompts_by_session": prompts_by_session,
            "average_prompt_length": total_length / len(all_prompts) if all_prompts else 0,
            "most_active_date": max(prompts_by_date.items(), key=lambda x: x[1])[0] if prompts_by_date else None
        }

    def delete_prompt_history(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        session_id: Optional[str] = None,
        confirm: bool = False
    ) -> int:
        """
        Delete prompt history with optional filters.

        Args:
            user_id: ID of the user
            start_date: Delete prompts from this date onwards
            end_date: Delete prompts up to this date
            session_id: Delete prompts from specific session
            confirm: Must be True to proceed

        Returns:
            Number of prompts deleted
        """
        if not confirm:
            raise ValueError("Must confirm deletion with confirm=True")

        prompt_history_path = self._get_user_path(user_id) / "prompt-history"
        if not prompt_history_path.exists():
            return 0

        deleted_count = 0

        if not start_date and not end_date and not session_id:
            # Delete entire prompt history
            shutil.rmtree(prompt_history_path)
            self._ensure_prompt_history_structure(user_id)
            logger.warning(f"Deleted ALL prompt history for user {user_id}")
            return -1  # Indicate all deleted

        # Filtered deletion - need to rebuild files
        prompts_to_keep = []
        all_prompts = self.get_prompt_history(user_id, limit=100000)

        for prompt in all_prompts:
            prompt_date = prompt.get("date", "")
            prompt_session = prompt.get("session_id", "")

            # Check if should be deleted
            should_delete = True

            if start_date and prompt_date < start_date:
                should_delete = False
            if end_date and prompt_date > end_date:
                should_delete = False
            if session_id and prompt_session != session_id:
                should_delete = False

            if should_delete:
                deleted_count += 1
            else:
                prompts_to_keep.append(prompt)

        # Rebuild prompt history with remaining prompts
        if deleted_count > 0:
            shutil.rmtree(prompt_history_path)
            self._ensure_prompt_history_structure(user_id)

            for prompt in prompts_to_keep:
                self._write_prompt_direct(user_id, prompt)

            logger.info(f"Deleted {deleted_count} prompts for user {user_id}")

        return deleted_count

    def export_prompt_history(
        self,
        user_id: int,
        output_path: str,
        format: str = "json"
    ) -> bool:
        """
        Export user's prompt history to a file.

        Args:
            user_id: ID of the user
            output_path: Path to output file
            format: Export format ('json', 'jsonl', 'csv', or 'txt')

        Returns:
            True if export succeeded
        """
        prompts = self.get_prompt_history(user_id, limit=100000)

        try:
            output_file = Path(output_path)

            if format == "json":
                with output_file.open("w", encoding="utf-8") as f:
                    json.dump(prompts, f, indent=2, ensure_ascii=False)

            elif format == "jsonl":
                with output_file.open("w", encoding="utf-8") as f:
                    for prompt in prompts:
                        f.write(json.dumps(prompt, ensure_ascii=False) + "\n")

            elif format == "csv":
                import csv
                with output_file.open("w", encoding="utf-8", newline="") as f:
                    if prompts:
                        writer = csv.DictWriter(f, fieldnames=prompts[0].keys())
                        writer.writeheader()
                        writer.writerows(prompts)

            elif format == "txt":
                with output_file.open("w", encoding="utf-8") as f:
                    for prompt in prompts:
                        f.write(f"[{prompt['timestamp']}] {prompt['prompt']}\n\n")

            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Exported {len(prompts)} prompts to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting prompt history: {e}")
            return False

    def _update_prompt_index(self, user_id: int, prompt_entry: Dict):
        """Update the searchable prompt index."""
        prompt_history_path = self._get_user_path(user_id) / "prompt-history"
        index_file = prompt_history_path / "prompt-index.json"

        if index_file.exists():
            index = self._read_json(index_file)
        else:
            index = {
                "user_id": user_id,
                "last_updated": None,
                "total_prompts": 0,
                "dates": []
            }

        # Update index
        index["last_updated"] = prompt_entry["timestamp"]
        index["total_prompts"] += 1

        date = prompt_entry["date"]
        if date not in index["dates"]:
            index["dates"].append(date)
            index["dates"].sort()

        self._write_json(index_file, index)

    def _write_prompt_direct(self, user_id: int, prompt_entry: Dict):
        """Write a prompt entry directly (used during rebuild)."""
        prompt_history_path = self._get_user_path(user_id) / "prompt-history"
        date_str = prompt_entry["date"]
        month_str = date_str[:7]  # YYYY-MM

        month_dir = prompt_history_path / month_str
        month_dir.mkdir(exist_ok=True)

        daily_file = month_dir / f"prompts-{date_str}.jsonl"
        with daily_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(prompt_entry, ensure_ascii=False) + "\n")
