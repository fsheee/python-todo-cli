# Frontend Deployment: Vercel

This guide covers deploying the Next.js frontend to Vercel.

---

## Project Setup

### Option 1: Import from Git Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Select your Git provider (GitHub/GitLab/Bitbucket)
4. Import the repository: `hackathon-todo`
5. Set the **Root Directory** to `phase2-web/frontend`
6. Vercel auto-detects Next.js and configures build settings

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd phase2-web/frontend

# Deploy (follow prompts)
vercel

# Deploy to production
vercel --prod
```

---

## Environment Variables

Configure these in **Project Settings → Environment Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `https://api.yourdomain.com` |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Better Auth endpoint | `https://auth.yourdomain.com` |
| `BETTER_AUTH_SECRET` | JWT signing secret (server-side only) | `your-secret-key` |

### Setting Environment Variables

**Via Dashboard:**
1. Go to Project → Settings → Environment Variables
2. Add each variable with appropriate scope:
   - **Production**: Only production deployments
   - **Preview**: Branch/PR preview deployments
   - **Development**: Local development via `vercel dev`

**Via CLI:**
```bash
vercel env add NEXT_PUBLIC_API_URL
# Follow prompts to set value and scope
```

**Via `vercel.json`** (non-sensitive values only):
```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.yourdomain.com"
  }
}
```

---

## Build Settings

Vercel auto-detects Next.js. Default settings:

| Setting | Value |
|---------|-------|
| Framework Preset | Next.js |
| Build Command | `next build` (or `npm run build`) |
| Output Directory | `.next` |
| Install Command | `npm install` |
| Node.js Version | 18.x (configurable) |

### Custom Build Settings

Override in **Project Settings → General → Build & Development Settings** or via `vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "framework": "nextjs",
  "nodeVersion": "20.x"
}
```

### Monorepo Configuration

Since frontend is in `phase2-web/frontend`, set:

```json
{
  "rootDirectory": "phase2-web/frontend"
}
```

Or configure via Dashboard: **Project Settings → General → Root Directory**

---

## Rendering Strategies

Next.js on Vercel supports multiple rendering modes. Choose based on your page requirements.

### Rendering Modes Overview

| Mode | When Rendered | Best For | Vercel Behavior |
|------|---------------|----------|-----------------|
| **SSG** (Static) | Build time | Marketing pages, docs | Served from Edge CDN |
| **ISR** (Incremental) | Build + revalidate | Product listings, blogs | Edge CDN + background regeneration |
| **SSR** (Server) | Each request | Auth pages, real-time data | Serverless Functions |
| **CSR** (Client) | Browser | Dashboards, interactive UI | Static shell + client fetch |

### Static Site Generation (SSG)

Pre-rendered at build time. Fastest performance.

```tsx
// app/about/page.tsx
export default function AboutPage() {
  return <div>Static content - rendered at build time</div>;
}
```

**With data fetching:**
```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

export default async function BlogPost({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug);
  return <article>{post.content}</article>;
}
```

### Incremental Static Regeneration (ISR)

Static pages that revalidate periodically.

```tsx
// app/products/page.tsx
export const revalidate = 60; // Regenerate every 60 seconds

export default async function ProductsPage() {
  const products = await fetch('https://api.example.com/products');
  return <ProductList products={products} />;
}
```

**On-demand revalidation:**
```tsx
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache';

export async function POST(request: Request) {
  const { path, tag } = await request.json();

  if (path) revalidatePath(path);
  if (tag) revalidateTag(tag);

  return Response.json({ revalidated: true });
}
```

### Server-Side Rendering (SSR)

Rendered on each request. Use for dynamic, personalized content.

```tsx
// app/dashboard/page.tsx
export const dynamic = 'force-dynamic'; // Opt out of static rendering

export default async function DashboardPage() {
  const user = await getCurrentUser();
  const tasks = await getUserTasks(user.id);

  return <Dashboard user={user} tasks={tasks} />;
}
```

**Alternative - no-store fetch:**
```tsx
// app/profile/page.tsx
export default async function ProfilePage() {
  // no-store disables caching, forcing SSR
  const user = await fetch('https://api.example.com/me', {
    cache: 'no-store',
    headers: { Authorization: `Bearer ${token}` }
  });

  return <Profile user={user} />;
}
```

### Client-Side Rendering (CSR)

Rendered in the browser. Use for highly interactive components.

```tsx
'use client';

import { useEffect, useState } from 'react';

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/tasks')
      .then((res) => res.json())
      .then((data) => {
        setTasks(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <Skeleton />;
  return <TaskList tasks={tasks} />;
}
```

### Hybrid Approach (Recommended for Todo App)

Combine strategies for optimal performance:

```
app/
├── page.tsx              # SSG - Landing page
├── login/page.tsx        # SSG - Static login form
├── dashboard/
│   ├── page.tsx          # SSR - User-specific data
│   └── layout.tsx        # Shared authenticated layout
├── tasks/
│   ├── page.tsx          # CSR - Real-time task list
│   └── [id]/page.tsx     # SSR - Individual task
└── api/
    └── tasks/route.ts    # API routes (serverless)
```

### Rendering Decision Guide

```
Is the content the same for all users?
├── Yes → Is it updated frequently?
│         ├── Yes → ISR (revalidate: 60-3600)
│         └── No  → SSG (static)
└── No  → Does it need SEO?
          ├── Yes → SSR (force-dynamic)
          └── No  → CSR ('use client')
```

