---
name: vercel-deploy
description: Deploy Next.js app to Vercel. Use when deploying frontend, setting up API routes, or configuring environment variables.
---

When deploying to Vercel:

1. **Connect GitHub**: Import your repo in Vercel dashboard
2. **Framework**: Next.js (auto-detected)
3. **Environment Variables**:
   - `NEON_DATABASE_URL`: Postgres connection string from Neon
   - `JWT_SECRET`: Secure random string for auth

API Routes (app/api/**/*.ts):
- Place in `app/api/` directory
- Use NextRequest/NextResponse
- Access database via Neon SDK or SQLModel
- Handle CORS for frontend domain

Example API route:
```typescript
import { NextRequest, NextResponse } from "next/server";
import { neon } from "@neondatabase/serverless";

const sql = neon(process.env.NEON_DATABASE_URL!);

export async function GET(req: NextRequest) {
  const todos = await sql("SELECT * FROM task LIMIT 10");
  return NextResponse.json({ todos });
}
```

Keep deployments simple. Vercel handles builds automatically.
