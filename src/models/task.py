"""Task model for Todo CLI Application."""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Unique identifier (auto-generated, positive integer).
        title: Short description of what needs to be done (required, non-empty).
        description: Detailed information about the task (optional).
        is_complete: Completion state (default: False).
    """

    id: int
    title: str
    description: str = ""
    is_complete: bool = False
