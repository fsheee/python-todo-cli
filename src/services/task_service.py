"""Task service for Todo CLI Application."""

from src.exceptions import TaskNotFoundError, ValidationError
from src.models.task import Task


class TaskService:
    """Service for managing tasks in memory.

    Provides CRUD operations for Task entities using an in-memory
    dictionary for storage.
    """

    def __init__(self) -> None:
        """Initialize the task service with empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def get_all(self) -> list[Task]:
        """Return all tasks as a list.

        Returns:
            List of all tasks, ordered by ID.
        """
        return list(self._tasks.values())

    def add_task(self, title: str, description: str = "") -> Task:
        """Add a new task with the given title and description.

        Args:
            title: The task title (required, non-empty).
            description: The task description (optional).

        Returns:
            The newly created Task.

        Raises:
            ValidationError: If the title is empty or whitespace-only.
        """
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")

        task = Task(
            id=self._next_id,
            title=title.strip(),
            description=description.strip() if description else "",
            is_complete=False,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task | None:
        """Get a task by its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The Task if found, None otherwise.
        """
        return self._tasks.get(task_id)

    def toggle_complete(self, task_id: int) -> Task:
        """Toggle the completion status of a task.

        Args:
            task_id: The ID of the task to toggle.

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If no task with the given ID exists.
        """
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        task.is_complete = not task.is_complete
        return task

    def update_task(
        self, task_id: int, title: str | None = None, description: str | None = None
    ) -> Task:
        """Update a task's title and/or description.

        Args:
            task_id: The ID of the task to update.
            title: The new title (if provided, must be non-empty).
            description: The new description (can be empty string).

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If no task with the given ID exists.
            ValidationError: If a non-None title is empty or whitespace-only.
        """
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        if title is not None:
            if not title or not title.strip():
                raise ValidationError("Title cannot be empty")
            task.title = title.strip()

        if description is not None:
            task.description = description.strip()

        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if the task was deleted.

        Raises:
            TaskNotFoundError: If no task with the given ID exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        del self._tasks[task_id]
        return True
