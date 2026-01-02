# Todo App Frontend

Next.js frontend for the multi-user Todo web application.

## Tech Stack

- **Next.js 16+** - React framework (App Router)
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Context** - State management

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd phase2-web/frontend

# Install dependencies
npm install
```

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/             # Auth pages (signin, signup, etc.)
│   │   ├── (protected)/        # Protected pages (dashboard, tasks)
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Landing page
│   │   └── providers.tsx       # Context providers
│   ├── components/
│   │   ├── auth/               # Auth components
│   │   │   ├── SignInForm.tsx
│   │   │   ├── SignUpForm.tsx
│   │   │   └── PasswordRequirements.tsx
│   │   ├── tasks/              # Task components
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── QuickAddTask.tsx
│   │   │   └── DeleteConfirmation.tsx
│   │   ├── ui/                 # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Checkbox.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── Skeleton.tsx
│   │   └── layout/             # Layout components
│   │       ├── Header.tsx
│   │       └── EmptyState.tsx
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   ├── auth.ts             # Auth utilities
│   │   ├── auth-context.tsx    # Auth context provider
│   │   ├── toast-context.tsx   # Toast context provider
│   │   └── utils.ts            # Utility functions
│   └── types/
│       └── index.ts            # TypeScript types
├── middleware.ts               # Route protection middleware
├── .env.local                  # Environment variables
├── tailwind.config.ts          # Tailwind configuration
└── tsconfig.json               # TypeScript configuration
```

## Pages

| Route | Description | Auth Required |
|-------|-------------|---------------|
| `/` | Landing page | No |
| `/signin` | Sign in page | No |
| `/signup` | Sign up page | No |
| `/forgot-password` | Password reset request | No |
| `/reset-password` | Password reset form | No |
| `/dashboard` | Task list | Yes |
| `/tasks/[id]` | Task detail/edit | Yes |
| `/settings` | User settings | Yes |

## Features

### Authentication
- Email/password registration
- Sign in with credentials
- JWT token stored in localStorage
- Protected routes via middleware

### Task Management
- View all tasks on dashboard
- Quick add task with title only
- Create task with title and description
- Edit task details
- Delete task with confirmation
- Toggle task completion

## Components

### UI Components
- **Button** - Primary, secondary, ghost, danger variants
- **Input** - Text, email, password with validation
- **Checkbox** - With optional label
- **Modal** - Dialog overlay
- **Toast** - Success, error, warning notifications
- **Skeleton** - Loading placeholders

### Auth Components
- **SignInForm** - Email/password login
- **SignUpForm** - Registration with validation
- **PasswordRequirements** - Password strength indicator

### Task Components
- **TaskItem** - Single task display
- **TaskList** - Task collection with loading/empty states
- **TaskForm** - Create/edit task form
- **QuickAddTask** - Inline task creation
- **DeleteConfirmation** - Deletion confirmation modal

## API Client

All API calls go through `src/lib/api.ts`:

```typescript
import { api } from '@/lib/api';

// Auth
await api.register({ email, password, name });
await api.login({ email, password });
await api.logout();
await api.getSession();

// Tasks
await api.getTasks(userId);
await api.getTask(userId, taskId);
await api.createTask(userId, { title, description });
await api.updateTask(userId, taskId, { title, description });
await api.deleteTask(userId, taskId);
await api.toggleComplete(userId, taskId);
```

## Scripts

```bash
# Development
npm run dev

# Build
npm run build

# Start production
npm start

# Lint
npm run lint
```

## Related Documentation

- [UI Components Spec](../specs/ui/components.md)
- [UI Pages Spec](../specs/ui/pages.md)
- [Authentication Spec](../specs/features/authentication.md)
- [Task CRUD Spec](../specs/features/task-crud.md)
