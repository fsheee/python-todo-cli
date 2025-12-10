"""Tests for Task model."""

from src.models.task import Task


class TestTask:
    """Tests for Task dataclass."""

    def test_create_task_with_required_fields(self):
        """Task can be created with id and title."""
        task = Task(id=1, title="Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.is_complete is False

    def test_create_task_with_all_fields(self):
        """Task can be created with all fields."""
        task = Task(
            id=1,
            title="Buy groceries",
            description="Milk, eggs, bread",
            is_complete=True,
        )

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.is_complete is True

    def test_task_defaults(self):
        """Task has correct default values."""
        task = Task(id=1, title="Test")

        assert task.description == ""
        assert task.is_complete is False

    def test_task_is_mutable(self):
        """Task fields can be modified."""
        task = Task(id=1, title="Original")

        task.title = "Updated"
        task.description = "New description"
        task.is_complete = True

        assert task.title == "Updated"
        assert task.description == "New description"
        assert task.is_complete is True
