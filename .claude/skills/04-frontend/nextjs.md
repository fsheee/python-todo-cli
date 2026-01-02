---
name: nextjs-frontend
description: Build Next.js frontend with API client and auth. Use when creating frontend pages and components.
---

When building Next.js frontend:

1. **API Client** (lib/api.ts):
   ```typescript
   const API_URL = process.env.NEXT_PUBLIC_API_URL;

   async function fetchTasks() {
     const res = await fetch(`${API_URL}/todos`, {
       headers: { Authorization: `Bearer ${token}` }
     });
     return res.json();
   }
   ```

2. **Auth Provider** (components/AuthProvider.tsx):
   - Wrap app with AuthProvider
   - Provide signin/signup/logout methods
   - Manage token in localStorage

3. **Pages**:
   - /app/page.tsx → Dashboard
   - /app/login/page.tsx → Sign in
   - /app/signup/page.tsx → Sign up

4. **API Routes** (app/api/todos/route.ts):
   - Use NextRequest/NextResponse
   - Access DB via Neon SDK
   - Verify JWT before operations