### Vercel-Specific Optimizations

**Edge Runtime** (faster cold starts):
```tsx
// app/api/hello/route.ts
export const runtime = 'edge';

export async function GET() {
  return Response.json({ message: 'Hello from Edge!' });
}
```

**Streaming SSR:**
```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<TasksSkeleton />}>
        <TaskList /> {/* Streams in when ready */}
      </Suspense>
    </div>
  );
}
```

**Partial Prerendering (PPR)** - Next.js 14+:
```tsx
// next.config.ts
const nextConfig = {
  experimental: {
    ppr: true,
  },
};

// app/dashboard/page.tsx
import { Suspense } from 'react';

export default function Dashboard() {
  return (
    <div>
      <StaticHeader /> {/* Pre-rendered shell */}
      <Suspense fallback={<Loading />}>
        <DynamicContent /> {/* Streamed dynamically */}
      </Suspense>
    </div>
  );
}
```

---

## Domain & Preview URLs

### Production Domain

1. Go to **Project → Settings → Domains**
2. Add your custom domain (e.g., `app.yourdomain.com`)
3. Configure DNS:
   - **A Record**: `76.76.21.21`
   - **CNAME**: `cname.vercel-dns.com`
4. Vercel automatically provisions SSL certificate

### Preview Deployments

Every push to a non-production branch creates a preview URL:
- Format: `<project>-<unique-id>-<team>.vercel.app`
- PR comments include preview link automatically

### URL Patterns

| Environment | URL Pattern |
|-------------|-------------|
| Production | `yourdomain.com` or `<project>.vercel.app` |
| Preview | `<project>-git-<branch>-<team>.vercel.app` |
| Deployment | `<project>-<hash>-<team>.vercel.app` |

---

## Common Errors + Fixes

### Build Errors

#### `Module not found: Can't resolve '@/...'`

**Cause:** Path alias misconfiguration

**Fix:** Ensure `tsconfig.json` has correct paths:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

#### `Error: ENOENT: no such file or directory`

**Cause:** Root directory not set correctly for monorepo

**Fix:** Set Root Directory to `phase2-web/frontend` in project settings

#### `Type error: Cannot find module 'X' or its type declarations`

**Cause:** Missing dependencies or type packages

**Fix:**
```bash
npm install
npm install -D @types/missing-package
```

---

### Runtime Errors

#### `Error: NEXT_PUBLIC_* is undefined`

**Cause:** Environment variable not set or not prefixed correctly

**Fix:**
1. Ensure variable is set in Vercel dashboard
2. Client-side variables MUST use `NEXT_PUBLIC_` prefix
3. Redeploy after adding env vars (changes don't apply to existing deployments)

#### `504 Gateway Timeout`

**Cause:** API routes or SSR taking too long

**Fix:**
- Vercel Serverless Functions have 10s default timeout (Hobby) / 60s (Pro)
- Optimize database queries
- Add caching with `unstable_cache` or ISR
- Upgrade plan for longer timeouts

#### `CORS errors when calling backend API`

**Cause:** Backend not configured for frontend domain

**Fix:** Configure CORS on backend (FastAPI):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Authentication Errors

#### `JWT token invalid` or `401 Unauthorized`

**Cause:** `BETTER_AUTH_SECRET` mismatch between frontend and backend

**Fix:**
1. Ensure same secret is set in both Vercel (frontend) and backend deployment
2. Secret should NOT have `NEXT_PUBLIC_` prefix (server-side only)
3. Verify secret has no trailing whitespace

#### `Cookies not being set`

**Cause:** SameSite/Secure cookie issues across domains

**Fix:**
1. Use same root domain for frontend and API (e.g., `app.domain.com` and `api.domain.com`)
2. Or configure cookies with `SameSite=None; Secure`

---

### Deployment Errors

#### `Build exceeded maximum duration`

**Cause:** Build taking longer than plan allows (45min Hobby / 45min Pro)

**Fix:**
- Add build cache: Vercel caches `node_modules` and `.next/cache` by default
- Reduce bundle size: analyze with `@next/bundle-analyzer`
- Split large pages into smaller components

#### `Error: Cannot find module 'sharp'`

**Cause:** Native dependency issue with Next.js Image Optimization

**Fix:** Add to `next.config.ts`:
```typescript
const nextConfig: NextConfig = {
  images: {
    unoptimized: true, // Or configure external loader
  },
};
```

---

## Deployment Checklist

- [ ] Root directory set to `phase2-web/frontend`
- [ ] All required environment variables configured
- [ ] `NEXT_PUBLIC_API_URL` points to deployed backend
- [ ] `BETTER_AUTH_SECRET` matches backend configuration
- [ ] Custom domain configured (optional)
- [ ] CORS configured on backend for Vercel domain
- [ ] Build completes successfully
- [ ] Preview deployment tested before production

---

## Useful Commands

```bash
# Check deployment status
vercel ls

# View deployment logs
vercel logs <deployment-url>

# Pull environment variables locally
vercel env pull .env.local

# Promote preview to production
vercel promote <deployment-url>

# Rollback to previous deployment
vercel rollback
```

---

## References

- [Vercel Next.js Documentation](https://vercel.com/docs/frameworks/nextjs)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)
