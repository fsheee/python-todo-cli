# Vercel Serverless Crash Resolution

> **Issue ID:** VERCEL-500-001
> **Status:** Active
> **Last Updated:** 2025-12-14

---

## Error Summary

```
This Serverless Function has crashed.

Your connection is working correctly.
Vercel is working correctly.

500: INTERNAL_SERVER_ERROR
Code: FUNCTION_INVOCATION_FAILED
ID: dxb1::dhjd4-1765667903283-987995ded13b
```

---

## Root Cause

Vercel's Python serverless runtime (`@vercel/python`) has **incompatibility with binary Python packages** that require C compilation:

| Package | Issue |
|---------|-------|
| `pydantic>=2.0` | Requires `pydantic_core` (Rust binary) |
| `bcrypt` | Requires C extension compilation |
| `psycopg2-binary` | Requires libpq C library |

The error trace shows:
```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
```

This occurs because:
1. Vercel's serverless environment runs on AWS Lambda
2. Lambda uses Amazon Linux with limited binary compatibility
3. Binary wheels compiled on other platforms don't work
4. Vercel's Python builder doesn't compile from source

---

## Attempted Solutions (Failed)

| Attempt | Result |
|---------|--------|
| Pin FastAPI 0.103.2 + Pydantic 1.10.13 | Vercel still installs pydantic v2 |
| Remove `uv.lock` | Vercel recreates it |
| Use `requirements.txt` only | Vercel ignores, uses `pyproject.toml` |
| Replace psycopg2 with pg8000 | Worked, but pydantic issue remains |

---

## Solution Options

### Option 1: Use Flask Instead of FastAPI (Recommended for Vercel)

Flask doesn't depend on Pydantic and works on Vercel serverless.

**Migration Steps:**
1. Replace FastAPI with Flask
2. Replace Pydantic models with dataclasses or marshmallow
3. Update route decorators
4. Keep pg8000 for database

**Pros:** Works on Vercel, simple migration
**Cons:** Loses OpenAPI docs, type validation

### Option 2: Use Alternative Hosting

Deploy backend to a platform with full Python support:

| Platform | Binary Support | Free Tier |
|----------|---------------|-----------|
| Railway | Yes | $5/month credit |
| Fly.io | Yes | Limited free |
| DigitalOcean App Platform | Yes | $5/month |
| AWS EC2/ECS | Yes | 12 months free |
| Google Cloud Run | Yes | Free tier |

### Option 3: Docker Deployment on Vercel (Experimental)

Use Vercel's Docker support (requires Pro plan):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Recommended Solution: Flask Migration

### Step 1: Create Flask Backend

```python
# main_flask.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
import os

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",
    "https://python-todo-cli-d9n6.vercel.app"
])

# ... routes implementation
```

### Step 2: Update Vercel Entry Point

```python
# api/index.py
from main_flask import app
```

### Step 3: Update requirements.txt

```
flask==3.0.0
flask-cors==4.0.0
pyjwt==2.8.0
bcrypt==4.0.1
python-dotenv==1.0.0
pg8000==1.30.3
```

### Step 4: Update vercel.json

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

---

## Alternative: Keep FastAPI, Change Host

If Flask migration is not desired, deploy FastAPI to:

1. **Railway.app** - Best free option
   ```bash
   railway login
   railway init
   railway up
   ```

2. **Fly.io**
   ```bash
   fly launch
   fly deploy
   ```

---

## Environment Variables Required

Regardless of solution, backend needs:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | JWT signing secret (32+ chars) |

---

## Verification Steps

After deployment:

1. Test health endpoint:
   ```bash
   curl https://your-backend-url/health
   ```

2. Test auth endpoint:
   ```bash
   curl -X POST https://your-backend-url/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123"}'
   ```

3. Update frontend `NEXT_PUBLIC_API_URL` environment variable

4. Redeploy frontend on Vercel

---

## Related Files

- `backend/main.py` - Current FastAPI entry point
- `backend/vercel.json` - Vercel configuration
- `backend/requirements.txt` - Python dependencies
- `backend/api/index.py` - Vercel serverless entry point

---

## Decision Required

Choose one:
- [ ] **Option 1:** Migrate to Flask (works on Vercel)
- [ ] **Option 2:** Deploy FastAPI to Railway/Fly.io
- [ ] **Option 3:** Keep trying Vercel with different approach
