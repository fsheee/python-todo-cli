"""
System prompts and templates for the Todo Assistant agent

Spec Reference: specs/agents/todo-agent.md - System Prompt
Task: 3.2
"""

from datetime import datetime


def get_system_prompt(current_date: str = None, user_timezone: str = "UTC") -> str:
    """
    Get the base system prompt for the Todo Assistant agent

    Args:
        current_date: Current date string (defaults to today)
        user_timezone: User's timezone (defaults to UTC)

    Returns:
        Complete system prompt string
    """
    if not current_date:
        current_date = datetime.now().strftime("%Y-%m-%d")

    return f"""You are a helpful AI assistant that manages todo lists through natural conversation.

Your role is to help users:
- Create new todos
- View their todo lists
- Update existing todos
- Mark todos as complete
- Delete todos
- Search and filter their tasks

Guidelines:
1. Be conversational and friendly, but concise
2. Always confirm actions you take (create, update, delete)
3. Ask for clarification when user intent is ambiguous
4. Use the provided MCP tools to perform all todo operations
5. Never make up or assume todo IDs - always verify with list/search first
6. Format responses with emojis and structure for readability
7. Remember context from the conversation to handle references like "that one" or "the first task"
8. Provide helpful suggestions when users seem stuck
9. Celebrate completions and encourage productivity

Important rules:
- All operations are for the authenticated user only (user_id provided in context)
- Dates like "tomorrow", "next week" should be calculated relative to today's date
- Always ask for confirmation before deleting tasks
- If a tool call fails, explain the error clearly and suggest alternatives
- Keep responses under 150 words unless providing a list

Today's date is: {current_date}
User timezone: {user_timezone}
"""


def get_context_prompt(
    user_id: int,
    user_email: str,
    pending_count: int,
    completed_count: int,
    chat_history: list
) -> str:
    """
    Build context prompt with user info and conversation history

    Args:
        user_id: User's ID
        user_email: User's email
        pending_count: Number of pending tasks
        completed_count: Number of completed tasks
        chat_history: Recent conversation messages

    Returns:
        Context prompt string
    """
    history_text = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in chat_history[-10:]  # Last 10 messages
    ])

    return f"""Previous conversation:
{history_text if history_text else "(No previous messages)"}

User information:
- User ID: {user_id}
- Email: {user_email}
- Current tasks count: {pending_count} pending, {completed_count} completed

Available MCP Tools:
- create_todo: Create a new todo item
- list_todos: Retrieve user's todos with optional filters
- update_todo: Update an existing todo
- delete_todo: Delete a todo (requires confirmation)
- search_todos: Search todos by keyword
"""


# Response templates
RESPONSE_TEMPLATES = {
    "create_success": [
        "I've created a new todo for you:\n📝 {title}\n{details}\n\nWould you like to add any details or set a due date?",
        "Got it! I've added '{title}' to your list.\n{details}",
        "Done! Created a new task: {title}\n{details}"
    ],
    "list": [
        "You have {count} {status} tasks:\n\n{list}\n\nWould you like details on any of these?",
        "Here are your {status} tasks ({count} total):\n\n{list}",
        "Your {status} task list:\n\n{list}"
    ],
    "update_success": [
        "Updated! '{title}' is now {change}.",
        "Done! I've updated '{title}' - {change}.",
        "Got it! '{title}' has been updated: {change}."
    ],
    "complete_success": [
        "Awesome! ✅ I've marked '{title}' as completed.\n\nYou have {remaining} tasks remaining. Keep it up!",
        "Great work! 🎉 '{title}' is now complete.\n\n{remaining} tasks left to go!",
        "Nicely done! 👏 '{title}' has been checked off your list.\n\n{remaining} tasks remaining.",
        "Way to go! 🌟 '{title}' is marked as done.\n\nYou have {remaining} tasks left."
    ],
    "delete_confirm": [
        "⚠️ Are you sure you want to delete '{title}'?\nThis action cannot be undone.\n\nType 'yes' to confirm or 'no' to cancel.",
        "⚠️ Delete '{title}'? This cannot be undone.\n\nConfirm with 'yes' or cancel with 'no'."
    ],
    "delete_success": [
        "Done! '{title}' has been removed from your list.",
        "Removed! '{title}' is no longer on your list."
    ],
    "search_results": [
        "I found {count} tasks matching '{query}':\n\n{list}\n\nWould you like details on any of these?",
        "Found {count} tasks for '{query}':\n\n{list}"
    ],
    "error": [
        "I'm sorry, I {error_description}.\n\n{suggestion}\n\nHow can I help you instead?",
        "Hmm, {error_description}.\n\n{suggestion}"
    ],
    "not_found": [
        "I couldn't find a task about '{query}' in your list.\n\nWould you like to:\n- See all your tasks\n- Create a new task\n- Try a different search?",
        "No tasks found matching '{query}'.\n\nWant to create one or see your full list?"
    ],
    "help": [
        """I'm your AI todo assistant! Here's what I can help you with:

✅ Create tasks: 'Add buy milk', 'I need to call mom tomorrow'
📋 View tasks: 'Show my tasks', 'What's due today?'
✏️ Update tasks: 'Make X high priority', 'Move X to tomorrow'
✔️ Complete tasks: 'I finished X', 'Mark X as done'
🗑️ Delete tasks: 'Delete X', 'Remove task 2'
🔍 Search tasks: 'Find tasks about X'

Just tell me what you need in your own words!"""
    ]
}


# Encouragement messages for completions
ENCOURAGEMENT_MESSAGES = [
    "Great work! ✅",
    "Nicely done! 🎉",
    "Way to go! 🌟",
    "Excellent! 👏",
    "You're on a roll! 🔥",
    "Keep it up! 💪",
    "Awesome! ⭐"
]


# Messages for completing all tasks
ALL_DONE_MESSAGES = [
    "All done! You've cleared your list! 🎉",
    "Amazing! You're all caught up! 🌟",
    "Fantastic! Nothing left to do! 🎊",
    "You did it! Everything's complete! 🎯"
]
