# UI Components Specification

> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

This document specifies the UI components for the multi-user todo web application. Components are built with Next.js, TypeScript, and Tailwind CSS.

---

## Design System

### Colors

```css
/* Primary */
--primary-50: #eff6ff;
--primary-500: #3b82f6;
--primary-600: #2563eb;
--primary-700: #1d4ed8;

/* Neutral */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-500: #6b7280;
--gray-700: #374151;
--gray-900: #111827;

/* Semantic */
--success: #10b981;
--error: #ef4444;
--warning: #f59e0b;
```

### Typography

```css
/* Font Family */
font-family: 'Inter', system-ui, sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
```

### Spacing

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
```

---

## Core Components

### Button

Primary interactive element for actions.

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  children: ReactNode;
  onClick?: () => void;
}
```

**Variants:**
| Variant | Background | Text | Use Case |
|---------|------------|------|----------|
| `primary` | blue-600 | white | Primary actions |
| `secondary` | gray-100 | gray-700 | Secondary actions |
| `ghost` | transparent | gray-700 | Tertiary actions |
| `danger` | red-600 | white | Destructive actions |

**States:**
- Default, Hover, Active, Focus, Disabled, Loading

**Accessibility:**
- Keyboard focusable (Tab)
- Enter/Space activates
- `aria-disabled` when disabled
- `aria-busy` when loading

---

### Input

Text input field for forms.

```typescript
interface InputProps {
  type: 'text' | 'email' | 'password';
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}
```

**States:**
- Default, Focus, Error, Disabled

**Accessibility:**
- Associated label via `id`
- `aria-invalid` when error
- `aria-describedby` for error message
- `aria-required` when required

---

### Checkbox

Toggle for boolean values.

```typescript
interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
}
```

**States:**
- Unchecked, Checked, Indeterminate, Disabled

**Accessibility:**
- `role="checkbox"`
- `aria-checked`
- Keyboard toggle (Space)
- Focus ring visible

---

### Toast

Notification feedback component.

```typescript
interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;  // ms, default 5000
  dismissible?: boolean;
}
```

**Behavior:**
- Auto-dismiss after duration
- Stack multiple toasts
- Swipe to dismiss on mobile
- `role="alert"` for screen readers

---

### Modal

Dialog overlay for focused interactions.

```typescript
interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  actions?: ReactNode;
}
```

**Behavior:**
- Focus trapped inside
- ESC key closes
- Click outside closes (optional)
- Body scroll locked

**Accessibility:**
- `role="dialog"`
- `aria-modal="true"`
- `aria-labelledby` for title
- Focus returns to trigger on close

---

### Skeleton

Loading placeholder component.

```typescript
interface SkeletonProps {
  variant: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
}
```

**Animation:**
- Pulse animation (opacity)
- Gray background

---

## Task Components

### TaskItem

Individual task display in list.

```typescript
interface TaskItemProps {
  task: {
    id: string;
    title: string;
    description?: string;
    completed: boolean;
    created_at: string;
  };
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}
```

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ ☐ Task title                          [⋮] menu │
│   Created: Dec 10, 2025                         │
└─────────────────────────────────────────────────┘
```

**States:**
- Default (incomplete)
- Completed (checkbox checked, strikethrough title)
- Hover (show action buttons)
- Editing (inline edit mode)

**Interactions:**
- Click checkbox → toggle complete
- Click title → view details
- Click menu → edit/delete options

---

### TaskList

Container for multiple tasks.

```typescript
interface TaskListProps {
  tasks: Task[];
  loading?: boolean;
  emptyMessage?: string;
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}
```

**States:**
- Loading (skeleton items)
- Empty (empty state message)
- Populated (task items)

**Features:**
- Virtualized list for performance (>100 items)
- Keyboard navigation (arrow keys)
- Drag to reorder (future)

---

### TaskForm

Form for creating/editing tasks.

```typescript
interface TaskFormProps {
  mode: 'create' | 'edit';
  initialData?: {
    title: string;
    description?: string;
  };
  onSubmit: (data: TaskFormData) => Promise<void>;
  onCancel?: () => void;
}
```

**Fields:**
- Title (required, max 255)
- Description (optional, max 2000)

**Validation:**
- Client-side validation on blur
- Submit button disabled until valid
- Error messages below fields

---

### QuickAddTask

Inline task creation input.

```typescript
interface QuickAddTaskProps {
  onAdd: (title: string) => Promise<void>;
  placeholder?: string;
}
```

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ + Add a task...                                 │
└─────────────────────────────────────────────────┘
```

