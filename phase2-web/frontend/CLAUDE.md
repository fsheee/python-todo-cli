# Frontend Guidelines - Todo Full-Stack Web App

## Purpose
This file defines frontend patterns, stack, and conventions for the Todo web application (Phase II).

## Tech Stack
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- React Server & Client Components
- API calls via `/lib/api.ts`
- **Authentication:** Better Auth (JWT tokens)

## Folder Structure
- `/app` - Pages and layouts
- `/components` - Reusable UI components
- `/styles` - Tailwind/global styles
- `/lib` - API clients and utilities

## Patterns & Conventions
- Use **server components** by default
- Use **client components** only for interactive features
- Keep components **small and atomic**
- Use Tailwind classes for styling, avoid inline CSS
- Follow naming conventions: PascalCase for components, camelCase for props and functions

## Authentication & API Integration
- Integrate Better Auth for user signup/signin
- Use JWT token issued by Better Auth for backend API calls
```ts
import { api } from '@/lib/api'

const token = await getJwtToken()  // from Better Auth session
const tasks = await api.getTasks(userId, token)

# API Authentication
- All API calls must include the JWT token in the header:

``Authorization: Bearer <token>``


## UI Guidelines
- Task list displays:
  - Title
  - Description
  - Completion status
- Use buttons for CRUD operations:
  - Add
  - Edit
  - Delete
  - Complete
- Use modals or forms for creating/editing tasks
- Responsive design for mobile and desktop

## Frontend Testing
- Unit test components with Jest / React Testing Library
- Test API client functions with mock data

## Claude Code Instructions
- Always refer to specs in `/specs/features/` before creating a component
- Implement one atomic component/feature at a time
- Use Tailwind utility classes consistently
- Do not write business logic in components; call API client
- Follow Better Auth flow for JWT token management
