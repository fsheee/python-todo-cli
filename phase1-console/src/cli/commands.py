"""CLI command handlers for Todo CLI Application."""

from src.exceptions import InvalidIdError, TaskNotFoundError, ValidationError
from src.models.task import Task
from src.services.task_service import TaskService


def view_tasks(service: TaskService) -> None:
    """Display all tasks with status indicators.

    Args:
        service: The task service instance.
    """
    tasks = service.get_all()

    if not tasks:
        print("\nNo tasks found.")
        return

    # Display header
    print()
    print(f"{'ID':<4}{'Status':<8}{'Title':<20}Description")
    print("─" * 55)

    # Display each task
    for task in tasks:
        status = "[X]" if task.is_complete else "[ ]"
        print(f"{task.id:<4}{status:<8}{task.title:<20}{task.description}")

    print("─" * 55)

    # Display summary
    complete_count = sum(1 for t in tasks if t.is_complete)
    incomplete_count = len(tasks) - complete_count
    print(f"Total: {len(tasks)} tasks ({complete_count} complete, {incomplete_count} incomplete)")


def display_menu() -> None:
    """Display the main menu options."""
    print()
    print("╔════════════════════════════════════════╗")
    print("║         TODO APP - Phase I             ║")
    print("╠════════════════════════════════════════╣")
    print("║  1. View all tasks                     ║")
    print("║  2. Add new task                       ║")
    print("║  3. Update task                        ║")
    print("║  4. Delete task                        ║")
    print("║  5. Toggle complete/incomplete         ║")
    print("║  6. Exit                               ║")
    print("╚════════════════════════════════════════╝")


def get_menu_choice() -> str:
    """Get and return the user's menu choice."""
    return input("Enter choice (1-6): ").strip()


def add_task_command(service: TaskService) -> None:
    """Handle the add task command with user input prompts.

    Args:
        service: The task service instance.
    """
    title = input("Enter task title: ").strip()
    description = input("Enter description (optional): ").strip()

    try:
        task = service.add_task(title, description)
        print(f"✓ Task added successfully (ID: {task.id})")
    except ValidationError as e:
        print(f"✗ Error: {e}")


def parse_task_id(id_str: str) -> int:
    """Parse and validate a task ID string.

    Args:
        id_str: The string to parse as a task ID.

    Returns:
        The parsed integer ID.

    Raises:
        InvalidIdError: If the string is not a valid positive integer.
    """
    try:
        task_id = int(id_str)
        if task_id <= 0:
            raise InvalidIdError()
        return task_id
    except ValueError:
        raise InvalidIdError()


def toggle_command(service: TaskService) -> None:
    """Handle the toggle complete/incomplete command.

    Args:
        service: The task service instance.
    """
    id_str = input("Enter task ID to toggle: ").strip()

    try:
        task_id = parse_task_id(id_str)
        task = service.toggle_complete(task_id)
        status = "complete" if task.is_complete else "incomplete"
        print(f"✓ Task {task_id} marked as {status}")
    except InvalidIdError as e:
        print(f"✗ Error: {e}")
    except TaskNotFoundError as e:
        print(f"✗ Error: {e}")


def update_command(service: TaskService) -> None:
    """Handle the update task command with optional field inputs.

    Args:
        service: The task service instance.
    """
    id_str = input("Enter task ID to update: ").strip()

    try:
        task_id = parse_task_id(id_str)

        # Check if task exists first
        task = service.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        # Get new values (empty means keep current)
        new_title = input("Enter new title (or press Enter to keep current): ").strip()
        new_description = input(
            "Enter new description (or press Enter to keep current): "
        ).strip()

        # Only pass non-empty values (None means no change)
        title = new_title if new_title else None
        description = new_description if new_description else None

        if title is None and description is None:
            print("No changes made.")
            return

        service.update_task(task_id, title, description)
        print(f"✓ Task {task_id} updated successfully")
    except InvalidIdError as e:
        print(f"✗ Error: {e}")
    except TaskNotFoundError as e:
        print(f"✗ Error: {e}")
    except ValidationError as e:
        print(f"✗ Error: {e}")


def delete_command(service: TaskService) -> None:
    """Handle the delete task command.

    Args:
        service: The task service instance.
    """
    id_str = input("Enter task ID to delete: ").strip()

    try:
        task_id = parse_task_id(id_str)
        service.delete_task(task_id)
        print(f"✓ Task {task_id} deleted successfully")
    except InvalidIdError as e:
        print(f"✗ Error: {e}")
    except TaskNotFoundError as e:
        print(f"✗ Error: {e}")
