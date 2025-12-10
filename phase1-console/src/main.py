"""Main entry point for Todo CLI Application."""

from src.cli.commands import (
    add_task_command,
    delete_command,
    display_menu,
    get_menu_choice,
    toggle_command,
    update_command,
    view_tasks,
)
from src.services.task_service import TaskService


def main() -> None:
    """Run the Todo CLI application main loop."""
    service = TaskService()

    print("Welcome to Todo App - Phase I")

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == "6":
            print("Goodbye!")
            break
        elif choice == "1":
            view_tasks(service)
        elif choice == "2":
            add_task_command(service)
        elif choice == "3":
            update_command(service)
        elif choice == "4":
            delete_command(service)
        elif choice == "5":
            toggle_command(service)
        else:
            print("✗ Error: Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()
