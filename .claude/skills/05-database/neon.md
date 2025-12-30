---
name: neon-postgres
description: Use Neon PostgreSQL database. Use when setting up database connection, creating tables, or running queries.
---

When using Neon PostgreSQL:

1. **Connection String**: Get from Neon dashboard
   - Format: `postgres://user:pass@ep-xxx.region.neon.tech/dbname?sslmode=require`

2. **Environment Variable**:
   ```
   NEON_DATABASE_URL=postgres://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
   ```

3. **In Next.js API Routes**:
   ```typescript
   import { neon } from "@neondatabase/serverless";
   const sql = neon(process.env.NEON_DATABASE_URL!);

   const result = await sql("SELECT * FROM task WHERE user_id = $1", [userId]);
   ```

4. **Tables** (SQL):
   ```sql
   CREATE TABLE public.user (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     email VARCHAR(255) UNIQUE NOT NULL,
     name VARCHAR(255) NOT NULL,
     password_hash VARCHAR(255) NOT NULL,
     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );

   CREATE TABLE public.task (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id UUID REFERENCES public.user(id) ON DELETE CASCADE,
     title VARCHAR(255) NOT NULL,
     description VARCHAR(2000),
     status VARCHAR(20) DEFAULT 'pending',
     priority VARCHAR(20) DEFAULT 'medium',
     due_date TIMESTAMPTZ,
     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
   );
   ```

5. **Index for Performance**:
   ```sql
   CREATE INDEX idx_task_user_id ON public.task(user_id);
   CREATE INDEX idx_task_status ON public.task(status);
   ```

Neon automatically scales. Enable sslmode=require for security.
