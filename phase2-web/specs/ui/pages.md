# UI Pages Specification

> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

This document specifies the pages/routes for the multi-user todo web application built with Next.js App Router.

---

## Route Structure

```
/                     → Landing page (unauthenticated) or Dashboard (authenticated)
/signin               → Sign in page
/signup               → Sign up page
/forgot-password      → Password reset request
/reset-password       → Password reset form (with token)
/dashboard            → Main task list (protected)
/tasks/[id]           → Task detail view (protected)
/settings             → User settings (protected)
```

---

## Pages

### Landing Page (`/`)

Public landing page for unauthenticated users. Redirects to dashboard if authenticated.

**Route:** `app/page.tsx`

**Behavior:**
- Check authentication status
- If authenticated → redirect to `/dashboard`
- If not → show landing content

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ [Logo]                                    [Sign In] [Sign Up]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              Organize your life, one task at a time         │
│                                                             │
│     A simple, beautiful todo app to help you stay on top    │
│                    of your tasks.                           │
│                                                             │
│                   [Get Started Free]                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    [Feature Cards]                          │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐                  │
│   │ Simple  │   │ Secure  │   │  Fast   │                  │
│   └─────────┘   └─────────┘   └─────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Sign In Page (`/signin`)

User authentication page.

**Route:** `app/signin/page.tsx`

**Behavior:**
- If authenticated → redirect to `/dashboard`
- If `returnUrl` param → redirect there after sign in
- Show error for invalid credentials

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                        [Logo]                               │
│                                                             │
│                    Welcome back                             │
│              Sign in to your account                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Email                                                │   │
│  │ [                                                  ] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Password                                    [Show]   │   │
│  │ [                                                  ] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [✓] Remember me              Forgot password?              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Sign In                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│            Don't have an account? Sign up                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Error States:**
- Invalid credentials: "Invalid email or password"
- Account locked: "Account temporarily locked. Try again in 15 minutes."
- Server error: "Something went wrong. Please try again."

---

### Sign Up Page (`/signup`)

New user registration page.

**Route:** `app/signup/page.tsx`

**Behavior:**
- If authenticated → redirect to `/dashboard`
- Validate email format and uniqueness
- Validate password requirements
- Create account and sign in

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                        [Logo]                               │
│                                                             │
│                   Create an account                         │
│              Start organizing your tasks                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Name                                                 │   │
│  │ [                                                  ] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Email                                                │   │
│  │ [                                                  ] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Password                                    [Show]   │   │
│  │ [                                                  ] │   │
│  └─────────────────────────────────────────────────────┘   │
│  Password requirements:                                     │
│  ✓ At least 8 characters    ✗ One uppercase                │
│  ✗ One lowercase            ✗ One number                   │
│                                                             │
│  [✓] I agree to the Terms of Service                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Create Account                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│           Already have an account? Sign in                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Forgot Password Page (`/forgot-password`)

Password reset request page.

**Route:** `app/forgot-password/page.tsx`

**Behavior:**
- Accept email input
- Send reset email (always show success to prevent enumeration)
- Link back to sign in

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                        [Logo]                               │
│                                                             │
│                  Reset your password                        │
│    Enter your email and we'll send you a reset link         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Email                                                │   │
│  │ [                                                  ] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               Send Reset Link                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│               ← Back to sign in                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Success State:**
```
┌─────────────────────────────────────────────────────────────┐
│                        [✓]                                  │
│                                                             │
│                    Check your email                         │
│  If an account exists for {email}, you'll receive a         │
│             password reset link shortly.                    │
│                                                             │
│               ← Back to sign in                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Reset Password Page (`/reset-password`)

Password reset form (accessed via email link).

**Route:** `app/reset-password/page.tsx`

**Query Parameters:**
- `token`: Reset token from email

**Behavior:**
- Validate token is present and valid
- Accept new password
- Reset password and redirect to sign in

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                        [Logo]                               │
│                                                             │
│                 Create new password                         │
│            Enter your new password below                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ New Password                                [Show]   │   │
│  │ [                                                  ] │   │
│  └─────────────────────────────────────────────────────┘   │
│  Password requirements:                                     │
│  ✓ At least 8 characters    ✗ One uppercase                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Confirm Password                            [Show]   │   │
│  │ [                                                  ] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               Reset Password                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Error States:**
- Invalid token: "This reset link is invalid or has expired."
- Passwords don't match: "Passwords do not match"

---

### Dashboard Page (`/dashboard`)

Main task list view. Protected route.

**Route:** `app/dashboard/page.tsx`

**Behavior:**
- Require authentication
- Fetch and display user's tasks
- Support CRUD operations

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] Todo App                           [Avatar ▼] Sign Out│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  My Tasks                                    [+ New Task]   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ + Add a task...                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ☐ Complete project documentation            [⋮]     │   │
│  │   Created: Dec 10, 2025                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ☑ Review pull requests                      [⋮]     │   │
│  │   Created: Dec 9, 2025                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ☐ Schedule team meeting                     [⋮]     │   │
│  │   Created: Dec 8, 2025                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Empty State:**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    [illustration]                           │
│                                                             │
│                   No tasks yet                              │
│        Create your first task to get started                │
│                                                             │
│                   [+ Add Task]                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Loading State:**
```
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │   │
│  │ ░░░░░░░░░░░░                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │   │
│  │ ░░░░░░░░░░░░                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │   │
│  │ ░░░░░░░░░░░░                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Interactions:**
- Click checkbox → toggle task completion
- Click task title → open task detail
- Click menu (⋮) → show edit/delete options
- Click "+ Add a task" → focus quick add input
- Click "[+ New Task]" → open full task form modal

