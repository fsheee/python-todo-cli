# Phase 3 Chatbot - User Guide

## 👋 Welcome to Your AI Todo Assistant!

Manage your todos through natural conversation. No forms, no clicking - just tell your AI assistant what you need!

---

## 🚀 Getting Started

### Step 1: Login

1. Go to `https://chat.your-domain.com/login`
2. Enter your email and password (same as Phase 2)
3. Click "Login"

You'll be redirected to the chat interface.

### Step 2: Start Chatting

Type naturally! The AI understands your requests.

**Examples:**
- "Add buy milk to my list"
- "Show me what I need to do today"
- "I finished the groceries"
- "Make the report high priority"
- "Delete the meeting task"

---

## ✨ What You Can Do

### 1. Create Todos

Just tell the AI what you need to do!

**Examples:**
```
You: "Add buy milk"
AI: "I've added 'Buy milk' to your list. 📝"

You: "I need to call the dentist tomorrow"
AI: "I've created 'Call the dentist' and set it for tomorrow. 📅"

You: "Create a high priority task to finish the quarterly report"
AI: "Got it! I've created a high priority task:
     📝 Finish the quarterly report
     🔴 High priority

     Would you like to set a due date?"
```

**What the AI Can Extract:**
- **Title** from any description
- **Due dates** like "tomorrow", "next Monday", "December 25"
- **Priority** when you say "high priority", "urgent", "low priority"
- **Descriptions** when you add extra details

---

### 2. View Your Tasks

Ask to see your todos anytime!

**Examples:**
```
You: "Show my tasks"
AI: "You have 3 pending tasks:

     1. 📝 Buy milk
     2. 📞 Call dentist (High priority, due tomorrow)
     3. 📄 Finish report (Due next week)

     Would you like details on any of these?"

You: "What's due today?"
AI: "You have 2 tasks due today:

     1. 🔴 Submit timesheet (High priority)
     2. 📧 Reply to client email

     Need help prioritizing?"

You: "Show high priority tasks"
AI: "Here are your high priority tasks:

     1. 🔴 Call dentist (Due tomorrow)
     2. 🔴 Submit timesheet (Due today)

     Focus on the one due today first?"
```

**Ways to View:**
- "Show my tasks" - All pending todos
- "What's due today?" - Today's tasks
- "Show completed tasks" - What you've done
- "What's overdue?" - Past-due items
- "Show high priority tasks" - Urgent items
- "What's due this week?" - Weekly overview

---

### 3. Update Your Tasks

Change any detail through conversation!

**Examples:**
```
You: "Change the groceries task to tomorrow"
AI: "I found 'Buy groceries' (currently due today).
     Would you like me to move it to tomorrow?"

You: "Yes"
AI: "Done! 'Buy groceries' is now due tomorrow. 📅"

You: "Make the report high priority"
AI: "Updated! 'Finish report' is now high priority. 🔴"

You: "Rename 'call dentist' to 'dentist appointment at 2pm'"
AI: "Updated! The task is now called 'Dentist appointment at 2pm'."
```

**What You Can Update:**
- **Title** - "Rename X to Y"
- **Due date** - "Move X to tomorrow"
- **Priority** - "Make X high priority"
- **Description** - "Add details to X: ..."
- **Status** - "Mark X as complete" (see next section)

---

### 4. Mark Tasks Complete

Celebrate your progress!

**Examples:**
```
You: "I finished buying milk"
AI: "Awesome! 🎉 I've marked 'Buy milk' as completed.

     You have 2 tasks remaining. Keep it up!"

You: "Mark task 1 as done"
AI: "Great work! ✅ 'Call dentist' is now complete.

     You're making great progress today!"

You: "I did all of today's tasks"
AI: "Amazing! 🎉 I've marked 3 tasks as completed:
     ✅ Buy milk
     ✅ Call dentist
     ✅ Submit timesheet

     You're all caught up for today! 🌟"
```

**Ways to Mark Complete:**
- "I finished [task]"
- "Mark [task] as done"
- "Complete [task]"
- "Check off [task]"
- "I did [task]"

**The AI Encourages You:**
- "Great work! ✅"
- "Awesome! 🎉"
- "Nicely done! 🌟"
- "Way to go! 💪"

---

### 5. Delete Tasks

Remove tasks you no longer need.

**Important:** The AI will always ask for confirmation before deleting!

**Examples:**
```
You: "Delete the groceries task"
AI: "⚠️ Are you sure you want to delete 'Buy groceries'?
     This action cannot be undone.

     Type 'yes' to confirm or 'no' to cancel."

You: "yes"
AI: "Done! 'Buy groceries' has been removed from your list."

You: "Remove task 2"
AI: "⚠️ This will delete 'Call dentist'. Are you sure?"

You: "no"
AI: "No problem! The task is still on your list."
```

**Safety Features:**
- Always asks for confirmation
- Shows what will be deleted
- Can cancel anytime
- Permanent deletion (cannot undo)

---

### 6. Search Your Tasks

Find specific tasks quickly!