**Behavior:**
- Click to focus input
- Enter to submit
- ESC to cancel
- Clear after successful add

---

### TaskDetail

Full task detail view (modal or page).

```typescript
interface TaskDetailProps {
  task: Task;
  onUpdate: (data: Partial<Task>) => Promise<void>;
  onDelete: () => Promise<void>;
  onClose: () => void;
}
```

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Task Title                              [Edit]  │
├─────────────────────────────────────────────────┤
│ Status: ○ Incomplete / ● Complete               │
│                                                 │
│ Description:                                    │
│ Task description text here...                   │
│                                                 │
│ Created: Dec 10, 2025 at 10:30 AM              │
│ Updated: Dec 10, 2025 at 11:00 AM              │
├─────────────────────────────────────────────────┤
│                           [Delete]    [Close]   │
└─────────────────────────────────────────────────┘
```

---

### DeleteConfirmation

Confirmation dialog for task deletion.

```typescript
interface DeleteConfirmationProps {
  taskTitle: string;
  onConfirm: () => void;
  onCancel: () => void;
}
```

**Content:**
```
Delete "{taskTitle}"?

This action cannot be undone.

[Cancel]  [Delete]
```

---

## Auth Components

### SignInForm

Email/password sign in form.

```typescript
interface SignInFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  onForgotPassword: () => void;
  loading?: boolean;
  error?: string;
}
```

**Fields:**
- Email input
- Password input (with show/hide toggle)
- Remember me checkbox
- Submit button
- Forgot password link

---

### SignUpForm

New user registration form.

```typescript
interface SignUpFormProps {
  onSubmit: (data: SignUpData) => Promise<void>;
  loading?: boolean;
  error?: string;
}
```

**Fields:**
- Name input
- Email input
- Password input (with requirements indicator)
- Confirm password input
- Terms checkbox
- Submit button

---

### PasswordRequirements

Password strength indicator.

```typescript
interface PasswordRequirementsProps {
  password: string;
}
```

**Requirements Display:**
```
Password requirements:
✓ At least 8 characters
✓ One uppercase letter
✗ One lowercase letter
✗ One number
```

---

## Layout Components

### Header

Top navigation bar.

```typescript
interface HeaderProps {
  user?: {
    name: string;
    email: string;
    image?: string;
  };
  onSignOut: () => void;
}
```

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ [Logo] Todo App              [Avatar ▼] Sign Out│
└─────────────────────────────────────────────────┘
```

---

### EmptyState

Placeholder for empty content.

```typescript
interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

**Layout:**
```
┌─────────────────────────────────────────────────┐
│                                                 │
│              [illustration]                     │
│                                                 │
│            No tasks yet                         │
│    Create your first task to get started        │
│                                                 │
│              [+ Add Task]                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| `sm` | 640px | Mobile |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop |
| `xl` | 1280px | Large Desktop |

---

## Accessibility Requirements

### WCAG 2.1 AA Compliance

- [ ] Color contrast ratio ≥ 4.5:1 for text
- [ ] Color contrast ratio ≥ 3:1 for UI components
- [ ] Focus indicators visible on all interactive elements
- [ ] All functionality accessible via keyboard
- [ ] Form inputs have associated labels
- [ ] Error messages are descriptive and associated with inputs
- [ ] Loading states announced to screen readers
- [ ] Skip links for main content

### Keyboard Navigation

| Component | Keys |
|-----------|------|
| All | Tab (focus), Shift+Tab (reverse) |
| Button | Enter/Space (activate) |
| Checkbox | Space (toggle) |
| Modal | ESC (close) |
| Menu | Arrow keys (navigate), Enter (select) |
| List | Arrow keys (navigate items) |

---

## Related Specifications

- `/specs/features/task-crud.md` - Task CRUD feature specification
- `/specs/features/authentication.md` - Authentication feature specification
- `/specs/api/rest-endpoints.md` - API endpoints

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
