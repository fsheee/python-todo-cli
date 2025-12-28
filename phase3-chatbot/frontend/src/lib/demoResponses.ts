/**
 * Demo response generator for landing page ChatKit demo
 * Simulates AI responses without backend calls
 */

export interface DemoMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export const DEMO_TODOS = [
  {
    id: 1,
    title: 'Buy groceries',
    status: 'pending',
    priority: 'high',
    due_date: 'tomorrow'
  },
  {
    id: 2,
    title: 'Call dentist',
    status: 'pending',
    priority: 'medium',
    due_date: 'today'
  },
  {
    id: 3,
    title: 'Finish quarterly report',
    status: 'pending',
    priority: 'high',
    due_date: 'next week'
  }
];

export function getDemoResponse(prompt: string): string {
  const lower = prompt.toLowerCase();

  // Show/List tasks
  if (lower.includes('show') || lower.includes('list') || lower.includes('tasks') || lower.includes('what')) {
    return `You have 3 demo tasks:

1. 🔴 Buy groceries (High priority, due tomorrow)
2. 📞 Call dentist (Due today)
3. 📄 Finish quarterly report (High priority, due next week)

*This is a demo. Sign up to create and manage real todos!*`;
  }

  // Add/Create task
  if (lower.includes('add') || lower.includes('create') || lower.includes('new')) {
    const taskMatch = prompt.match(/add|create|new\s+(.+)/i);
    const taskName = taskMatch ? taskMatch[1] : 'your task';

    return `I've created a demo task: "${taskName}" 📝

In the real app, this would be saved to your account permanently.

**Ready to try it for real?** Sign up above to start managing your todos! 🚀`;
  }

  // Complete/Finish task
  if (lower.includes('finish') || lower.includes('complete') || lower.includes('done') || lower.includes('mark')) {
    return `Great work! 🎉 I've marked the task as completed in this demo.

In the real app, you'd see your progress and get achievement celebrations!

**Sign up to track your real accomplishments!** ✅`;
  }

  // Update/Change task
  if (lower.includes('update') || lower.includes('change') || lower.includes('make') || lower.includes('set')) {
    return `Updated! ✨ In the demo, this would change the task.

The real app lets you update:
- Priority (high, medium, low)
- Due dates ("tomorrow", "next Monday")
- Titles and descriptions

**Sign up to manage tasks your way!**`;
  }

  // Delete/Remove task
  if (lower.includes('delete') || lower.includes('remove')) {
    return `⚠️ In the real app, I'd ask for confirmation before deleting.

This is a demo, so your tasks are safe! 😊

**Sign up to have full control over your todo list!**`;
  }

  // Search/Find tasks
  if (lower.includes('search') || lower.includes('find')) {
    return `🔍 In the real app, I'd search through all your tasks!

The demo only has 3 sample tasks, but the real app can:
- Search by keyword
- Filter by status, priority, date
- Show relevant results instantly

**Sign up to unlock powerful search!**`;
  }

  // Help
  if (lower.includes('help') || lower.includes('how') || lower.includes('what can')) {
    return `I'm an AI todo assistant! I can help you:

✅ **Create tasks:** "Add buy milk"
📋 **View tasks:** "Show my tasks"
✏️ **Update tasks:** "Make X high priority"
✔️ **Complete tasks:** "I finished X"
🗑️ **Delete tasks:** "Delete X"
🔍 **Search tasks:** "Find work tasks"

**This is a demo.** Sign up to unlock the full AI assistant and manage your real todos! 🚀`;
  }

  // Greeting
  if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
    return `Hello! 👋 I'm your AI todo assistant demo.

Try asking me:
- "Show my tasks"
- "Add buy milk"
- "What's due today?"
- "Help"

**Sign up above to start managing your real todos!** 🎯`;
  }

  // Default response
  return `Interesting! In the full app, I'd help you with that.

Try asking me to:
- Show tasks
- Add a new task
- Mark something as done
- Get help

**Sign up above to unlock the full AI todo assistant!** ✨`;
}

export function getInitialDemoMessages(): DemoMessage[] {
  return [
    {
      role: 'assistant',
      content: `👋 Welcome to the Todo Assistant demo!

Try asking me:
- "Show my tasks"
- "Add buy milk"
- "Help"

*This is a demo with sample data. Sign up to create real todos!*`,
      timestamp: new Date().toISOString()
    }
  ];
}
