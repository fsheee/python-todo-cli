# Todo Chatbot Frontend - Next.js

Lightweight Next.js frontend with OpenAI ChatKit for AI-powered todo management.

## Features

- Next.js 14 App Router
- TypeScript for type safety
- OpenAI ChatKit integration
- Zustand for auth state
- Better Auth (Phase 2) integration
- Session persistence with localStorage
- Responsive design

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Build

```bash
# Production build
npm run build

# Start production server
npm start
```

## Environment

Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Architecture

```
Next.js Frontend
    ↓ POST /chat (JWT in header)
FastAPI Backend
    ↓ Calls agent
AI Agent (OpenAI)
    ↓ Calls MCP tools
MCP Server (5 tools)
    ↓ Wraps Phase 2
Phase 2 Backend
    ↓
Database
```

## Spec Reference

See `specs/ui/chatkit-integration.md` for complete specifications.

**Updated:** Next.js instead of Vite for simplified deployment and better ChatKit integration.