**Examples:**
```
You: "Find tasks about work"
AI: "I found 2 tasks matching 'work':

     1. 💼 Review work email
     2. 📊 Prepare work presentation

     Would you like details on either of these?"

You: "Search for meeting"
AI: "I found 3 tasks related to 'meeting':

     1. 📅 Prepare for client meeting (High priority)
     2. 📝 Review meeting notes
     3. 📧 Send meeting agenda

     Which one are you looking for?"
```

---

## 🎯 Smart Features

### Context Awareness

The AI remembers your conversation!

**Example:**
```
You: "Show my tasks"
AI: [Lists 3 tasks]

You: "Make the second one high priority"
AI: "Updated! 'Call dentist' is now high priority. 🔴"

You: "And set it for tomorrow"
AI: "Done! 'Call dentist' is now due tomorrow. 📅"
```

**The AI Remembers:**
- Tasks you just listed
- The last task you created
- What you just talked about
- References like "it", "that one", "the first task"

**Context Timeout:**
- After 5 messages, you may need to be more specific
- Just describe the task again if the AI asks

---

### Natural Date Understanding

The AI understands dates naturally!

**Examples:**
- "tomorrow" → Next day
- "next Monday" → Following Monday
- "in 3 days" → 3 days from now
- "this Friday" → Upcoming Friday
- "next week" → Asks which day
- "December 25" → Specific date

---

### Smart Suggestions

The AI helps you stay productive!

**Examples:**
```
You: "What should I focus on?"
AI: "You have 2 high priority tasks:

     1. 🔴 Submit timesheet (Due today)
     2. 🔴 Client presentation (Due tomorrow)

     I'd recommend starting with the timesheet since it's due today!"

You: [completes all tasks]
AI: "All done! You've cleared your list! 🎉

     Ready to add new tasks, or taking a break?"
```

---

## 💬 Conversation Tips

### Be Natural

Talk like you would to a person:
- ✅ "Add buy milk"
- ✅ "I need to buy milk"
- ✅ "Remind me to buy milk"
- ✅ "Can you add buy milk to my list?"

All work the same way!

### Use References

After listing tasks, you can refer to them easily:
- "the first one"
- "task 2"
- "that one"
- "it"

### Multiple Tasks

You can create multiple tasks:
```
You: "I need to buy milk and call the dentist"
AI: "I see two tasks. Should I create them separately?"

You: "Yes"
AI: "Perfect! I've created:
     1. Buy milk
     2. Call the dentist"
```

---

## 🆘 Getting Help

### Ask for Help

```
You: "Help"
AI: "I'm your AI todo assistant! Here's what I can help you with:

     ✅ Create tasks: 'Add buy milk', 'I need to call mom tomorrow'
     📋 View tasks: 'Show my tasks', 'What's due today?'
     ✏️ Update tasks: 'Make X high priority', 'Move X to tomorrow'
     ✔️ Complete tasks: 'I finished X', 'Mark X as done'
     🗑️ Delete tasks: 'Delete X', 'Remove task 2'
     🔍 Search tasks: 'Find tasks about X'

     Just tell me what you need in your own words!"
```

### Start a New Conversation

Click "New Chat" button to:
- Clear message history
- Start fresh session
- Keep your todos (only clears chat)

### Logout

Click "Logout" to:
- Clear your session
- Return to login page
- Secure your data

---

## ❓ FAQ

**Q: Does the AI remember previous conversations?**
A: Yes! Within the same session, the AI remembers your conversation. Start a "New Chat" to reset.

**Q: Can I use it on mobile?**
A: Yes! The interface is fully responsive and works on phones and tablets.

**Q: How do I undo a deletion?**
A: Deletions are permanent. The AI will always ask for confirmation first.

**Q: What if the AI doesn't understand me?**
A: Try rephrasing, or the AI will ask clarifying questions.

**Q: Can I see my old conversations?**
A: Yes, conversations persist in your session. View history by session ID.

**Q: Is my data private?**
A: Yes! Only you can see your todos and conversations. User isolation is enforced.

---

## 🎉 Example Workflow

Here's a typical day using your AI Todo Assistant:

```
Morning:
You: "Show me what I need to do today"
AI: [Lists 5 tasks for today]

You: "I finished the timesheet"
AI: "Great work! ✅ That's done."

Afternoon:
You: "Add prepare slides for tomorrow's meeting, high priority"
AI: "I've created a high priority task for you! 📝"

You: "Actually, make it due Friday"
AI: "Updated! 'Prepare slides' is now due Friday."

Evening:
You: "What did I accomplish today?"
AI: "You completed 4 tasks today! 🎉
     ✅ Submit timesheet
     ✅ Reply to emails
     ✅ Call dentist
     ✅ Buy groceries

     Excellent work!"
```

---

## 💡 Pro Tips

1. **Be specific with dates** - "tomorrow" is clearer than "soon"
2. **Use priority** - Mark urgent tasks as "high priority"
3. **Reference by number** - After listing, say "complete number 2"
4. **Batch operations** - "Show all completed tasks", "Delete all done items"
5. **Natural language** - Don't worry about perfect phrasing!

---

## 🌟 Enjoy Your AI Todo Assistant!

Questions or feedback? We'd love to hear from you!

**Happy task managing!** 🚀

---

**User Guide Version:** 1.0.0
**Last Updated:** 2025-12-25