---

### Task Detail Page (`/tasks/[id]`)

Full task detail view. Protected route.

**Route:** `app/tasks/[id]/page.tsx`

**Behavior:**
- Require authentication
- Fetch task by ID
- Verify user owns task
- Support edit and delete

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] Todo App                           [Avatar ▼] Sign Out│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ← Back to tasks                                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │  Complete project documentation              [Edit]  │   │
│  │                                                      │   │
│  │  Status: ○ Incomplete                               │   │
│  │                                                      │   │
│  │  Description:                                        │   │
│  │  Write comprehensive API documentation and user      │   │
│  │  guide for the todo application. Include examples    │   │
│  │  for all endpoints.                                  │   │
│  │                                                      │   │
│  │  Created: December 10, 2025 at 10:30 AM             │   │
│  │  Updated: December 10, 2025 at 11:00 AM             │   │
│  │                                                      │   │
│  ├──────────────────────────────────────────────────────│   │
│  │                                                      │   │
│  │  [Delete Task]                                       │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Edit Mode:**
```
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                      │   │
│  │  Title                                               │   │
│  │  [Complete project documentation                   ] │   │
│  │                                                      │   │
│  │  Description                                         │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │ Write comprehensive API documentation and     │  │   │
│  │  │ user guide for the todo application...        │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  │                                                      │   │
│  │                        [Cancel]  [Save Changes]      │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**404 State:**
- Task not found or doesn't belong to user
- Show "Task not found" message with link back to dashboard

---

### Settings Page (`/settings`)

User account settings. Protected route.

**Route:** `app/settings/page.tsx`

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] Todo App                           [Avatar ▼] Sign Out│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Settings                                                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Profile                                              │   │
│  │                                                      │   │
│  │ Name                                                 │   │
│  │ [John Doe                                          ] │   │
│  │                                                      │   │
│  │ Email                                                │   │
│  │ john@example.com (cannot be changed)                 │   │
│  │                                                      │   │
│  │                              [Save Changes]          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Security                                             │   │
│  │                                                      │   │
│  │ Password                                             │   │
│  │ ••••••••                        [Change Password]    │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Danger Zone                                          │   │
│  │                                                      │   │
│  │ Delete Account                                       │   │
│  │ Permanently delete your account and all tasks        │   │
│  │                                [Delete Account]      │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Protected Route Middleware

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const protectedRoutes = ['/dashboard', '/tasks', '/settings']
const authRoutes = ['/signin', '/signup', '/forgot-password', '/reset-password']

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value
  const { pathname } = request.nextUrl

  // Protected routes require authentication
  if (protectedRoutes.some(route => pathname.startsWith(route))) {
    if (!token) {
      const signInUrl = new URL('/signin', request.url)
      signInUrl.searchParams.set('returnUrl', pathname)
      return NextResponse.redirect(signInUrl)
    }
  }

  // Auth routes redirect if already authenticated
  if (authRoutes.some(route => pathname.startsWith(route))) {
    if (token) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  }

  return NextResponse.next()
}
```

---

## SEO & Meta

### Page Titles
| Page | Title |
|------|-------|
| Landing | "Todo App - Organize Your Life" |
| Sign In | "Sign In - Todo App" |
| Sign Up | "Create Account - Todo App" |
| Dashboard | "My Tasks - Todo App" |
| Task Detail | "{Task Title} - Todo App" |
| Settings | "Settings - Todo App" |

### Meta Tags
```html
<meta name="description" content="A simple, beautiful todo app to help you stay on top of your tasks." />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta property="og:title" content="Todo App" />
<meta property="og:description" content="Organize your life, one task at a time." />
```

---

## Related Specifications

- `/specs/ui/components.md` - UI component specifications
- `/specs/features/task-crud.md` - Task CRUD feature specification
- `/specs/features/authentication.md` - Authentication feature specification
- `/specs/api/rest-endpoints.md` - API endpoints

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
