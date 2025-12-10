"""Tests for TaskService."""

import pytest

from src.exceptions import TaskNotFoundError, ValidationError
from src.services.task_service import TaskService


class TestTaskServiceAdd:
    """Tests for TaskService.add_task()."""

    def test_add_task_returns_task(self):
        """add_task returns the created task."""
        service = TaskService()

        task = service.add_task("Buy groceries")

        assert task.title == "Buy groceries"
        assert task.id == 1

    def test_add_task_with_description(self):
        """add_task accepts optional description."""
        service = TaskService()

        task = service.add_task("Buy groceries", "Milk, eggs, bread")

        assert task.description == "Milk, eggs, bread"

    def test_add_task_increments_id(self):
        """Each task gets a unique incremented ID."""
        service = TaskService()

        task1 = service.add_task("Task 1")
        task2 = service.add_task("Task 2")
        task3 = service.add_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_sets_incomplete_by_default(self):
        """New tasks are incomplete by default."""
        service = TaskService()

        task = service.add_task("Test task")

        assert task.is_complete is False

    def test_add_task_strips_whitespace(self):
        """Title and description are stripped of whitespace."""
        service = TaskService()

        task = service.add_task("  Buy groceries  ", "  Milk, eggs  ")

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs"

    def test_add_task_empty_title_raises_error(self):
        """Empty title raises ValidationError."""
        service = TaskService()

        with pytest.raises(ValidationError) as exc_info:
            service.add_task("")

        assert "Title cannot be empty" in str(exc_info.value)

    def test_add_task_whitespace_title_raises_error(self):
        """Whitespace-only title raises ValidationError."""
        service = TaskService()

        with pytest.raises(ValidationError):
            service.add_task("   ")


class TestTaskServiceGetAll:
    """Tests for TaskService.get_all()."""

    def test_get_all_empty(self):
        """get_all returns empty list when no tasks."""
        service = TaskService()

        tasks = service.get_all()

        assert tasks == []

    def test_get_all_returns_all_tasks(self):
        """get_all returns all added tasks."""
        service = TaskService()
        service.add_task("Task 1")
        service.add_task("Task 2")

        tasks = service.get_all()

        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"


class TestTaskServiceGetTask:
    """Tests for TaskService.get_task()."""

    def test_get_task_returns_task(self):
        """get_task returns the task with matching ID."""
        service = TaskService()
        service.add_task("Test task")

        task = service.get_task(1)

        assert task is not None
        assert task.title == "Test task"

    def test_get_task_not_found_returns_none(self):
        """get_task returns None for non-existent ID."""
        service = TaskService()

        task = service.get_task(999)

        assert task is None


class TestTaskServiceToggle:
    """Tests for TaskService.toggle_complete()."""

    def test_toggle_marks_complete(self):
        """toggle_complete marks incomplete task as complete."""
        service = TaskService()
        service.add_task("Test task")

        task = service.toggle_complete(1)

        assert task.is_complete is True

    def test_toggle_marks_incomplete(self):
        """toggle_complete marks complete task as incomplete."""
        service = TaskService()
        service.add_task("Test task")
        service.toggle_complete(1)  # Now complete

        task = service.toggle_complete(1)  # Now incomplete

        assert task.is_complete is False

    def test_toggle_not_found_raises_error(self):
        """toggle_complete raises TaskNotFoundError for non-existent ID."""
        service = TaskService()

        with pytest.raises(TaskNotFoundError) as exc_info:
            service.toggle_complete(999)

        assert exc_info.value.task_id == 999


class TestTaskServiceUpdate:
    """Tests for TaskService.update_task()."""

    def test_update_title(self):
        """update_task updates the title."""
        service = TaskService()
        service.add_task("Original title")

        task = service.update_task(1, title="New title")

        assert task.title == "New title"

    def test_update_description(self):
        """update_task updates the description."""
        service = TaskService()
        service.add_task("Test", "Original description")

        task = service.update_task(1, description="New description")

        assert task.description == "New description"

    def test_update_both_fields(self):
        """update_task updates both title and description."""
        service = TaskService()
        service.add_task("Original", "Original desc")

        task = service.update_task(1, title="New title", description="New desc")

        assert task.title == "New title"
        assert task.description == "New desc"

    def test_update_none_preserves_values(self):
        """update_task with None preserves existing values."""
        service = TaskService()
        service.add_task("Original", "Original desc")

        task = service.update_task(1, title=None, description=None)

        assert task.title == "Original"
        assert task.description == "Original desc"

    def test_update_not_found_raises_error(self):
        """update_task raises TaskNotFoundError for non-existent ID."""
        service = TaskService()

        with pytest.raises(TaskNotFoundError):
            service.update_task(999, title="New")

    def test_update_empty_title_raises_error(self):
        """update_task raises ValidationError for empty title."""
        service = TaskService()
        service.add_task("Test")

        with pytest.raises(ValidationError):
            service.update_task(1, title="")


class TestTaskServiceDelete:
    """Tests for TaskService.delete_task()."""

    def test_delete_removes_task(self):
        """delete_task removes the task."""
        service = TaskService()
        service.add_task("Test task")

        result = service.delete_task(1)

        assert result is True
        assert service.get_task(1) is None

    def test_delete_not_found_raises_error(self):
        """delete_task raises TaskNotFoundError for non-existent ID."""
        service = TaskService()

        with pytest.raises(TaskNotFoundError):
            service.delete_task(999)
