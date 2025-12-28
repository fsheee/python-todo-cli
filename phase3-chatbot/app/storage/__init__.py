"""Storage module for chat history management."""

from .file_storage import FileBasedChatStorage

# Global storage instance
_storage_instance = None


def get_storage() -> FileBasedChatStorage:
    """
    Get or create the global file-based storage instance.

    Returns:
        FileBasedChatStorage instance
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = FileBasedChatStorage()
    return _storage_instance


__all__ = ["FileBasedChatStorage", "get_storage"]
