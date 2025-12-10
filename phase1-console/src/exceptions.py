"""Custom exceptions for Todo CLI Application."""


class TaskNotFoundError(Exception):
    """Raised when a task with the specified ID is not found."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task not found (ID: {task_id})")


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidIdError(Exception):
    """Raised when a task ID is not a valid positive integer."""

    def __init__(self) -> None:
        super().__init__("Invalid task ID")
